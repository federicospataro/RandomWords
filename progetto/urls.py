"""progetto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from randomwords import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('login/registrati', views.registrati, name='registrati'),
    path('logout/', views.logout, name='logout'),
    path('pubblica/', views.pubblica, name='pubblica'),
    path('approva/', views.approva, name='approva'),
    path('pagina/<str:parametro>/<int:page>/', views.pagina, name='pagina'),
    path('cerca/', views.cerca, name='cerca'),
    path('profilo/', views.mioprofilo,name="mioprofilo"),
    path('profilo/<int:codice>/<int:page>/',views.profilo,name="profilo"),
    path('contenuto/<int:cod>/',views.contenuto,name="contenuto"),
    path('like/<int:cod>/<int:p>/',views.like,name="like"),
    path('modificaprofilo/',views.modificaprofilo,name="modificaprofilo")
]
