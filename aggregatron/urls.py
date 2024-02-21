from django.urls import path

from . import views

urlpatterns = (
    path(r'rack-overview/', views.RackOverviewListView.as_view(), name='rack_list'),
    path(r'device-overview/', views.DeviceOverviewListView.as_view(), name='device_list'),
)
