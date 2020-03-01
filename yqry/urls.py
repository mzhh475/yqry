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
from web import views, views_mzz, views_ypz, views_glz, views_hwz, views_fyz, views_hhz, views_hbz
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
    url(r'^search_all$', views.search_all, name='search_all'),

    #话务组url
    url('^dx_import_hwz$', views_hwz.dx_import_hwz),
    url('^muban_upload_hwz$', views_hwz.muban_upload_hwz),
    url('^need_update_db_hwz$', views_hwz.need_update_db_hwz),
    url('^yqdx_list_hwz$', views_hwz.yqdx_list_hwz),
    url('^jjbd_hwz$', views_hwz.jjbd_hwz),
    url('^jjbd_upload_hwz$', views_hwz.jjbd_upload_hwz),
    url('^bddc_hwz$', views_hwz.bddc_hwz),
    url('^bddc_upload_hwz$', views_hwz.bddc_upload_hwz),
    url('^yqdx_list_export_hwz$', views_hwz.yqdx_list_export_hwz),
    url(r'^yqdx_mod_hwz$', views_hwz.yqdx_mod_hwz, name='yqdx_mod_hwz'),
    url(r'^yqdx_del_hwz$', views_hwz.yqdx_del_hwz, name='yqdx_del_hwz'),
    url(r'^yqdx_mod_db_hwz$', views_hwz.yqdx_mod_db_hwz, name='yqdx_mod_db_hwz'),

    # 研判组url
    url('^dx_import_ypz$', views_ypz.dx_import_ypz),
    url('^muban_upload_ypz$', views_ypz.muban_upload_ypz),
    url('^need_update_db_ypz$', views_ypz.need_update_db_ypz),
    url('^yqdx_list_ypz$', views_ypz.yqdx_list_ypz),
    url('^jjbd_ypz$', views_ypz.jjbd_ypz),
    url('^jjbd_upload_ypz$', views_ypz.jjbd_upload_ypz),
    url('^bddc_ypz$', views_ypz.bddc_ypz),
    url('^bddc_upload_ypz$', views_ypz.bddc_upload_ypz),
    url('^yqdx_list_export_ypz$', views_ypz.yqdx_list_export_ypz),
    url(r'^yqdx_mod_ypz$', views_ypz.yqdx_mod_ypz, name='yqdx_mod_ypz'),
    url(r'^yqdx_del_ypz$', views_ypz.yqdx_del_ypz, name='yqdx_del_ypz'),
    url(r'^yqdx_mod_db_ypz$', views_ypz.yqdx_mod_db_ypz, name='yqdx_mod_db_ypz'),

    # 集中隔离数据组url
    url('^dx_import_glz$', views_glz.dx_import_glz),
    url('^muban_upload_glz$', views_glz.muban_upload_glz),
    url('^need_update_db_glz$', views_glz.need_update_db_glz),
    url('^yqdx_list_glz$', views_glz.yqdx_list_glz),
    url('^jjbd_glz$', views_glz.jjbd_glz),
    url('^jjbd_upload_glz$', views_glz.jjbd_upload_glz),
    url('^bddc_glz$', views_glz.bddc_glz),
    url('^bddc_upload_glz$', views_glz.bddc_upload_glz),
    url('^yqdx_list_export_glz$', views_glz.yqdx_list_export_glz),
    url(r'^yqdx_mod_glz$', views_glz.yqdx_mod_glz, name='yqdx_mod_glz'),
    url(r'^yqdx_del_glz$', views_glz.yqdx_del_glz, name='yqdx_del_glz'),
    url(r'^yqdx_mod_db_glz$', views_glz.yqdx_mod_db_glz, name='yqdx_mod_db_glz'),

    url(r'^muban_upload_glz$', views_glz.muban_upload_glz, name='muban_upload_glz'),

    #门诊组url
    url('^dx_import_mzz$', views_mzz.dx_import_mzz),
    url('^muban_upload_mzz$', views_mzz.muban_upload_mzz),
    url('^need_update_db_mzz$', views_mzz.need_update_db_mzz),
    url('^yqdx_list_mzz$', views_mzz.yqdx_list_mzz),
    url('^jjbd_mzz$', views_mzz.jjbd_mzz),
    url('^jjbd_upload_mzz$', views_mzz.jjbd_upload_mzz),
    url('^bddc_mzz$', views_mzz.bddc_mzz),
    url('^bddc_upload_mzz$', views_mzz.bddc_upload_mzz),
    url('^yqdx_list_export_mzz$', views_mzz.yqdx_list_export_mzz),
    url(r'^yqdx_mod_mzz$', views_mzz.yqdx_mod_mzz, name='yqdx_mod_mzz'),
    url(r'^yqdx_del_mzz$', views_mzz.yqdx_del_mzz, name='yqdx_del_mzz'),
    url(r'^yqdx_mod_db_mzz$', views_mzz.yqdx_mod_db_mzz, name='yqdx_mod_db_mzz'),

    #返甬人员url
    url('^dx_import_fyz$', views_fyz.dx_import_fyz),
    url('^tongbu$', views_fyz.tongbu),
    url('^yqdx_list_fyz$', views_fyz.yqdx_list_fyz),
    url('^yqdx_list_export_fyz$', views_fyz.yqdx_list_export_fyz),
    url('^jjbd_fyz$', views_fyz.jjbd_fyz),
    url('^jjbd_upload_fyz$', views_fyz.jjbd_upload_fyz),
    url('^bddc_fyz$', views_fyz.bddc_fyz),
    url('^bddc_upload_fyz$', views_fyz.bddc_upload_fyz),
    url('^zzq_fyz$', views_fyz.zzq_fyz_manager),
    url('^zzq_fyz_db$', views_fyz.zzq_fyz_db),
    url('^tongji_fyz$', views_fyz.tongji_fyz),

    url('^get_progress_message$', views_fyz.get_progress_message, name='get_progress_message'),


