from django.urls import path

from . import views

app_name = 'distribute'
urlpatterns = [
    path('edit_count/', views.edit_count_to_distribute, name='edit_count'),
    path('designate_patients/', views.designate_patients,name='designate_patients'),
    path('patient_assignments/', views.patient_assignments, name='patient_assignments'),
    path('set_rounders/', views.set_rounders, name='set_rounders'),
    path('', views.current_rounders, name='current_rounders'),
]