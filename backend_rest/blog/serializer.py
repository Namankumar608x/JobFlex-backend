from rest_framework import serializers
from .models import Blog, Comment, Upvote
from user.models import User

class CommentSerializer(serializers.ModelSerializer):
    uname = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'blog', 'U_ID', 'comment_text', 'created_at', 'uname']

    def get_uname(self, obj):
        try:
            return obj.U_ID.uname
        except:
            return "Anonymous"

class BlogSerializer(serializers.ModelSerializer):
    uname = serializers.SerializerMethodField()
    upvote_count = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Blog
        fields = ['id', 'title', 'blogtext', 'U_ID', 'uname', 'upvote_count', 'comments']

    def get_uname(self, obj):
        try:
            user = User.objects.get(U_ID=obj.U_ID_id)
            return user.uname
        except User.DoesNotExist:
            return "Anonymous"

    def get_upvote_count(self, obj):
        return obj.upvotes.count()