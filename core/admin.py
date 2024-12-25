
from django.http import HttpResponseForbidden


    

from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from .models import Directorate, Area, Mosque, UserRole

from django.db.utils import OperationalError



class AreaInline(admin.TabularInline):
    model = Area
    extra = 1

class MosqueInline(admin.TabularInline):
    
    model = Mosque
    extra = 1



class DirectorateAdmin(admin.ModelAdmin):
    list_display = ('name', 'supervisor','manager')
    search_fields = ('name', 'supervisor__username', 'manager')
    inlines = [AreaInline]
    
    

class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'directorate')
    inlines = [MosqueInline]



    
    



class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'role')
   

    
    



admin.site.register(Directorate, DirectorateAdmin)

admin.site.register(Area, AreaAdmin)


admin.site.register(UserRole, UserRoleAdmin)




# تسجيل النماذج في لوحة الإدارة


# إنشاء المجموعات والأذونات
def setup_groups_permissions():
    try:
        # admin_group, created = Group.objects.get_or_create(name='Admin')
        manager_group, created = Group.objects.get_or_create(name='Manager')
        supervisor_group, created = Group.objects.get_or_create(name='Directorate Supervisor')

        content_type = ContentType.objects.get_for_model(Mosque)

        supervisor_permissions = [
            Permission.objects.get_or_create(codename='add_mosque', name='Can add mosque', content_type=content_type)[0],
            Permission.objects.get_or_create(codename='change_mosque', name='Can change mosque', content_type=content_type)[0],
            Permission.objects.get_or_create(codename='delete_mosque', name='Can delete mosque', content_type=content_type)[0],
        ]

        supervisor_group.permissions.set(supervisor_permissions)
    except OperationalError:
        print("Migrations are not applied yet. Skipping setup_groups_permissions.")


# setup_groups_permissions()





class DirectorateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_supervisor')

    def get_supervisor(self, obj):
        # الحصول على المشرف من UserRole المرتبط بالمديرية
        user_roles = UserRole.objects.filter(directorate=obj, role='directorate_supervisor')
        if user_roles.exists():
            return ", ".join([user_role.user.username for user_role in user_roles])
        return "No Supervisor"

    get_supervisor.short_description = 'Supervisor'

# تسجيل النموذج فقط إذا لم يكن مسجلًا بالفعل
if not admin.site.is_registered(Directorate):
    admin.site.register(Directorate, DirectorateAdmin)



# إلغاء تسجيل النموذج إذا كان مسجلاً بالفعل
try:
    admin.site.unregister(Mosque)
except admin.sites.NotRegistered:
    pass

class MosqueAdmin(admin.ModelAdmin):
    list_display = ('name', 'area', 'mosque_type', 'womens_prayer_area', 'quran_school', 'islamic_center', 'has_awqaf', 'commercial_units', 'houses', 'farms', 'rental_apartments', 'lands', 'wells', 'khatib_name', 'khatib_phone', 'khatib_whatsapp', 'imam_name', 'imam_phone', 'imam_whatsapp', 'classification')
    list_filter = ('area', 'has_awqaf', 'classification')
    search_fields = ('name', 'area', 'khatib_name', 'imam_name')
    ordering = ('name',)

    def get_queryset(self, request):
        user_role = UserRole.objects.get(user=request.user)
        if user_role.role == 'directorate_supervisor':
            return Mosque.objects.none()
        return super().get_queryset(request)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        try:
            user_role = UserRole.objects.get(user=request.user)
            if user_role.role == 'directorate_supervisor':
                # حجب الحقل عن مشرف المديرية
                form.base_fields.pop('classification', None)
        except UserRole.DoesNotExist:
            pass

        return form

# تسجيل النموذج
admin.site.register(Mosque, MosqueAdmin)
