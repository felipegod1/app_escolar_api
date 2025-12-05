from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views.bootstrap import VersionView
from app_escolar_api.views import bootstrap
from app_escolar_api.views import users
from app_escolar_api.views import alumnos
from app_escolar_api.views import maestros
from app_escolar_api.views import auth
from app_escolar_api.views import materias


urlpatterns = [

        path('admin/', users.AdminView.as_view()),
        path('lista-admins/', users.AdminAll.as_view()),
        path('alumnos/', alumnos.AlumnosView.as_view()),
        path('lista-alumnos/', alumnos.AlumnosAll.as_view()),
        path('maestros/', maestros.MaestrosView.as_view()),
        path('lista-maestros/', maestros.MaestrosAll.as_view()),
        path('total-usuarios/', users.TotalUsers.as_view()),
    path('materias/', materias.MateriasView.as_view()),
    path('lista-materias/', materias.MateriasAll.as_view()),
    path('lista-maestros/', materias.ListaMaestrosView.as_view()),
        path('login/', auth.CustomAuthToken.as_view()),
        path('logout/', auth.Logout.as_view())
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
