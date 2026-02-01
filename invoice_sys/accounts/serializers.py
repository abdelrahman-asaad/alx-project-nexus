from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

# --- Activate Account Serializer ---
class ActivateAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"}
    )

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email not found in our records.")

        if user.has_usable_password():
            raise serializers.ValidationError("Account already active. Please login.")

        self.context["user"] = user
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def save(self, **kwargs):
        user = self.context["user"]
        password = self.validated_data["password"]
        user.set_password(password)
        user.is_active = True
        user.save()
        return user


# --- Register Serializer (هنا التعديل الجوهري) ---
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        # ❌ حذفنا الـ username تماماً لأن الموديل بتاعك مبقاش فيه الحقل ده
        fields = ['id', 'email', 'password', 'role']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("هذا البريد الإلكتروني مسجل بالفعل.")
        return value

    def create(self, validated_data):
        # ✅ حذفنا username=validated_data['email'] 
        # المانجر (UserManager) اللي أنت عملته بياخد الإيميل والباسورد بس
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'sales')
        )
        return user


# --- User Serializer ---
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # تأكد إنك مش حاطط username هنا برضه
        fields = ['id', 'email', 'role']


# --- Update Role Serializer ---
class UpdateRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["role"]

    def to_internal_value(self, data):
        if "role" in data and isinstance(data["role"], str):
            data["role"] = data["role"].lower().strip()
        return super().to_internal_value(data)