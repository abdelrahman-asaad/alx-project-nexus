from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    #custom field to be serialized
    #write_only = True means that password is sending in request only
    #but not in viewed in response

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']
        #fields to be serialized
        

    def create(self, validated_data): #data to be saved in db
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'sales') # default role is 'sales'
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
    