#红黄绿码组url
    url('^dx_import_hhz$', views_hhz.dx_import_hhz),
    url('^muban_upload_hhz$', views_hhz.muban_upload_hhz),
    url('^need_update_db_hhz$', views_hhz.need_update_db_hhz),
    url('^yqdx_list_hhz$', views_hhz.yqdx_list_hhz),
    url('^jjbd_hhz$', views_hhz.jjbd_hhz),
    url('^jjbd_upload_hhz$', views_hhz.jjbd_upload_hhz),
    url('^bddc_hhz$', views_hhz.bddc_hhz),
    url('^bddc_upload_hhz$', views_hhz.bddc_upload_hhz),
    url('^yqdx_list_export_hhz$', views_hhz.yqdx_list_export_hhz),
    url(r'^yqdx_mod_hhz$', views_hhz.yqdx_mod_hhz, name='yqdx_mod_hhz'),
    url(r'^yqdx_del_hhz$', views_hhz.yqdx_del_hhz, name='yqdx_del_hhz'),
    url(r'^yqdx_mod_db_hhz$', views_hhz.yqdx_mod_db_hhz, name='yqdx_mod_db_hhz'),

# 武汉籍在甬去库存数据组url
    url('^dx_import_hbz$', views_hbz.dx_import_hbz),
    url('^muban_upload_hbz$', views_hbz.muban_upload_hbz),
    url('^need_update_db_hbz$', views_hbz.need_update_db_hbz),
    url('^yqdx_list_hbz$', views_hbz.yqdx_list_hbz, name='yqdx_list_hbz'),
    url('^jjbd_hbz$', views_hbz.jjbd_hbz),
    url('^jjbd_upload_hbz$', views_hbz.jjbd_upload_hbz),
    url('^bddc_hbz$', views_hbz.bddc_hbz),
    url('^bddc_upload_hbz$', views_hbz.bddc_upload_hbz),
    url('^yqdx_list_export_hbz$', views_hbz.yqdx_list_export_hbz),
    url(r'^yqdx_mod_hbz$', views_hbz.yqdx_mod_hbz, name='yqdx_mod_hbz'),
    url(r'^yqdx_del_hbz$', views_hbz.yqdx_del_hbz, name='yqdx_del_hbz'),
    url(r'^yqdx_mod_db_hbz$', views_hbz.yqdx_mod_db_hbz, name='yqdx_mod_db_hbz'),

    url(r'^muban_upload_hbz$', views_hbz.muban_upload_hbz, name='muban_upload_hbz'),
    url(r'^plbz_hbz$', views_hbz.plbz_hbz, name='plbz_hbz'),
    url(r'^plbz_hbz_db$', views_hbz.plbz_hbz_db, name='plbz_hbz_db'),


]
