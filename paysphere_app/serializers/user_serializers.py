from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate
from ..models.user_models import User
import re
from datetime import date

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data (excludes password unless updating)"""

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_no', 'gender', 'dob', 'designation', 'group', 'is_active', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'email': {'required': False}
        }

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)  

        for attr, value in validated_data.items():
            setattr(instance, attr, value)  

        if password: 
            instance.password = make_password(password)

        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password', 
                  'phone_no', 'gender', 'dob', 'designation', 'group', 'address']

        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):

        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):  
            raise serializers.ValidationError("Enter a valid email address.")

        if User.objects.filter(email=value).exists():  
            raise serializers.ValidationError("Email is already in use.")

        return value

    def validate_first_name(self, value):

        if not re.match(r'^[A-Za-z]+$', value):
            raise serializers.ValidationError("First name can only contain letters.")

        return value

    def validate_last_name(self, value):
        if not re.match(r'^[A-Za-z]+$', value):
            raise serializers.ValidationError("Last name can only contain letters.")

        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")

        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one number.")

        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Password must contain at least one letter.")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError("Password must contain at least one special character.")

        return value

    def validate_phone_no(self, value):
        if not re.match(r'^\d{10}$', value): 
            raise serializers.ValidationError("Phone number must be 10 digits long and contain only numbers.")

        return value

    def validate_gender(self, value):
        allowed_genders = ['Male', 'Female', 'Other']

        if value not in allowed_genders:
            raise serializers.ValidationError(f"Gender must be one of {allowed_genders}.")

        return value

    def validate_group(self, value):
        allowed_groups = ['HR', 'EMPLOYEE']

        if value not in allowed_groups:
            raise serializers.ValidationError(f"Group must be one of {allowed_groups}.")

        return value

    def validate_dob(self, value):
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))

        if age < 18:
            raise serializers.ValidationError("User must be at least 18 years old.")

        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password') 
        validated_data['password'] = make_password(validated_data['password'])
        
        return super().create(validated_data)

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
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