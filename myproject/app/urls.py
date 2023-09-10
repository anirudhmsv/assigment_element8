from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
        path('',views.adminlogin,name='login'),
        path('loginadmin',views.loginadmin),
        path('admindash',views.admindash),
        path('adminteacher',views.adminteacher),
        path('adminviewteacher', views.adminviewteacher),
        # path('import_page', views.import_page),
        path('import', views.import_teachers, name='import_teachers'),

]