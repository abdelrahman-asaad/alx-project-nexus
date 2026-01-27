from rest_framework import serializers
from django.contrib.auth import get_user_model


from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class ActivateAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"}
    )

    # ---------------------------------
    # validate email
    # ---------------------------------
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Email not found in our records."
            )

        # لو الحساب متفعل قبل كده
        if user.has_usable_password():
            raise serializers.ValidationError(
                "Account already active. Please login."
            )

        # نخزن اليوزر عشان نستخدمه بعدين
        self.context["user"] = user
        return value

    # ---------------------------------
    # validate password strength
    # ---------------------------------
    def validate_password(self, value):
        validate_password(value)  # Django built-in validation
        return value

    # ---------------------------------
    # activate account logic
    # ---------------------------------
    def save(self, **kwargs):
        user = self.context["user"]
        password = self.validated_data["password"]

        user.set_password(password)
        user.is_active = True
        user.save()

        return user


class RegisterSerializer(serializers.ModelSerializer):
    # نحدد أن الإيميل مطلوب ويجب أن يكون فريداً في التحقق (Validation)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        # لاحظ أننا أبقينا الـ username لأن AbstractUser يطلبه بشكل افتراضي
        fields = ['id', 'username', 'email', 'password', 'role']

    def validate_email(self, value):
        # التأكد من أن الإيميل غير مستخدم مسبقاً قبل محاولة الإنشاء
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("هذا البريد الإلكتروني مسجل بالفعل.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'], # جعل اليوزر نيم هو الإيميل
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'sales')
        )
        return user
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

# Serializer مخصص لتحديث الدور فقط
class UpdateRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["role"] #it takes only the role field to be updated

#this validation is not necessary but good to have for developers using the API
#through Postman or other tools and not for end users using the web app
    
    def to_internal_value(self, data): #built-in method in DRF serializers to
# normalize input before validation (called before field validators run)        
        if "role" in data and isinstance(data["role"], str):
            data["role"] = data["role"].lower().strip()
        return super().to_internal_value(data)
    
