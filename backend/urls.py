from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('/moviesingle/<mvid>',views.moviesingle,name='moviesingle'),
]