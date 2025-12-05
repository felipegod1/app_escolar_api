
from django.db.models import *
from django.db import transaction
from app_escolar_api.serializers import MateriaSerializer
from app_escolar_api.models import Materias, Maestros
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import json

class MateriasAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        materias = Materias.objects.all().order_by("id")
        
       
        lista = []
        for materia in materias:
            materia_data = MateriaSerializer(materia).data
            
          
            if materia.profesor:
                materia_data['profesor'] = str(materia.profesor.id)
                materia_data['profesor_nombre'] = f"{materia.profesor.user.first_name} {materia.profesor.user.last_name}"
            else:
                materia_data['profesor'] = None
                materia_data['profesor_nombre'] = None
            
            
            if materia.dias:
                try:
                    materia_data['dias'] = json.loads(materia.dias)
                except:
                    materia_data['dias'] = materia.dias.split(',') if materia.dias else []
            else:
                materia_data['dias'] = []
            
            lista.append(materia_data)
        
        return Response(lista, 200)

class MateriasView(generics.CreateAPIView):
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []
    
    def get(self, request, *args, **kwargs):
        materia_id = request.GET.get("id")
        if not materia_id:
            return Response({"error": "Se requiere el parámetro 'id'"}, status=400)
        
        try:
            materia = get_object_or_404(Materias, id=materia_id)
            materia_data = MateriaSerializer(materia).data
            
           
            if materia.profesor:
                materia_data['profesor'] = str(materia.profesor.id)
                materia_data['profesor_nombre'] = f"{materia.profesor.user.first_name} {materia.profesor.user.last_name}"
            else:
                materia_data['profesor'] = None
                materia_data['profesor_nombre'] = None
            
           
            if materia.dias:
                try:
                    materia_data['dias'] = json.loads(materia.dias)
                except:
                    materia_data['dias'] = materia.dias.split(',') if materia.dias else []
            else:
                materia_data['dias'] = []
            
            return Response(materia_data, 200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            required_fields = ['nrc', 'nombre', 'seccion', 'dias', 'programa_educativo', 'creditos']
            for field in required_fields:
                if field not in request.data or not request.data[field]:
                    return Response({"error": f"El campo {field} es requerido"}, status=400)
            
            if Materias.objects.filter(nrc=request.data['nrc']).exists():
                return Response({"error": "El NRC ya existe"}, status=400)
            
         
            dias_data = request.data['dias']
            if isinstance(dias_data, list):
                dias_str = json.dumps(dias_data)
            else:
                dias_str = dias_data
            
            materia_data = {
                'nrc': request.data['nrc'],
                'nombre': request.data['nombre'],
                'seccion': request.data['seccion'],
                'dias': dias_str,
                'programa_educativo': request.data['programa_educativo'],
                'creditos': request.data['creditos'],
                'salon': request.data.get('salon', ''),
            }
            
            if request.data.get('hora_inicio'):
                materia_data['hora_inicio'] = request.data['hora_inicio']
            if request.data.get('hora_fin'):
                materia_data['hora_fin'] = request.data['hora_fin']
            
            if request.data.get('profesor'):
                profesor = get_object_or_404(Maestros, id=request.data['profesor'])
                materia_data['profesor'] = profesor
            
            materia = Materias.objects.create(**materia_data)
            materia.save()
            
            return Response({
                "materia_created_id": materia.id, 
                "message": "Materia registrada correctamente",
                "materia": MateriaSerializer(materia).data
            }, 201)
            
        except Exception as e:
            return Response({"error": str(e)}, status=400)
    
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        try:
            if "id" not in request.data:
                return Response({"error": "Se requiere el campo 'id'"}, status=400)
            
            materia = get_object_or_404(Materias, id=request.data["id"])
            
           
            materia.nrc = request.data.get("nrc", materia.nrc)
            materia.nombre = request.data.get("nombre", materia.nombre)
            materia.seccion = request.data.get("seccion", materia.seccion)
        
            if "dias" in request.data:
                dias_data = request.data['dias']
                if isinstance(dias_data, list):
                    materia.dias = json.dumps(dias_data)
                else:
                    materia.dias = dias_data
            
            materia.hora_inicio = request.data.get("hora_inicio", materia.hora_inicio)
            materia.hora_fin = request.data.get("hora_fin", materia.hora_fin)
            materia.salon = request.data.get("salon", materia.salon)
            materia.programa_educativo = request.data.get("programa_educativo", materia.programa_educativo)
            materia.creditos = request.data.get("creditos", materia.creditos)
            
            if request.data.get('profesor'):
                profesor = get_object_or_404(Maestros, id=request.data['profesor'])
                materia.profesor = profesor
            elif 'profesor' in request.data and request.data['profesor'] is None:
                materia.profesor = None
            
            materia.save()
            
        
            materia_data = MateriaSerializer(materia).data
            if materia.profesor:
                materia_data['profesor'] = str(materia.profesor.id)
                materia_data['profesor_nombre'] = f"{materia.profesor.user.first_name} {materia.profesor.user.last_name}"
            
            return Response({
                "message": "Materia actualizada correctamente", 
                "materia": materia_data
            }, 200)
            
        except Exception as e:
            return Response({"error": str(e)}, status=400)
    
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            materia_id = request.GET.get("id")
            if not materia_id:
                return Response({"error": "Se requiere el parámetro 'id'"}, status=400)
            
            materia = get_object_or_404(Materias, id=materia_id)
            materia_id_deleted = materia.id
            materia.delete()
            
            return Response({
                "message": "Materia eliminada correctamente",
                "deleted_id": materia_id_deleted
            }, 200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class ListaMaestrosView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        try:
            maestros = Maestros.objects.filter(user__is_active=True).order_by("user__first_name")
            lista_maestros = []
            
            for maestro in maestros:
                lista_maestros.append({
                    'id': maestro.id,
                    'nombre_completo': f"{maestro.user.first_name} {maestro.user.last_name}",
                    'id_trabajador': maestro.id_trabajador,
                    'first_name': maestro.user.first_name,
                    'last_name': maestro.user.last_name,
                    'email': maestro.user.email
                })
            
            return Response(lista_maestros, 200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)