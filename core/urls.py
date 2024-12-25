from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import custom_login_view, home
from .views import custom_login_view, directorate_supervisor_view, manager_view, supervisor_view, mosque_detail_view
from .views import directorate_supervisor_view, add_area, add_mosque

from .views import directorate_supervisor_view, add_area, add_mosque, get_mosques

from .views import show_statistics, export_statistics_pdf




# urls.py

from .views import export_directorate_data

from django.contrib.auth.views import LogoutView







urlpatterns = [
    path('',views.home,name='home'),
    path('login/', custom_login_view, name='login'),
    path('directorate_supervisor/', directorate_supervisor_view, name='directorate_supervisor_page'),
    path('delete_area/', views.delete_area, name='delete_area'),
    
    path('logout/', views.custom_logout_view, name='logout'),
    
    path('export_directorate_data/', export_directorate_data, name='export_directorate_data'),
    path('manager/', views.manager_page, name='manager_page'),
    path('get_mosques/<int:area_id>/', get_mosques, name='get_mosques'),
   # path('get_mosques/<int:area_id>/', views.get_mosques, name='get_mosques'),
   
    path('export_directorate_data/<int:directorate_id>/', views.export_directorate_data, name='export_directorate_data'),
   
    path('areas/', views.area_list, name='area_list'),
    path('mosques/<int:area_id>/', views.mosque_list, name='mosque_list'),
    path('mosque/<int:mosque_id>/', views.mosque_detail, name='mosque_detail'), 
   
    path('edit_mosque/', views.edit_mosque, name='edit_mosque'),
    path('update_mosque/<int:mosque_id>/', views.update_mosque, name='update_mosque'),
    path('delete_mosque/', views.delete_mosque, name='delete_mosque'),
    path('confirm_delete_mosque/<int:mosque_id>/', views.confirm_delete_mosque, name='confirm_delete_mosque'),
    
    #path('edit_area/<int:area_id>/', views.edit_area, name='edit_area'),  # تحديث المسار لتعديل منطقة

    path('update_area/<int:area_id>/', views.update_area, name='update_area'),
    path('supervisor/', views.supervisor_view, name='supervisor_view'),

    path('manager/', manager_view, name='manager_page'),
    path('supervisor/', supervisor_view, name='supervisor_page'),
      path('get_areas/<int:directorate_id>/', views.get_areas, name='get_areas'),
    path('directorate_supervisor/', views.directorate_supervisor_view, name='directorate_supervisor'),
    
    # path('get_mosque_details/<int:mosque_id>/', views.get_mosque_details, name='get_mosque_details'),
    path('get_mosque_details/<int:mosque_id>/', views.get_mosque_details, name='get_mosque_details'),
   #  path('add_new_area/',views.add_area, name='add_new_area'),
    path('add_area/',views.add_area, name='add_area'),
    path('add_mosque/', add_mosque, name='add_mosque'),
   # path('export/<str:export_type>/', export_data, name='export_data'),
   
   # path('add_area/', add_area, name='add_area'),
   # path('add_directorate/', add_directorate, name='add_directorate'),
    # أضف مسارات أخرى إذا كانت موجودة
    path('show_statistics/', views.show_statistics, name='show_statistics'),  # أضف هذا المسار
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('manage_directorates/', views.manage_directorates, name='manage_directorates'),
    path('new_operations/', views.new_operations, name='new_operations'), 
    path('add_directorate/', views.add_directorate, name='add_directorate'),
    path('edit_directorate/', views.edit_directorate, name='edit_directorate'),
    path('delete_directorate/', views.delete_directorate, name='delete_directorate'), 
    path('edit_area/<int:area_id>/', views.edit_area, name='edit_area'),
    path('choose_area_to_edit/', views.choose_area_to_edit, name='choose_area_to_edit'),
    path('choose_area_to_delete/', views.choose_area_to_delete, name='choose_area_to_delete'),
    path('delete_area_form/<int:area_id>/', views.delete_area_form, name='delete_area_form'),
    path('choose_area_to_add_mosque/', views.choose_area_to_add_mosque, name='choose_area_to_add_mosque'),
    path('add_mosque_form/<int:area_id>/', views.add_mosque_form, name='add_mosque_form'),
   
    path('choose_mosque_to_edit/', views.choose_mosque_to_edit, name='choose_mosque_to_edit'),
    path('edit_mosque_form/<int:mosque_id>/', views.edit_mosque_form, name='edit_mosque_form'),
 
    path('choose_mosque_to_delete/', views.choose_mosque_to_delete, name='choose_mosque_to_delete'),
    path('delete_mosque_confirm/<int:mosque_id>/', views.delete_mosque_confirm, name='delete_mosque_confirm'),
    path('approve_operation/<int:operation_id>/', views.approve_operation, name='approve_operation'),
    #path('edit_operation/<int:operation_id>/', views.edit_operation, name='edit_operation'),
    path('delete_operation/<int:operation_id>/', views.delete_operation, name='delete_operation'),
    path('export_statistics_pdf/', export_statistics_pdf, name='export_statistics_pdf'),
    path('search/', views.search, name='search'),
    path('add_user/', views.add_user, name='add_user'),
    path('user_details/<int:user_id>/', views.user_details, name='user_details'),
    path('user_details/<int:user_id>/', views.user_details, name='user_details'),
    path('save_user_details/<int:user_id>/', views.user_details, name='save_user_details'),  # تم تحديث الرابط
    # مسارات أخرى...
    
]


