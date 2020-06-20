"""MovieRecommend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path,include
from backend import views
import xadmin
urlpatterns = [
    #path('',include('backend.urls')),
    path('',views.index,name='index'),
    path('moviesingle/<mvid>',views.moviesingle,name='moviesingle'),
    path('movielist/',views.movielist,name='movielist'),
    path('moviesinglepage/<mvid>',views.moviesingle_page,name='moviesingle_page'),
    path('movielistlayui/',views.movielistlayui,name="movielistlayui"),
    path('moviegrid/',views.moviegrid,name="moviegrid"),
    path('moviegridlayui/',views.moviegridlayui,name="moviegridlayui"),
    path('moviesearch/',views.moviesearch,name="moviesearch"),
    path('moviesearchlayui/',views.moviesearchlayui,name="moviesearchlayui"),
    path('login/',views.login,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('register/',views.register,name='register'),
    path('user/profile/',views.userprofile,name='userprofile'),
    path('user/changeinfo/',views.userchangeinfo,name='userchangeinfo'),
    path('user/changepwd/',views.userchangepwd,name='userchangepwd'),
    path('user/comments/',views.usercomments,name='usercomments'),
    path('user/commentslayui/',views.usercommentslayui,name='usercommentslayui'),
    path('xadmin/', xadmin.site.urls),
    path('rate/',views.rate,name='rate'),
    path('shortcomment/',views.shortcomment,name='shortcomment'),
    path('writeblog/',views.writeblog,name='writeblog'),
    path('blogpost/',views.blogpost,name='blogpost'),
    path('blogdetail/<id>',views.blogdetail,name='blogdetail'),
    path('bloglist',views.bloglist,name="bloglist"),
    path('adjustRecommend/',views.adjustRecommend,name='adjustRecommend')
]
