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

class MaestrosAll(generics.CreateAPIView):
    # Obtener todos los maestros activos
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        maestros = Maestros.objects.filter(user__is_active=1).order_by("id")
        lista = MaestroSerializer(maestros, many=True).data
        
        # Convertir materias_json de string a lista para el frontend
        for maestro in lista:
            if "materias_json" in maestro and maestro["materias_json"]:
                try:
                    maestro["materias_json"] = json.loads(maestro["materias_json"])
                except:
                    maestro["materias_json"] = []
        
        return Response(lista, 200)

class MaestrosView(generics.CreateAPIView):
    # Control de permisos
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [] 

    # Obtener maestro por ID
    def get(self, request, *args, **kwargs):
        try:
            # Buscamos por el ID que manda Angular (?id=...)
            maestro = get_object_or_404(Maestros, id=request.GET.get("id"))
            maestro_data = MaestroSerializer(maestro, many=False).data
            
            # Parsear materias_json si existe
            if "materias_json" in maestro_data and maestro_data["materias_json"]:
                try:
                    maestro_data["materias_json"] = json.loads(maestro_data["materias_json"])
                except:
                    maestro_data["materias_json"] = []
            
            return Response(maestro_data, 200)
        except Exception as e:
            return Response({"error": str(e)}, 404)

    # Registrar nuevo maestro
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

            # Crear perfil de Maestro
            # Nota: Convertimos la lista de materias a JSON string antes de guardar
            materias_str = json.dumps(request.data["materias_json"]) if "materias_json" in request.data else "[]"

            maestro = Maestros.objects.create(user=user,
                                            id_trabajador= request.data["id_trabajador"],
                                            fecha_nacimiento= request.data["fecha_nacimiento"],
                                            telefono= request.data["telefono"],
                                            rfc= request.data["rfc"].upper(),
                                            cubiculo= request.data["cubiculo"],
                                            area_investigacion= request.data["area_investigacion"],
                                            materias_json = materias_str)
            maestro.save()

            return Response({"maestro_created_id": maestro.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)

    # Actualizar maestro (PUT)
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        # Obtenemos el maestro por ID
        maestro = get_object_or_404(Maestros, id=request.data.get("id"))
        
        # Actualizar datos de la tabla Maestros
        maestro.id_trabajador = request.data.get("id_trabajador", maestro.id_trabajador)
        maestro.fecha_nacimiento = request.data.get("fecha_nacimiento", maestro.fecha_nacimiento)
        maestro.telefono = request.data.get("telefono", maestro.telefono)
        maestro.rfc = request.data.get("rfc", maestro.rfc).upper()
        maestro.cubiculo = request.data.get("cubiculo", maestro.cubiculo)
        maestro.area_investigacion = request.data.get("area_investigacion", maestro.area_investigacion)
        
        if "materias_json" in request.data:
             maestro.materias_json = json.dumps(request.data["materias_json"])
        
        maestro.save()
        
        # Actualizar datos del usuario (User)
        user = maestro.user
        user.first_name = request.data.get("first_name", user.first_name)
        user.last_name = request.data.get("last_name", user.last_name)
        user.save()
        
        return Response({"message": "Maestro actualizado correctamente"}, 200)

    # Eliminar maestro
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        maestro = get_object_or_404(Maestros, id=request.GET.get("id"))
        try:
            maestro.user.delete()
            return Response({"details":"Maestro eliminado"}, 200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"}, 400)