from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_company, name='add_company'),
    path('switch/<int:company_id>/', views.switch_company, name='switch_company'),
]
