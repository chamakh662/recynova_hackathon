import json

from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Scan, ScanMaterial, ScanProject
from .ai_service import detect_material_from_image, detect_materials_from_image
from materials.models import Material
from projects.models import Project


def project_to_dict(project):
    return {
        "id": project.id,
        "titre": project.titre,
        "description": project.description,
        "cout_estime": project.cout_estime,
        "duree_minutes": project.duree_minutes,
        "difficulte": project.difficulte,
        "etapes": project.etapes,
        "image": project.image.url if project.image else None
    }


def parse_manual_materials(raw):
    """
    Parse les matériaux manuels envoyés sous forme de JSON,
    de liste d'objets, ou de chaîne séparée par des virgules.
    """
    if not raw:
        return []
    if isinstance(raw, str):
        raw = raw.strip()
        try:
            raw = json.loads(raw)
        except Exception:
            raw = [s.strip() for s in raw.split(',') if s.strip()]

    materials_list = []
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, str) and item.strip():
                materials_list.append({"nom": item.strip(), "quantite": 1})
            elif isinstance(item, dict):
                nom = item.get("nom") or item.get("name")
                mat_id = item.get("material_id") or item.get("id")
                quantite = item.get("quantite", 1)
                try:
                    quantite = max(1, int(quantite))
                except (ValueError, TypeError):
                    quantite = 1
                if nom:
                    materials_list.append({"nom": nom.strip(), "quantite": quantite})
                elif mat_id:
                    try:
                        m = Material.objects.get(id=mat_id)
                        materials_list.append({"nom": m.nom, "quantite": quantite})
                    except Material.DoesNotExist:
                        pass
    return materials_list


class ScanListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    # 1. Consulter l'historique des scans
    def get(self, request):

        scans = Scan.objects.filter(
            user=request.user
        ).order_by('-created_at')

        data = []

        for scan in scans:

            materials = []

            for item in ScanMaterial.objects.filter(
                scan=scan
            ).select_related('material'):

                materials.append({
                    "id": item.material.id,
                    "nom": item.material.nom,
                    "quantite": item.quantite,
                    "poids_moyen_kg": item.material.poids_moyen_kg
                })

            recommendations = []

            for item in ScanProject.objects.filter(
                scan=scan
            ).select_related('project').order_by('rang'):

                recommendations.append({
                    "rang": item.rang,
                    "project": project_to_dict(item.project)
                })

            data.append({
                "id": scan.id,
                "image": scan.image.url if scan.image else None,
                "budget": scan.budget,
                "temps_dispo": scan.temps_dispo,
                "difficulte": scan.difficulte,
                "ai_raw_response": scan.ai_raw_response,
                "created_at": scan.created_at,
                "materiaux": materials,
                "recommendations": recommendations
            })

        return Response(data, status=status.HTTP_200_OK)

    # 2. Créer un nouveau scan
    @transaction.atomic
    def post(self, request):

        budget = request.data.get('budget', 0)
        temps_dispo = request.data.get('temps_dispo')
        difficulte = request.data.get('difficulte')

        # Vérification des champs obligatoires
        if temps_dispo is None or not difficulte:

            return Response(
                {
                    "error": "Le temps disponible et la difficulté sont obligatoires."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérification des valeurs numériques
        try:
            budget = int(budget)
            temps_dispo = int(temps_dispo)

            if budget < 0 or temps_dispo <= 0:
                raise ValueError()

        except (ValueError, TypeError):

            return Response(
                {"error": "Budget ou temps disponible invalide."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérification de la difficulté
        if difficulte not in ['facile', 'moyen', 'difficile']:

            return Response(
                {"error": "La difficulté doit être facile, moyen ou difficile."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Traitement des matériaux saisis manuellement
        validated_materials = []
        raw_materiaux = request.data.get('materiaux') or request.data.get('materiaux_manuels')
        manual_items = parse_manual_materials(raw_materiaux)

        for item in manual_items:
            mat_obj, _ = Material.objects.get_or_create(
                nom=item["nom"],
                defaults={"poids_moyen_kg": 0.05}
            )
            existing = next((m for m in validated_materials if m[0].id == mat_obj.id), None)
            if existing:
                idx = validated_materials.index(existing)
                validated_materials[idx] = (existing[0], existing[1] + item["quantite"])
            else:
                validated_materials.append((mat_obj, item["quantite"]))

        # 2. Récupération de l'ensemble des images (multiples ou unique)
        images = request.FILES.getlist('images')
        if not images:
            images = request.FILES.getlist('image')
        if not images and request.FILES.get('image'):
            images = [request.FILES.get('image')]

        # Vérification qu'au moins une image ou un matériau manuel est fourni
        if not images and not validated_materials:
            return Response(
                {"error": "Veuillez fournir au moins une photo ou renseigner un matériau."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Analyse de chaque image avec l'IA
        all_ai_results = []
        for img in images:
            detected_items = detect_materials_from_image(img)
            all_ai_results.extend(detected_items)
            for d in detected_items:
                mat_name = d["nom"]
                mat_obj, _ = Material.objects.get_or_create(
                    nom=mat_name,
                    defaults={"poids_moyen_kg": d.get("poids_moyen_kg", 0.05)}
                )
                qty = d.get("quantite", 1)
                existing = next((m for m in validated_materials if m[0].id == mat_obj.id), None)
                if existing:
                    idx = validated_materials.index(existing)
                    validated_materials[idx] = (existing[0], existing[1] + qty)
                else:
                    validated_materials.append((mat_obj, qty))

        # 4. Création du scan
        scan = Scan.objects.create(
            user=request.user,
            image=images[0] if images else None,
            budget=budget,
            temps_dispo=temps_dispo,
            difficulte=difficulte,
            ai_raw_response={
                "images_count": len(images),
                "ai_detections": all_ai_results,
                "manual_materials": manual_items
            }
        )

        # Enregistrement des matériaux associés
        for material, quantite in validated_materials:
            ScanMaterial.objects.create(
                scan=scan,
                material=material,
                quantite=quantite
            )

        # Recherche des projets compatibles avec priorité sur les matériaux détectés
        material_ids = [m[0].id for m in validated_materials]
        selected_projects = []

        if material_ids:
            # 1. Projets correspondant aux matériaux ET aux contraintes
            compat = Project.objects.filter(
                materiaux__id__in=material_ids,
                cout_estime__lte=budget,
                duree_minutes__lte=temps_dispo,
                difficulte=difficulte
            ).distinct().order_by('cout_estime', 'duree_minutes')
            selected_projects.extend(list(compat[:3]))

            # 2. Si moins de 3, projets utilisant le matériau même avec budget/durée différents
            if len(selected_projects) < 3:
                existing_ids = [p.id for p in selected_projects]
                more_mat = Project.objects.filter(
                    materiaux__id__in=material_ids
                ).exclude(id__in=existing_ids).distinct().order_by('cout_estime', 'duree_minutes')
                for p in more_mat:
                    if len(selected_projects) >= 3:
                        break
                    selected_projects.append(p)

        # 3. Si toujours moins de 3, compléter avec des projets généraux dans le budget/temps
        if len(selected_projects) < 3:
            existing_ids = [p.id for p in selected_projects]
            general = Project.objects.filter(
                cout_estime__lte=budget,
                duree_minutes__lte=temps_dispo
            ).exclude(id__in=existing_ids).order_by('cout_estime', 'duree_minutes')
            for p in general:
                if len(selected_projects) >= 3:
                    break
                selected_projects.append(p)

        # 4. Dernier recours : projets existants dans le catalogue
        if len(selected_projects) < 3:
            existing_ids = [p.id for p in selected_projects]
            fallback_any = Project.objects.exclude(id__in=existing_ids).order_by('id')
            for p in fallback_any:
                if len(selected_projects) >= 3:
                    break
                selected_projects.append(p)

        # Enregistrement des recommandations
        recommendations = []
        projects_dict_list = []

        for rang, project in enumerate(selected_projects, start=1):
            ScanProject.objects.create(
                scan=scan,
                project=project,
                rang=rang
            )
            p_dict = project_to_dict(project)
            projects_dict_list.append(p_dict)
            recommendations.append({
                "rang": rang,
                "project": p_dict
            })

        return Response(
            {
                "message": "Scan enregistré avec succès.",
                "scan_id": scan.id,
                "ai_detected": all_ai_results[0] if all_ai_results else None,
                "ai_detections": all_ai_results,
                "materiaux": [
                    {
                        "id": material.id,
                        "nom": material.nom,
                        "quantite": quantite,
                        "poids_moyen_kg": material.poids_moyen_kg
                    }
                    for material, quantite in validated_materials
                ],
                "recommendations": recommendations,
                "projects": projects_dict_list
            },
            status=status.HTTP_201_CREATED
        )