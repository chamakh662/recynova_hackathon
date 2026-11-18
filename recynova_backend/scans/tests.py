from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from users.models import User
from materials.models import Material
from projects.models import Project
from scans.models import Scan
from PIL import Image
import json
import io


def make_test_image(color=(120, 120, 120)):
    buf = io.BytesIO()
    Image.new("RGB", (100, 100), color=color).save(buf, format="JPEG")
    return buf.getvalue()


class ScanMultiImageAndManualTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="tester@example.com",
            password="password123",
            nom="Tester Recy"
        )
        self.client.force_authenticate(user=self.user)

        self.carton = Material.objects.create(nom="Carton", poids_moyen_kg=0.15)
        self.plastic = Material.objects.create(nom="Plastique", poids_moyen_kg=0.05)
        self.papier = Material.objects.create(nom="Papier", poids_moyen_kg=0.02)

        self.p_carton = Project.objects.create(
            titre="Organisateur en carton",
            description="Super organisateur",
            cout_estime=3.0,
            duree_minutes=30,
            difficulte="facile",
            etapes=["1. Découper", "2. Assembler"]
        )
        self.p_carton.materiaux.add(self.carton)

        self.p_plastic = Project.objects.create(
            titre="Pot de fleurs bouteille",
            description="Jardinière bouteille",
            cout_estime=2.0,
            duree_minutes=25,
            difficulte="facile",
            etapes=["1. Couper", "2. Planter"]
        )
        self.p_plastic.materiaux.add(self.plastic)

    def test_two_photos_bottle_and_carton(self):
        # User scenario 1: 1 photo contains a bottle, the other contains carton
        # Expected: Carton and Plastique (NOT métal)
        img_bottle = SimpleUploadedFile(
            "bouteille_eau.jpg",
            make_test_image(color=(100, 140, 200)),
            content_type="image/jpeg"
        )
        img_carton = SimpleUploadedFile(
            "carton_box.jpg",
            make_test_image(color=(160, 120, 80)),
            content_type="image/jpeg"
        )

        res = self.client.post(
            "/api/scans/",
            {
                "images": [img_bottle, img_carton],
                "budget": 10,
                "temps_dispo": 45,
                "difficulte": "facile"
            },
            format="multipart"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        mat_names = [m["nom"] for m in res.data["materiaux"]]
        self.assertIn("Carton", mat_names)
        self.assertIn("Plastique", mat_names)
        self.assertNotIn("Métal", mat_names)

    def test_single_image_with_three_products(self):
        # User scenario 2: 1 photo containing paper and two plastic bottles
        # Expected: Papier and Plastique (NOT métal)
        img_multi = SimpleUploadedFile(
            "papier_et_bouteilles_plastique.jpg",
            make_test_image(color=(220, 220, 220)),
            content_type="image/jpeg"
        )

        res = self.client.post(
            "/api/scans/",
            {
                "images": [img_multi],
                "budget": 10,
                "temps_dispo": 45,
                "difficulte": "facile"
            },
            format="multipart"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        mat_names = [m["nom"] for m in res.data["materiaux"]]
        self.assertIn("Papier", mat_names)
        self.assertIn("Plastique", mat_names)
        self.assertNotIn("Métal", mat_names)

    def test_anonymous_image_carton(self):
        # Test anonymous carton image (no filename hint, only kraft color)
        img_carton_anon = SimpleUploadedFile(
            "photo_123.jpg",
            make_test_image(color=(170, 130, 85)),
            content_type="image/jpeg"
        )
        res = self.client.post(
            "/api/scans/",
            {
                "images": [img_carton_anon],
                "budget": 10,
                "temps_dispo": 45,
                "difficulte": "facile"
            },
            format="multipart"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        mat_names = [m["nom"] for m in res.data["materiaux"]]
        self.assertIn("Carton", mat_names)
        self.assertNotIn("Métal", mat_names)

    def test_manual_materials_without_image(self):
        manual_json = json.dumps([{"nom": "Carton", "quantite": 3}, {"nom": "Verre", "quantite": 1}])
        res = self.client.post(
            "/api/scans/",
            {
                "materiaux": manual_json,
                "budget": 10,
                "temps_dispo": 45,
                "difficulte": "facile"
            },
            format="multipart"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        mat_names = [m["nom"] for m in res.data["materiaux"]]
        self.assertIn("Carton", mat_names)
        self.assertIn("Verre", mat_names)
        self.assertTrue(len(res.data["recommendations"]) > 0)

    def test_real_user_uploaded_image_all_materials(self):
        # Image réelle contenant la bouteille plastique, le bocal en verre et le rouleau papier/carton
        real_img_path = r"C:\Users\admin\.gemini\antigravity\brain\bd255dd3-39d2-4899-b549-6333b2c78cc0\.user_uploaded\media_1794949183683_23057f0a.jpg"
        import os
        if os.path.exists(real_img_path):
            with open(real_img_path, "rb") as f:
                img_data = f.read()
            uploaded = SimpleUploadedFile("real_photo.jpg", img_data, content_type="image/jpeg")
            res = self.client.post(
                "/api/scans/",
                {
                    "images": [uploaded],
                    "budget": 10,
                    "temps_dispo": 45,
                    "difficulte": "facile"
                },
                format="multipart"
            )
            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            mat_names = [m["nom"] for m in res.data["materiaux"]]
            self.assertIn("Plastique", mat_names)
            self.assertIn("Verre", mat_names)
            self.assertIn("Papier", mat_names)
            self.assertIn("Carton", mat_names)
            self.assertNotIn("Métal", mat_names)
