from django.urls import path

from . import views

urlpatterns = [
    path('patients/', views.PatientCreateView.as_view(), name='patient-create'),
    path('patients/<int:pk>/history/', views.PatientHistoryView.as_view(), name='patient-history'),
    path('patients/<int:pk>/predict/', views.CVDPredictView.as_view(), name='patient-predict'),
    path('health-records/', views.HealthRecordCreateView.as_view(), name='healthrecord-create'),
]
