"""yqry URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf.urls import url
from web import views
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('^$', views.index),
    url('^dx_import$', views.dx_import),
    url('^muban_upload$', views.muban_upload),
    url('^need_update_db$', views.need_update_db),
    url('^white_red_list_set$', views.white_red_list_set),
    url('^white_red_list_set_db$', views.white_red_list_set_db),
    url('^yqdx_list$', views.yqdx_list),
    url('^jjbd$', views.jjbd),
    url('^jjbd_upload$', views.jjbd_upload),
    url('^back_date_whitelist$', views.back_date_whitelist),
    url('^bddc$', views.bddc),
    url('^bddc_upload$', views.bddc_upload),
    url('^yqdx_list_export$', views.yqdx_list_export),
    url(r'^download$', views.download, name='file_download'),
    url(r'^yqdx_mod$', views.yqdx_mod, name='yqdx_mod'),
    url(r'^yqdx_del$', views.yqdx_del, name='yqdx_del'),
    url(r'^yqdx_mod_db$', views.yqdx_mod_db, name='yqdx_mod_db'),

    #话务组url
    url('^dx_import_hwz$', views.dx_import_hwz),
    url('^muban_upload_hwz$', views.muban_upload_hwz),
    url('^need_update_db_hwz$', views.need_update_db_hwz),
    url('^yqdx_list_hwz$', views.yqdx_list_hwz),
    url('^jjbd_hwz$', views.jjbd_hwz),
    url('^jjbd_upload_hwz$', views.jjbd_upload_hwz),
    url('^bddc_hwz$', views.bddc_hwz),
    url('^bddc_upload_hwz$', views.bddc_upload_hwz),
    url('^yqdx_list_export_hwz$', views.yqdx_list_export_hwz),
    url(r'^yqdx_mod_hwz$', views.yqdx_mod_hwz, name='yqdx_mod_hwz'),
    url(r'^yqdx_del_hwz$', views.yqdx_del_hwz, name='yqdx_del_hwz'),
    url(r'^yqdx_mod_db_hwz$', views.yqdx_mod_db_hwz, name='yqdx_mod_db_hwz'),




]
