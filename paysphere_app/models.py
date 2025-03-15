from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """ Custom manager for User model without username field """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)  
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """ Creates and returns a superuser """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("group", "HR")  

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):  
    
    username = None  
    email = models.EmailField(unique=True)  

    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Other')
    dob = models.DateField(null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField(default="Unknown")  

    
    GROUP_CHOICES = [('HR', 'HR/Admin'), ('EMPLOYEE', 'Employee')]
    group = models.CharField(max_length=10, choices=GROUP_CHOICES, default='EMPLOYEE')

    # Contact Details
    phone_no = models.CharField(max_length=15, default="0000000000")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  
    modified_at = models.DateTimeField(auto_now=True)

    # Audit Fields
    created_by = models.CharField(max_length=100, null=True, blank=True)
    modified_by = models.CharField(max_length=100, null=True, blank=True)

    # Active Status 
    is_active = models.BooleanField(default=True)

    # Department
    department = models.CharField(max_length=100, null=True, blank=True)

    # Define authentication fields
    USERNAME_FIELD = "email"  
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_no", "gender", "dob", "designation", "group"]

    objects = CustomUserManager()  # Use the custom manager

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.group}"