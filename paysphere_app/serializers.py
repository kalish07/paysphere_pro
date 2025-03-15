from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data (excludes password unless updating)"""

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_no', 'gender', 'dob', 'designation', 'group', 'is_active', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},  # ✅ Password is optional in updates
            'email': {'required': False}  # ✅ Email is optional in updates
        }

    def update(self, instance, validated_data):
        """Ensure password is updated correctly if provided"""
        password = validated_data.pop('password', None)  # Extract password if provided

        for attr, value in validated_data.items():
            setattr(instance, attr, value)  # Update other fields

        if password:  # ✅ If password is provided, hash it before saving
            instance.password = make_password(password)

        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'phone_no', 'gender', 'dob', 'designation', 'group']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Hash the password before saving the user"""
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Check user credentials and active status"""
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        if not check_password(password, user.password):
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("Your account is inactive. Please contact admin.")

        data["user"] = user
        return data