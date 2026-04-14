from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['uname', 'email', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)   
        user.save()
        return user


class UserProfileLinksUpdateSerializer(serializers.ModelSerializer):
    leetcode_username = serializers.CharField(
        source='Leetcode_username',
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=100,
    )
    codeforces_username = serializers.CharField(
        source='Codeforces_username',
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=100,
    )

    class Meta:
        model = User
        fields = ['linkedin_url', 'leetcode_username', 'codeforces_username']
