from django.urls import path

from . import views

urlpatterns = [
    path('', views.UserList.as_view(), name="user-list"),
    path('<uuid:pk>/', views.UserDetail.as_view(), name="user-detail"),
    path('change-password/', views.ChangePassword.as_view(), name="change-password"),
]
