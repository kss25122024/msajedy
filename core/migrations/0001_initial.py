# Generated by Django 4.1.13 on 2024-12-22 21:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('directorate_name', models.CharField(max_length=100)),
                ('supervisor_name', models.CharField(max_length=100)),
                ('operation_type', models.CharField(choices=[('add', 'إضافة'), ('delete', 'حذف')], max_length=10)),
                ('area_name', models.CharField(max_length=100)),
                ('mosque_name', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Directorate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='directorates', to=settings.AUTH_USER_MODEL)),
                ('supervisor', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='supervised_directorate', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('manager', 'Manager'), ('directorate_supervisor', 'Directorate Supervisor')], max_length=150)),
                ('directorate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supervisors', to='core.directorate')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation_type', models.CharField(choices=[('اضافة_منطقة', 'إضافة منطقة'), ('تعديل_منطقة', 'تعديل منطقة'), ('حذف_منطقة', 'حذف منطقة'), ('اضافة_مسجد', 'إضافة مسجد'), ('تعديل_مسجد', 'تعديل مسجد'), ('حذف_مسجد', 'حذف مسجد')], max_length=120)),
                ('entity_name', models.CharField(max_length=100)),
                ('entity_id', models.IntegerField(default=1)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('shown', models.BooleanField(default=False)),
                ('is_old', models.BooleanField(default=False)),
                ('original_name', models.CharField(blank=True, max_length=255, null=True)),
                ('original_data', models.JSONField(blank=True, null=True)),
                ('processed', models.BooleanField(default=False)),
                ('approved', models.BooleanField(default=False)),
                ('supervisor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Mosque',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('mosque_type', models.CharField(choices=[('جمعة', 'جمعة'), ('جماعة', 'جماعة')], default='default_type', max_length=50)),
                ('womens_prayer_area', models.BooleanField(default=False)),
                ('quran_school', models.BooleanField(default=False)),
                ('islamic_center', models.BooleanField(default=False)),
                ('has_awqaf', models.BooleanField(default=False)),
                ('commercial_units', models.IntegerField(blank=True, null=True)),
                ('houses', models.IntegerField(blank=True, null=True)),
                ('farms', models.IntegerField(blank=True, null=True)),
                ('rental_apartments', models.IntegerField(blank=True, null=True)),
                ('lands', models.IntegerField(blank=True, null=True)),
                ('wells', models.IntegerField(blank=True, null=True)),
                ('khatib_name', models.CharField(default='text', max_length=100)),
                ('khatib_phone', models.IntegerField(blank=True, null=True)),
                ('khatib_whatsapp', models.IntegerField(blank=True, null=True)),
                ('imam_name', models.CharField(default='text', max_length=100)),
                ('imam_phone', models.IntegerField(blank=True, null=True)),
                ('imam_whatsapp', models.IntegerField(blank=True, null=True)),
                ('classification', models.CharField(choices=[('اصلاح', 'اصلاح'), ('تبليغ', 'تبليغ'), ('رشاد', 'رشاد'), ('رابطة', 'رابطة'), ('حكمة', 'حكمة'), ('احسان', 'احسان'), ('الحجوري', 'الحجوري'), ('محمد الامام', 'محمد الامام'), ('مستقل', 'مستقل'), ('أخرى', 'أخرى')], default='default_classification', max_length=100)),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mosques', to='core.area')),
            ],
        ),
        migrations.CreateModel(
            name='ManagerDirectorate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('directorate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.directorate')),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='area',
            name='directorate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='areas', to='core.directorate'),
        ),
    ]
