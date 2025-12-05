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

class AlumnosAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        alumnos = Alumnos.objects.filter(user__is_active=1).order_by("id")
        lista = AlumnoSerializer(alumnos, many=True).data
        return Response(lista, 200)

class AlumnosView(generics.CreateAPIView):
    # Control de permisos
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [] 

    # 1. OBTENER ALUMNO POR ID (GET)
    def get(self, request, *args, **kwargs):
        try:
            alumno = get_object_or_404(Alumnos, id=request.GET.get("id"))
            alumno_data = AlumnoSerializer(alumno, many=False).data
            return Response(alumno_data, 200)
        except Exception as e:
            return Response({"error": str(e)}, 404)
    
    # 2. REGISTRAR ALUMNO (POST)
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

            # Crear perfil de Alumno
            alumno = Alumnos.objects.create(user=user,
                                            matricula= request.data["matricula"],
                                            curp= request.data["curp"].upper(),
                                            rfc= request.data["rfc"].upper(),
                                            fecha_nacimiento= request.data["fecha_nacimiento"],
                                            edad= request.data["edad"],
                                            telefono= request.data["telefono"],
                                            ocupacion= request.data["ocupacion"])
            alumno.save()

            return Response({"alumno_created_id": alumno.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)

    # 3. ACTUALIZAR ALUMNO (PUT) -> ¡ESTE ES EL QUE TE FALTABA O FALLABA!
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        # Obtenemos el alumno por ID (que viene en el body del request)
        alumno = get_object_or_404(Alumnos, id=request.data.get("id"))
        
        # Actualizar datos específicos de Alumnos
        alumno.matricula = request.data.get("matricula", alumno.matricula)
        alumno.curp = request.data.get("curp", alumno.curp).upper()
        alumno.rfc = request.data.get("rfc", alumno.rfc).upper()
        alumno.fecha_nacimiento = request.data.get("fecha_nacimiento", alumno.fecha_nacimiento)
        alumno.edad = request.data.get("edad", alumno.edad)
        alumno.telefono = request.data.get("telefono", alumno.telefono)
        alumno.ocupacion = request.data.get("ocupacion", alumno.ocupacion)
        alumno.save()
        
        # Actualizar datos del usuario asociado (nombre, email)
        user = alumno.user
        user.first_name = request.data.get("first_name", user.first_name)
        user.last_name = request.data.get("last_name", user.last_name)
        # user.email = request.data.get("email", user.email) # Opcional si dejas editar email
        user.save()
        
        return Response({"message": "Alumno actualizado correctamente"}, 200)

    # 4. ELIMINAR ALUMNO (DELETE)
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        alumno = get_object_or_404(Alumnos, id=request.GET.get("id"))
        try:
            alumno.user.delete()
            return Response({"details":"Alumno eliminado"}, 200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"}, 400)