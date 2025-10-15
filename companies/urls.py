from django.urls import path
from . import views

urlpatterns = [
    path('select/', views.select_company, name='select_company'),
    path('select/<int:company_id>/', views.select_and_activate_company, name='select_and_activate_company'),
    path('add/', views.add_company, name='add_company'),
    path('switch/<int:company_id>/', views.switch_company, name='switch_company'),
    path('details/', views.company_details, name='company_details'),
    path('upload-logo/', views.upload_logo, name='upload_logo'),
]
