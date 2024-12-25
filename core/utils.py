from django.contrib.auth.models import User, Group

def assign_user_to_group(username, group_name):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, password='defaultpassword')
    group = Group.objects.get(name=group_name)
    user.groups.add(group)
    user.is_superuser = True  # يمكنك تعيين صلاحيات المستخدم هنا إذا لزم الأمر
    user.is_staff = True
    user.save()

# استدعاء الدالة لإنشاء المستخدم الرئيسي إذا لم يكن موجودًا
assign_user_to_group('example_user', 'Admin')


# utils.py أو في مكان مناسب آخر
from .models import ActivityLog

def get_recent_activities():
    return ActivityLog.objects.order_by('-timestamp')[:10]
