import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet.settings')
django.setup()

from materials.models import Material
from projects.models import Project

def seed():
    print("Initialisation des matériaux et projets RecyNova...")

    # 1. Matériaux
    materials_data = [
        {"nom": "Plastique", "poids_moyen_kg": 0.05},
        {"nom": "Carton", "poids_moyen_kg": 0.15},
        {"nom": "Verre", "poids_moyen_kg": 0.35},
        {"nom": "Métal", "poids_moyen_kg": 0.08},
        {"nom": "Papier", "poids_moyen_kg": 0.02},
        {"nom": "Déchets divers", "poids_moyen_kg": 0.10},
    ]

    materials = {}
    for mat in materials_data:
        obj, created = Material.objects.get_or_create(
            nom=mat["nom"],
            defaults={"poids_moyen_kg": mat["poids_moyen_kg"]}
        )
        materials[mat["nom"]] = obj
        action = "Créé" if created else "Existant"
        print(f"[{action}] Matériau : {obj.nom}")

    # 2. Projets
    projects_data = [
        {
            "titre": "Pot de fleurs auto-arrosant",
            "description": "Transformez une bouteille en plastique en une élégante jardinière autonome pour vos plantes d'intérieur.",
            "cout_estime": 2.50,
            "duree_minutes": 25,
            "difficulte": "facile",
            "materiaux": ["Plastique"],
            "etapes": [
                "Nettoyez soigneusement une bouteille en plastique et retirez l'étiquette.",
                "Découpez la bouteille en deux parties horizontales à environ 10 cm du goulot.",
                "Percez un trou dans le bouchon et insérez-y une mèche en coton ou cordelette (5 cm de chaque côté).",
                "Vissez le bouchon, retournez la partie supérieure goulot vers le bas et placez-la dans la base.",
                "Remplissez le fond d'eau, ajoutez du terreau et votre plante dans la partie supérieure."
            ]
        },
        {
            "titre": "Distributeur de sacs suspendu",
            "description": "Un distributeur pratique et hygiénique pour ranger tous vos sacs plastiques réutilisables.",
            "cout_estime": 0.00,
            "duree_minutes": 15,
            "difficulte": "facile",
            "materiaux": ["Plastique"],
            "etapes": [
                "Prenez une grande bouteille en plastique propre (2L ou 5L).",
                "Découpez proprement le fond de la bouteille pour créer l'ouverture de remplissage.",
                "Poncez doucement les rebords découpés pour éliminer toute aspérité.",
                "Fixez la bouteille tête en bas sur un mur ou l'intérieur d'un placard.",
                "Insérez les sacs par le haut et tirez-les facilement un par un par le goulot !"
            ]
        },
        {
            "titre": "Organisateur de bureau & Range-revues",
            "description": "Donnez une seconde vie à vos boîtes en carton en créant un organisateur de documents moderne et solide.",
            "cout_estime": 3.00,
            "duree_minutes": 35,
            "difficulte": "facile",
            "materiaux": ["Carton", "Papier"],
            "etapes": [
                "Prenez une boîte en carton (boîte de céréales ou colis postal rigide).",
                "Tracez une ligne diagonale sur les flancs depuis la moitié de la hauteur jusqu'au coin supérieur opposé.",
                "Découpez soigneusement selon le tracé pour obtenir le profil biseauté d'un range-documents.",
                "Renforcez les arêtes intérieures avec du ruban adhésif pour une robustesse optimale.",
                "Personnalisez l'extérieur avec du papier kraft, de la peinture ou des découpes graphiques."
            ]
        },
        {
            "titre": "Support ergonomique pour ordinateur",
            "description": "Surélevez l'écran de votre ordinateur portable à hauteur des yeux pour un confort de travail parfait.",
            "cout_estime": 1.00,
            "duree_minutes": 40,
            "difficulte": "moyen",
            "materiaux": ["Carton"],
            "etapes": [
                "Sélectionnez un carton ondulé solide à double cannelure.",
                "Découpez deux triangles identiques avec un angle de 20 degrés pour surélever l'ordinateur.",
                "Réalisez une encoche de retenue à l'avant pour sécuriser l'ordinateur portable.",
                "Découpez une traverse centrale pour relier fermement les deux triangles latéraux.",
                "Assemblez les pièces par emboîtement et profitez d'une meilleure aération pour votre PC."
            ]
        },
        {
            "titre": "Vase d'ambiance & Photophore",
            "description": "Sublimez vos bocaux ou bouteilles en verre pour créer une décoration chaleureuse et raffinée.",
            "cout_estime": 4.00,
            "duree_minutes": 30,
            "difficulte": "facile",
            "materiaux": ["Verre"],
            "etapes": [
                "Immergez le bocal en verre dans de l'eau tiède pour retirer l'étiquette et les résidus de colle.",
                "Nettoyez et essuyez la surface avec un chiffon propre et sec.",
                "Enroulez une ficelle de jute naturelle autour du col du bocal et nouez délicatement.",
                "Versez une fine couche de sable fin ou de petits galets au fond du bocal.",
                "Déposez une bougie chauffe-plat ou des fleurs séchées à l'intérieur pour une ambiance cosy."
            ]
        },
        {
            "titre": "Pot à crayons & ustensiles stylisé",
            "description": "Récupérez vos boîtes de conserve métalliques pour fabriquer des pots de rangement design et durables.",
            "cout_estime": 1.50,
            "duree_minutes": 20,
            "difficulte": "facile",
            "materiaux": ["Métal"],
            "etapes": [
                "Lavez abondamment la boîte de conserve métallique et retirez l'étiquette papier.",
                "À l'aide d'une pince, repliez ou limez le rebord métallique intérieur pour sécuriser la manipulation.",
                "Appliquez une couche de peinture pour métal ou recouvrez le cylindre d'une feuille de liège ou de corde.",
                "Laissez sécher pendant environ 15 minutes.",
                "Organisez-y vos stylos, pinceaux ou couverts de cuisine !"
            ]
        }
    ]

    for p_data in projects_data:
        mats = [materials[m] for m in p_data["materiaux"] if m in materials]
        project, created = Project.objects.get_or_create(
            titre=p_data["titre"],
            defaults={
                "description": p_data["description"],
                "cout_estime": p_data["cout_estime"],
                "duree_minutes": p_data["duree_minutes"],
                "difficulte": p_data["difficulte"],
                "etapes": p_data["etapes"]
            }
        )
        if created:
            project.materiaux.set(mats)
            print(f"[Créé] Projet : {project.titre}")
        else:
            print(f"[Existant] Projet : {project.titre}")

    print("\nInitialisation terminée avec succès !")

if __name__ == '__main__':
    seed()
