from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id','first_name','last_name', 'email')


class AdminSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Administradores
        fields = '__all__'


class AlumnoSerializer(serializers.ModelSerializer): 
    user=UserSerializer(read_only=True)
    class Meta: 
        model = Alumnos 
        fields = '__all__'

class MaestroSerializer(serializers.ModelSerializer): 
    user=UserSerializer(read_only=True)
    class Meta: 
        model = Maestros 
        fields = '__all__'

class MateriaSerializer(serializers.ModelSerializer):
    profesor_nombre = serializers.SerializerMethodField()
    profesor_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Materias
        fields = '__all__'
        extra_fields = ['profesor_nombre', 'profesor_id']
    
    def get_profesor_nombre(self, obj):
        if obj.profesor and obj.profesor.user:
            return f"{obj.profesor.user.first_name} {obj.profesor.user.last_name}"
        return None
    
    def get_profesor_id(self, obj):
        if obj.profesor:
            return obj.profesor.id
        return None
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.profesor:
            representation['profesor'] = str(instance.profesor.id)
        else:
            representation['profesor'] = None
        return representation