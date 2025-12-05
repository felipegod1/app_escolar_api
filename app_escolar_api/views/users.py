from django.shortcuts import render, get_object_or_404
from django.db.models import *
from django.db import transaction
from app_escolar_api.serializers import *
from app_escolar_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group
import json

class AdminAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        # Filtramos por usuarios activos
        admin = Administradores.objects.filter(user__is_active=1).order_by("id")
        lista = AdminSerializer(admin, many=True).data
        return Response(lista, 200)

class AdminView(generics.CreateAPIView):
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [] 
    
    # Obtener admin por ID
    def get(self, request, *args, **kwargs):
        try:
            admin = get_object_or_404(Administradores, id=request.GET.get("id"))
            admin = AdminSerializer(admin, many=False).data
            return Response(admin, 200)
        except Exception as e:
            return Response({"error": str(e)}, 404)
    
    # Registrar nuevo admin
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = UserSerializer(data=request.data)
        
        if user.is_valid():
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']

            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message":"Username "+email+", is already taken"}, 400)

            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)

            user.save()
            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            # Crear perfil de Administrador
            admin = Administradores.objects.create(user=user,
                                                   clave_admin= request.data["clave_admin"],
                                                   telefono= request.data["telefono"],
                                                   rfc= request.data["rfc"].upper(),
                                                   edad= request.data["edad"],
                                                   ocupacion= request.data["ocupacion"])
            admin.save()

            return Response({"admin_created_id": admin.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)

    # Actualizar datos del administrador
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        admin = get_object_or_404(Administradores, id=request.data.get("id"))
        
        # Actualizar datos del modelo Administradores
        admin.clave_admin = request.data.get("clave_admin", admin.clave_admin)
        admin.telefono = request.data.get("telefono", admin.telefono)
        admin.rfc = request.data.get("rfc", admin.rfc).upper()
        admin.edad = request.data.get("edad", admin.edad)
        admin.ocupacion = request.data.get("ocupacion", admin.ocupacion)
        admin.save()
        
        # Actualizar datos del usuario (User)
        user = admin.user
        user.first_name = request.data.get("first_name", user.first_name)
        user.last_name = request.data.get("last_name", user.last_name)
        user.save()
        
        return Response({"message": "Administrador actualizado correctamente"}, 200)

    # Eliminar administrador
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        admin = get_object_or_404(Administradores, id=request.GET.get("id"))
        try:
            admin.user.delete()
            return Response({"details": "Administrador eliminado"}, 200)
        except Exception as e:
            print(e)
            return Response({"details": "Algo pasó al eliminar"}, 400)

class TotalUsers(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        admin_qs = Administradores.objects.filter(user__is_active=True)
        total_admins = admin_qs.count()

        maestros_qs = Maestros.objects.filter(user__is_active=True)
        total_maestros = maestros_qs.count()

        alumnos_qs = Alumnos.objects.filter(user__is_active=True)
        total_alumnos = alumnos_qs.count()

        return Response({
            "admins": total_admins,
            "maestros": total_maestros,
            "alumnos": total_alumnos
        }, 200)