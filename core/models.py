from django.db import models
from django.utils import timezone


from django.contrib.auth.models import User



   


class ActivityLog(models.Model):
    directorate_name = models.CharField(max_length=100)
    supervisor_name = models.CharField(max_length=100)
    operation_type = models.CharField(max_length=10, choices=[('add', 'إضافة'), ('delete', 'حذف')])
    area_name = models.CharField(max_length=100)
    mosque_name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)



class Directorate(models.Model):
    name = models.CharField(max_length=100)
    manager = models.ForeignKey(User, related_name='directorates', on_delete=models.CASCADE)
    supervisor = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_directorate')
    def __str__(self):
        return self.name

USER_ROLES = (
    ('admin', 'Admin'),
    ('manager', 'Manager'),
    ('directorate_supervisor', 'Directorate Supervisor'),
)

class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=22, choices=USER_ROLES)
    directorate = models.ForeignKey(Directorate, related_name='supervisors', on_delete=models.CASCADE, null=True, blank=True)



class ManagerDirectorate(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    directorate = models.ForeignKey(Directorate, on_delete=models.CASCADE)

class Area(models.Model):
    name = models.CharField(max_length=255)
    directorate = models.ForeignKey(Directorate, on_delete=models.CASCADE, related_name='areas')
    
    

    def __str__(self):
        return f"{self.name} - {self.directorate.name}"














class Mosque(models.Model):
    name = models.CharField(max_length=100 )
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='mosques')
   # directorate = models.ForeignKey(Directorate, on_delete=models.CASCADE )
    mosque_type = models.CharField(max_length=50, choices=[('جمعة', 'جمعة'), ('جماعة', 'جماعة')], default="default_type")
    womens_prayer_area = models.BooleanField(default=False)  # مصلى النساء
    quran_school = models.BooleanField(default=False)  # مدرسة تحفيظ
    islamic_center = models.BooleanField(default=False)  # مركز علوم شرعية
    has_awqaf = models.BooleanField(default=False) #هل للجامع أوقاف 
    commercial_units = models.IntegerField(null=True, blank=True)  # عدد المحلات التجارية
    houses = models.IntegerField(null=True, blank=True)  # عدد البيوت
    farms = models.IntegerField(null=True, blank=True)  # عدد المزارع
    rental_apartments = models.IntegerField(null=True, blank=True)  # عدد الشقق الإيجار
    lands = models.IntegerField(null=True, blank=True)  # عدد الأراضي
    wells = models.IntegerField(null=True, blank=True)  # عدد الآبار
    khatib_name = models.CharField(max_length=100, default="text")
    khatib_phone = models.IntegerField(null=True, blank=True)
    khatib_whatsapp = models.IntegerField(null=True, blank=True)
    imam_name = models.CharField(max_length=100, default="text")
    imam_phone = models.IntegerField(null=True, blank=True)
    imam_whatsapp = models.IntegerField(null=True, blank=True)
    classification = models.CharField(max_length=100,  choices=[
        ('ص1', 'ص1'), ('ط2', 'ط2 '), (' 3س', ' 3س'), (' 4م', ' 4م'), ('ج5 ', ' ج5'),
        ('ك6 ', ' ك6'), (' ش7', 'ش7 '), (' ث8 ', '8ث '), (' 9ت', ' 9ت'), (' 10ب', '10ب '), ('ف11 ', '11ف')
    ],default="  غير مصنف")
    
    def save(self, *args, **kwargs):
        if not self.has_awqaf:
            self.commercial_units = None
            self.houses = None
            self.farms = None
            self.rental_apartments = None
            self.lands= None
            self.wells= None
        super().save(*args, **kwargs)
    
    
    def __str__(self):
        return self.name




USER_ROLES = (
    ('admin', 'Admin'),
    ('manager', 'Manager'),
    ('directorate_supervisor', 'Directorate Supervisor'),
)


class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=150, choices=(('admin', 'Admin'), ('manager', 'Manager'), ('directorate_supervisor', 'Directorate Supervisor')))
    directorate = models.ForeignKey(Directorate, related_name='supervisors', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role} - {self.get_role_display()}"




class Operation(models.Model):
    OPERATION_TYPES = [
        ('اضافة_منطقة', 'إضافة منطقة'),
        ('تعديل_منطقة', 'تعديل منطقة'),
        ('حذف_منطقة', 'حذف منطقة'),
        ('اضافة_مسجد', 'إضافة مسجد'),
        ('تعديل_مسجد', 'تعديل مسجد'),
        ('حذف_مسجد', 'حذف مسجد'),
    ]

    supervisor = models.ForeignKey(User, on_delete=models.CASCADE)
    operation_type = models.CharField(max_length=120, choices=OPERATION_TYPES)
    entity_name = models.CharField(max_length=100)
    entity_id = models.IntegerField(default=1)  # تأكد من تحديد القيمة الافتراضية إذا لم تكن محددة
    date = models.DateTimeField(auto_now_add=True)
    shown = models.BooleanField(default=False)  # الحقل الجديد لتتبع ما إذا كانت العملية قد عُرضت
    is_old = models.BooleanField(default=False)  # الحقل الجديد لتتبع ما إذا كانت العملية قديمة
    original_name = models.CharField(max_length=255, null=True, blank=True)  # إضافة حقل لتخزين البيانات الأصلية
    original_data = models.JSONField(null=True, blank=True)  # حقل لتخزين البيانات الأصلية
    processed = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.supervisor.username} - {self.operation_type} - {self.entity_name}"
    

