from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Follow, Profile
from .serializers import ProfileSerializer, RegisterSerializer, UserSerializer


User = get_user_model()


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)
        if not user:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        return Response(ProfileSerializer(profile).data)

    def patch(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class FollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id, *args, **kwargs):
        target = get_object_or_404(User, pk=user_id)
        if target == request.user:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        _, created = Follow.objects.get_or_create(
            follower=request.user,
            following=target,
        )
        return Response(
            {"detail": "Following." if created else "Already following."},
            status=status.HTTP_200_OK,
        )


class UnfollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, user_id, *args, **kwargs):
        target = get_object_or_404(User, pk=user_id)
        deleted, _ = Follow.objects.filter(
            follower=request.user,
            following=target,
        ).delete()
        return Response(
            {"detail": "Unfollowed." if deleted else "Not following."},
            status=status.HTTP_200_OK,
        )


class FeedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from rest_framework.pagination import PageNumberPagination
        from resources.models import Resource
        from resources.serializers import ResourceSerializer

        following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list("following_id", flat=True)
        queryset = (
            Resource.objects.filter(owner_id__in=following_ids)
            .select_related("owner", "category")
            .order_by("-created_at")
        )
        is_available = request.query_params.get("is_available")
        if is_available is not None:
            if str(is_available).lower() in ("true", "1", "yes"):
                queryset = queryset.filter(is_available=True)
            elif str(is_available).lower() in ("false", "0", "no"):
                queryset = queryset.filter(is_available=False)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(queryset, request)
        serializer = ResourceSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

