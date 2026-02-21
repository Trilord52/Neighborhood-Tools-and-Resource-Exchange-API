from rest_framework import serializers

from .models import Category, Comment, Resource, ResourceLike


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class ResourceSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    like_count = serializers.SerializerMethodField()
    liked_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = [
            "id",
            "name",
            "description",
            "owner",
            "category",
            "is_available",
            "created_at",
            "like_count",
            "liked_by_me",
        ]
        read_only_fields = ["id", "owner", "created_at", "like_count", "liked_by_me"]

    def get_like_count(self, obj):
        if hasattr(obj, "_like_count"):
            return obj._like_count
        return obj.likes.count()

    def get_liked_by_me(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        if hasattr(obj, "_liked_by_me"):
            return obj._liked_by_me
        return obj.likes.filter(user=request.user).exists()


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    resource = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "resource", "author", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "resource", "author", "created_at", "updated_at"]

