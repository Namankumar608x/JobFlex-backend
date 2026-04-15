from rest_framework import serializers
from .models import Blog, Comment, Upvote

class CommentSerializer(serializers.ModelSerializer):
    uname = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'blog', 'U_ID', 'comment_text', 'created_at', 'uname']

    def get_uname(self, obj):
        user = getattr(obj, "U_ID", None)
        return getattr(user, "uname", "Anonymous")

class BlogSerializer(serializers.ModelSerializer):
    uname = serializers.SerializerMethodField()
    upvote_count = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Blog
        fields = ['id', 'title', 'blogtext', 'U_ID', 'uname', 'upvote_count', 'comments']

    def get_uname(self, obj):
        user = getattr(obj, "U_ID", None)
        return getattr(user, "uname", "Anonymous")

    def get_upvote_count(self, obj):
        annotated_count = getattr(obj, "upvote_count", None)
        if annotated_count is not None:
            return annotated_count
        return obj.upvotes.count()
