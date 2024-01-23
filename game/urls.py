from django.urls import path

from . import views

urlpatterns = [
    path('9_man_moris/', views.make_move)
]