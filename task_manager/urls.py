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
    # path("", bot, name="bot"),
    path("bot/", bot, name="bot"),
    path("", home, name="home"),
    path('add_task/<str:mobile>/', add_task2, name='add_task2'),
    path('add_tasks/<str:mobile>/', add_task2, name='add_task2'),
    path('view_tasks/<str:mobile>/', view_tasks, name='view_tasks'),
    path('save_tasks/<str:mobile>/', save_tasks, name='save_tasks'),
    path('xxxxx/', view_users, name='view_users'),
    path('view_logs/<int:user_id>/', view_logs, name='view_logs'),
    path('view_tasks/periodic/<str:mobile>/', view_periodic_tasks, name='view_periodic_tasks'),
    path('feedback/', feedback, name='feedback'),
    path('contact/', contact, name='contact'),
    path('view_tasks2/<str:mobile>/', view_tasks2, name='view_tasks2'),
    path('view-task-details/<int:task_id>/', view_task_details, name='view_task_details'),
    path('update-task-details/<int:task_id>/', update_task_details, name='update_task_details'),
    path('delete-task/<int:task_id>/', delete_task, name='delete_task'),
    path('update-task-status', update_task_status, name='update_task_status'),
    path('registerclickevent/', save_click_event, name='save_click_event'),
    path('getcountry/', get_country, name='get_country'),
    path('xxxxxxx/', view_ClickEvent, name='view_ClickEvent'),
        
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urls.py
from django.conf.urls import handler404

handler404 = 'task.views.custom_404'  # Replace 'myapp.views.custom_404' with your view





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
