"""
URL configuration for whatsapp_bot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from task.views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", bot, name="bot"),
    path("bot/", bot, name="bot"),
    path('add_task/<str:mobile>/', add_task, name='add_task'),
    path('add_tasks/<str:mobile>/', add_task2, name='add_task2'),
    path('view_tasks/<str:mobile>/', view_tasks, name='view_tasks'),
    path('update_notes/', update_notes, name='update_notes'),
    path('update_task/', update_task, name='update_task'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



# from django.urls import re_path

# # from django.conf.urls import url
# # from django.conf.urls.static import static

# # from . import views

# urlpatterns = [
#     re_path(r'^$', views.index, name='index'),
#     re_path(r'^config/$', views.config, name='config'),
#     re_path(r'^images/$', views.get_all_media, name='images'),
#     re_path(r'^images/(?P<filename>[0-9A-Za-z\.]{0,50})$', views.handle_delete_media_file, name='delete_image'),
#     re_path(r'^incoming/$', views.handle_incoming_message, name='incoming'),
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)