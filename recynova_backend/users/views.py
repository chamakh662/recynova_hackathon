from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        nom = request.data.get("nom")
        email = request.data.get("email")
        password = request.data.get("password")

        if not nom or not email or not password:
            return Response(
                {"error": "Tous les champs sont obligatoires."},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = email.strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            return Response(
                {"error": "Cet email existe déjà."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(password) < 8:
            return Response(
                {"error": "Le mot de passe doit contenir au moins 8 caractères."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            email=email,
            password=password,
            nom=nom
        )

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Inscription réussie.",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "nom": user.nom,
                "email": user.email,
                "eco_score_total": user.eco_score_total
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email et mot de passe obligatoires."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            request,
            email=email.strip().lower(),
            password=password
        )

        if user is None:
            return Response(
                {"error": "Email ou mot de passe incorrect."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Connexion réussie.",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "nom": user.nom,
                "email": user.email,
                "eco_score_total": user.eco_score_total
            }
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            "id": user.id,
            "nom": user.nom,
            "email": user.email,
            "eco_score_total": user.eco_score_total
        })

    def put(self, request):
        user = request.user

        nom = request.data.get("nom", user.nom)
        email = request.data.get("email", user.email).strip().lower()

        if User.objects.filter(email__iexact=email).exclude(
            id=user.id
        ).exists():
            return Response(
                {"error": "Cet email est déjà utilisé."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.nom = nom
        user.email = email
        user.save()

        return Response({
            "message": "Profil modifié avec succès.",
            "id": user.id,
            "nom": user.nom,
            "email": user.email,
            "eco_score_total": user.eco_score_total
        })