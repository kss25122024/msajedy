
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse,HttpResponseForbidden, JsonResponse, HttpResponseNotFound
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .models import Area, UserRole, User, Directorate, Operation, Mosque
from .forms import MosqueForm, AreaForm, DirectorateForm
from django.db import IntegrityError
from django.contrib.auth.models import Group  # إضافة الاستيراد لمجموعات المستخدمين
import matplotlib
matplotlib.use('Agg')  # تعيين محرك الرسم غير التفاعلي
import matplotlib.pyplot as plt
import io
import base64
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import utils
import pandas as pd
from django.contrib.auth.models import User
from django.db.models import F  
from django.views.decorators.csrf import csrf_exempt
from .utils import assign_user_to_group  # قم باستيراد الدالة من utils.py
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
import csv
from django.contrib import messages
from django.contrib.auth import logout
import json
import matplotlib.pyplot as plt
import io
import urllib, base64




def custom_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                user_role = UserRole.objects.get(user=user)
                if user_role.role == 'directorate_supervisor':
                    return redirect('directorate_supervisor_page')
                elif user_role.role == 'manager':
                    return redirect('manager_page')
                elif user_role.role == 'supervisor':
                    return redirect('supervisor_page')
                elif user_role.role == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})





def mosque_detail_view(request, mosque_id):
    mosque = get_object_or_404(Mosque, id=mosque_id)
    context = {
        'mosque': mosque,
    }
    return render(request, 'registration/mosque_detail.html', context)




def home(request):

   return render(request,'core/home.html')






def get_mosques(request, area_id):
    mosques = Mosque.objects.filter(area__id=area_id).values('id', 'name')
    mosques_list = list(mosques)
    return JsonResponse({'mosques': mosques_list})




def area_list(request):
    areas = Area.objects.all()
    return JsonResponse(list(areas.values()), safe=False)


def mosque_list(request, area_id):
    mosques = Mosque.objects.filter(area_id=area_id)
    return JsonResponse(list(mosques.values()), safe=False)



def mosque_detail(request, mosque_id):
    mosque = get_object_or_404(Mosque, id=mosque_id)
    return JsonResponse({
        'name': mosque.name,
        'mosque_type': mosque.mosque_type,
        'womens_prayer_area': mosque.womens_prayer_area,
        'quran_school': mosque.quran_school,
        'islamic_center': mosque.islamic_center,
        'has_awqaf': mosque.has_awqaf,
        'commercial_units': mosque.commercial_units,
        'houses': mosque.houses,
        'farms': mosque.farms,
        'rental_apartments': mosque.rental_apartments,
        'lands': mosque.lands,
        'wells': mosque.wells,
        'khatib_name': mosque.khatib_name,
        'khatib_phone': mosque.khatib_phone,
        'khatib_whatsapp': mosque.khatib_whatsapp,
        'imam_name': mosque.imam_name,
        'imam_phone': mosque.imam_phone,
        'imam_whatsapp': mosque.imam_whatsapp,
    })
 





@csrf_exempt
def update_area(request, area_id):
    if request.method == 'POST':
        area = get_object_or_404(Area, id=area_id)
        original_name = area.name  # حفظ الاسم الأصلي
        new_name = request.POST.get('name')
        if new_name:
            area.name = new_name
            area.save()

            # تسجيل العملية الجديدة مع حفظ البيانات الأصلية
            Operation.objects.create(
                supervisor=request.user,
                operation_type='تعديل_منطقة',
                entity_name=area.name,
                entity_id=area.id,
                original_data=json.dumps({'name': original_name})  # حفظ البيانات الأصلية
            )

            return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)







def supervisor_view(request):
    return render(request, 'registration/supervisor.html')



    
    user_role = UserRole.objects.get(user=request.user)
    if user_role.role != 'directorate_supervisor':
        data['classification'] = mosque.classification
    return JsonResponse(data)


@login_required
def add_area(request):
    user = request.user
    try:
        user_role = UserRole.objects.get(user=user)
    except UserRole.DoesNotExist:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")
    
    if user_role.role not in ['admin', 'manager', 'directorate_supervisor']:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")
    
    if user_role.role == 'directorate_supervisor':
        user_directorate = get_object_or_404(Directorate, supervisor=request.user)
        directorates = Directorate.objects.filter(id=user_directorate.id)
    else:
        directorates = Directorate.objects.all()

    if request.method == 'POST':
        form = AreaForm(request.POST)
        if form.is_valid():
            area = get_object_or_404(Area, id=form.cleaned_data['id']) if 'id' in form.cleaned_data else None
            original_data = json.dumps({'name': area.name}) if area else None  # حفظ البيانات الأصلية

            new_area = form.save(commit=False)
            if user_role.role == 'directorate_supervisor':
                new_area.directorate = user_directorate
            else:
                selected_directorate_id = request.POST.get('directorate')
                selected_directorate = get_object_or_404(Directorate, id=selected_directorate_id)
                new_area.directorate = selected_directorate
            new_area.save()

            # تسجيل العملية الجديدة
            Operation.objects.create(
                supervisor=request.user,
                operation_type='إضافة_منطقة' if not area else 'تعديل_منطقة',
                entity_name=new_area.name,
                entity_id=new_area.id,
                original_data=original_data  # حفظ البيانات الأصلية
            )

            if user_role.role == 'directorate_supervisor':
                return redirect('directorate_supervisor_page')
            elif user_role.role == 'manager':
                return redirect('manager_page')
            elif user_role.role == 'admin':
                return redirect('admin_dashboard')
    else:
        form = AreaForm()
    
    if user_role.role == 'directorate_supervisor':
        back_url = 'directorate_supervisor_page'
    elif user_role.role == 'manager':
        back_url = 'manager_page'
    elif user_role.role == 'admin':
        back_url = 'admin_dashboard'
    else:
        back_url = 'home'  # مسار افتراضي
    
    return render(request, 'core/add_area.html', {
        'form': form,
        'directorates': directorates,
        'user_role': user_role,
        'back_url': back_url
    })







@login_required
def directorate_supervisor_page(request):
    user_directorate = get_object_or_404(Directorate, supervisor=request.user)
    areas = Area.objects.filter(directorate=user_directorate)
    return render(request, 'core/directorate_supervisor_page.html', {'areas': areas})




@login_required
def delete_area(request):
    user_directorate = get_object_or_404(Directorate, supervisor=request.user)
    areas = Area.objects.filter(directorate=user_directorate)

    if request.method == 'POST':
        areas_to_delete = request.POST.getlist('areas')
        
        # تخزين معلومات المناطق التي سيتم حذفها قبل الحذف
        areas_info = Area.objects.filter(id__in=areas_to_delete, directorate=user_directorate)

        # تسجيل العمليات الجديدة لكل منطقة تم حذفها
        for area in areas_info:
            Operation.objects.create(
                supervisor=request.user,
                operation_type='حذف_منطقة',
                entity_name=area.name,
                entity_id=area.id,
                shown=False,  # تعيين العملية كغير معروضة
                original_data=json.dumps({'name': area.name, 'directorate': area.directorate.id})  # حفظ البيانات الأصلية
            )

        # حذف المناطق
        areas_info.delete()

        return redirect('directorate_supervisor_page')  # تعديل إعادة التوجيه لصفحة العمليات الجديدة
    
    return render(request, 'core/delete_area.html', {'areas': areas, 'directorate': user_directorate})





@login_required
def directorate_supervisor_page(request):
    user_directorate = get_object_or_404(Directorate, supervisor=request.user)
    areas = Area.objects.filter(directorate=user_directorate)
    return render(request, 'registration/directorate_supervisor_page.html', {'areas': areas})




@login_required
def add_mosque(request):
    if request.method == 'POST':
        area_id = request.POST.get('area')
        name = request.POST.get('mosqueName')
        mosque_type = request.POST.get('mosqueType')
        womens_prayer_area = request.POST.get('womensPrayerArea', False) == 'on'
        quran_school = request.POST.get('quranSchool', False) == 'on'
        islamic_center = request.POST.get('islamicCenter', False) == 'on'
        has_awqaf = request.POST.get('hasAwqaf', False) == 'on'
        commercial_units = request.POST.get('commercialUnits')
        houses = request.POST.get('houses')
        farms = request.POST.get('farms')
        rental_apartments = request.POST.get('rentalApartments')
        lands = request.POST.get('lands')
        wells = request.POST.get('wells')
        khatib_name = request.POST.get('khatibName')
        khatib_phone = request.POST.get('khatibPhone')
        khatib_whatsapp = request.POST.get('khatibWhatsapp')
        imam_name = request.POST.get('imamName')
        imam_phone = request.POST.get('imamPhone')
        imam_whatsapp = request.POST.get('imamWhatsapp')

        area = get_object_or_404(Area, id=area_id)

        new_mosque = Mosque.objects.create(
            name=name,
            area=area,
            mosque_type=mosque_type,
            womens_prayer_area=womens_prayer_area,
            quran_school=quran_school,
            islamic_center=islamic_center,
            has_awqaf=has_awqaf,
            commercial_units=commercial_units,
            houses=houses,
            farms=farms,
            rental_apartments=rental_apartments,
            lands=lands,
            wells=wells,
            khatib_name=khatib_name,
            khatib_phone=khatib_phone,
            khatib_whatsapp=khatib_whatsapp,
            imam_name=imam_name,
            imam_phone=imam_phone,
            imam_whatsapp=imam_whatsapp
        )

        # تسجيل العملية الجديدة
        Operation.objects.create(
            supervisor=request.user,
            operation_type='إضافة_مسجد',
            entity_name=new_mosque.name,
            entity_id=new_mosque.id,
            shown=False,  # تعيين العملية كغير معروضة
            original_data=json.dumps({
                'name': name,
                'area': area_id,
                'mosque_type': mosque_type,
                'womens_prayer_area': womens_prayer_area,
                'quran_school': quran_school,
                'islamic_center': islamic_center,
                'has_awqaf': has_awqaf,
                'commercial_units': commercial_units,
                'houses': houses,
                'farms': farms,
                'rental_apartments': rental_apartments,
                'lands': lands,
                'wells': wells,
                'khatib_name': khatib_name,
                'khatib_phone': khatib_phone,
                'khatib_whatsapp': khatib_whatsapp,
                'imam_name': imam_name,
                'imam_phone': imam_phone,
                'imam_whatsapp': imam_whatsapp
            })  # حفظ البيانات الأصلية
        )

        messages.success(request, 'تم إضافة المسجد بنجاح!')
        return redirect('directorate_supervisor_page')

    return render(request, 'registration/add_mosque.html')




@login_required
def edit_mosque(request):
    user_directorate = get_object_or_404(Directorate, supervisor=request.user)
    mosques = Mosque.objects.filter(area__directorate=user_directorate)

    if request.method == 'POST':
        mosque_id = request.POST.get('mosque_id')
        return redirect('update_mosque', mosque_id=mosque_id)

    return render(request, 'core/edit_mosque.html', {'mosques': mosques, 'directorate': user_directorate})

@login_required
def update_mosque(request, mosque_id):
    mosque = get_object_or_404(Mosque, id=mosque_id)

    if request.method == 'POST':
        form = MosqueForm(request.POST, instance=mosque)
        if form.is_valid():
            original_data = {
                'name': mosque.name,
                'area': mosque.area.id,
                'mosque_type': mosque.mosque_type,
                'womens_prayer_area': mosque.womens_prayer_area,
                'quran_school': mosque.quran_school,
                'islamic_center': mosque.islamic_center,
                'has_awqaf': mosque.has_awqaf,
                'commercial_units': mosque.commercial_units,
                'houses': mosque.houses,
                'farms': mosque.farms,
                'rental_apartments': mosque.rental_apartments,
                'lands': mosque.lands,
                'wells': mosque.wells,
                'khatib_name': mosque.khatib_name,
                'khatib_phone': mosque.khatib_phone,
                'khatib_whatsapp': mosque.khatib_whatsapp,
                'imam_name': mosque.imam_name,
                'imam_phone': mosque.imam_phone,
                'imam_whatsapp': mosque.imam_whatsapp
            }

            form.save()

            # تسجيل العملية الجديدة
            Operation.objects.create(
                supervisor=request.user,
                operation_type='تعديل_مسجد',
                entity_name=mosque.name,
                entity_id=mosque.id,
                shown=False,  # تعيين العملية كغير معروضة
                original_data=json.dumps(original_data)  # حفظ البيانات الأصلية
            )

            return redirect('directorate_supervisor_page')
    else:
        form = MosqueForm(instance=mosque)

    return render(request, 'core/update_mosque.html', {'form': form, 'mosque': mosque})







@login_required
def custom_logout_view(request):
    logout(request)
    return redirect('home')





@login_required
def delete_mosque(request):
    user = request.user
    user_role = UserRole.objects.get(user=user)
    
    if user_role.role != 'directorate_supervisor':
        return redirect('home')
    
    directorate = get_object_or_404(Directorate, supervisor=user)
    areas = directorate.areas.all()
    mosques = Mosque.objects.filter(area__in=areas)

    if request.method == 'POST':
        selected_mosque_id = request.POST.get('selected_mosque')
        if selected_mosque_id:
            return redirect('confirm_delete_mosque', mosque_id=selected_mosque_id)

    return render(request, 'core/delete_mosque.html', {'mosques': mosques, 'directorate': directorate})



@login_required
def confirm_delete_mosque(request, mosque_id):
    mosque = get_object_or_404(Mosque, id=mosque_id)

    if request.method == 'POST':
        if 'delete' in request.POST:
            original_data = {
                'name': mosque.name,
                'area': mosque.area.id,
                'mosque_type': mosque.mosque_type,
                'womens_prayer_area': mosque.womens_prayer_area,
                'quran_school': mosque.quran_school,
                'islamic_center': mosque.islamic_center,
                'has_awqaf': mosque.has_awqaf,
                'commercial_units': mosque.commercial_units,
                'houses': mosque.houses,
                'farms': mosque.farms,
                'rental_apartments': mosque.rental_apartments,
                'lands': mosque.lands,
                'wells': mosque.wells,
                'khatib_name': mosque.khatib_name,
                'khatib_phone': mosque.khatib_phone,
                'khatib_whatsapp': mosque.khatib_whatsapp,
                'imam_name': mosque.imam_name,
                'imam_phone': mosque.imam_phone,
                'imam_whatsapp': mosque.imam_whatsapp
            }

            mosque.delete()

            # تسجيل العملية الجديدة
            Operation.objects.create(
                supervisor=request.user,
                operation_type='حذف_مسجد',
                entity_name=mosque.name,
                entity_id=mosque_id,
                shown=False,  # تعيين العملية كغير معروضة
                original_data=json.dumps(original_data)  # حفظ البيانات الأصلية
            )

            return redirect('directorate_supervisor_page')
        elif 'cancel' in request.POST:
            return redirect('delete_mosque')

    return render(request, 'core/confirm_delete_mosque.html', {'mosque': mosque})








@login_required
def manager_view(request):
    return render(request, 'registration/manager.html')

@login_required
def supervisor_view(request):
    return render(request, 'registration/supervisor.html')





def some_view(request):
    # يمكنك الآن استخدام الدالة كما تريد
    assign_user_to_group('example_user', 'Admin')
    return render(request, 'some_template.html')

from .models import ActivityLog

def get_recent_activities():
    return ActivityLog.objects.order_by('-timestamp')[:10]






@login_required
def manager_page(request):
    user = request.user
    try:
        user_role = UserRole.objects.get(user=user)
    except UserRole.DoesNotExist:
        raise Http404("No UserRole matches the given query.")

    if user_role.role != 'manager':
        return redirect('home')

    directorates = Directorate.objects.filter(manager=user)

    return render(request, 'core/manager_page.html', {
        'directorates': directorates,
        'user': user
    })




@login_required
def directorate_supervisor_view(request):
    user = request.user
    try:
        user_role = UserRole.objects.get(user=user)
    except UserRole.DoesNotExist:
        raise Http404("No UserRole matches the given query.")
    
    if user_role.role != 'directorate_supervisor':
        return redirect('home')
    
    # الوصول إلى المديرية والمناطق المرتبطة بها من خلال user_role
    directorate = user_role.directorate
    areas = Area.objects.filter(directorate=directorate)

    return render(request, 'registration/directorate_supervisor.html', {
        'directorate': directorate,
        'areas': areas,
        'user': user
    })

    
    
@login_required
def directorate_supervisor_view(request):
    current_user = request.user
    user_role = get_object_or_404(UserRole, user=current_user)
    
    if user_role.directorate is None:
        # إذا لم يكن للمستخدم مديرية معينة، يمكنك التعامل مع هذا الحالة هنا
        return HttpResponse("لم يتم تعيين مديرية لهذا المستخدم")

    directorate = get_object_or_404(Directorate, id=user_role.directorate.id)

   
  
  
  




@login_required
def directorate_supervisor_view(request):
    user = request.user
    try:
        user_role = UserRole.objects.get(user=user)
    except UserRole.DoesNotExist:
        raise Http404("No UserRole matches the given query.")
    
    if user_role.role != 'directorate_supervisor':
        return redirect('home')
    
    # التحقق إذا كان هناك مديرية مرتبطة بالمشرف
    directorate = user_role.directorate
    if directorate is None:
        raise Http404("No Directorate assigned to this supervisor.")
    
    areas = Area.objects.filter(directorate=directorate)

    return render(request, 'registration/directorate_supervisor.html', {
        'directorate': directorate,
        'areas': areas,
        'user': user
    })


@login_required
def create_or_update_directorate(request, directorate_id=None):
    if directorate_id:
        directorate = get_object_or_404(Directorate, pk=directorate_id)
    else:
        directorate = None
    
    if request.method == 'POST':
        form = DirectorateForm(request.POST, instance=directorate)
        if form.is_valid():
            form.save()
            return redirect('directorate_supervisor')
    else:
        form = DirectorateForm(instance=directorate)
    
    return render(request, 'core/directorate_form.html', {'form': form})

  
  

@login_required
def get_areas(request, directorate_id):
    areas = Area.objects.filter(directorate_id=directorate_id).values('id', 'name')
    return JsonResponse({'areas': list(areas)})



@login_required
def get_areas(request, directorate_id):
    directorate = get_object_or_404(Directorate, pk=directorate_id)
    areas = Area.objects.filter(directorate=directorate).values('id', 'name')
    return JsonResponse({'areas': list(areas)})


@login_required
def get_mosques(request, area_id):
    area = get_object_or_404(Area, pk=area_id)
    mosques = Mosque.objects.filter(area=area).values('id', 'name')
    return JsonResponse({'mosques': list(mosques)})


@login_required
def get_mosque_details(request, mosque_id):
    mosque = get_object_or_404(Mosque, pk=mosque_id)
    data = {
                    'اسم المديرية': mosque.area.directorate.name,
            'اسم المنطقة': mosque.area.name,
            'اسم المسجد': mosque.name,
            'نوع الجامع': mosque.mosque_type,
            'مصلى النساء': 'نعم' if mosque.womens_prayer_area else 'لا',
            'مدرسة تحفيظ القرآن الكريم': 'نعم' if mosque.quran_school else 'لا',
            'مركز للعلوم الشرعية': 'نعم' if mosque.islamic_center else 'لا',
            'هل للجامع أوقاف': 'نعم' if mosque.has_awqaf else 'لا',
            'عدد المحلات التجارية': mosque.commercial_units if mosque.has_awqaf else '',
            'عدد البيوت': mosque.houses if mosque.has_awqaf else '',
            'عدد المزارع': mosque.farms if mosque.has_awqaf else '',
            'عدد الشقق المؤجرة': mosque.rental_apartments if mosque.has_awqaf else '',
            'عدد الأراضي': mosque.lands if mosque.has_awqaf else '',
            'عدد الآبار': mosque.wells if mosque.has_awqaf else '',
            'اسم الخطيب': mosque.khatib_name,
            'رقم هاتف الخطيب': mosque.khatib_phone,
            'رقم واتساب الخطيب': mosque.khatib_whatsapp,
            'اسم إمام المسجد': mosque.imam_name,
            'رقم هاتف إمام المسجد': mosque.imam_phone,
            'رقم واتساب إمام المسجد': mosque.imam_whatsapp,
            'المكون الدعوي': mosque.classification,
        
    }
    return JsonResponse(data)



@login_required
def admin_dashboard(request):
    admin_user = request.user
    directorates = Directorate.objects.all()
    areas = Area.objects.all()
    mosques = Mosque.objects.all()
    return render(request, 'core/admin_dashboard.html', {
        'admin_user': admin_user,
        'directorates': directorates,
        'areas': areas,
        'mosques': mosques
    })



@login_required
def manage_users(request):
    users = User.objects.all()
    return render(request, 'core/manage_users.html', {
        'users': users,
    })



@login_required
def manage_directorates(request):
    directorates = Directorate.objects.all()
    return render(request, 'core/manage_directorates.html', {
        'directorates': directorates,
    })








@login_required
def show_statistics(request):
    user_count = User.objects.count()
    directorate_count = Directorate.objects.count()
    area_count = Area.objects.count()
    mosque_count = Mosque.objects.count()

    # جمع تفاصيل المساجد
    mosque_details = {
        'types': {},
        'womens_prayer_area': 0,
        'quran_school': 0,
        'islamic_center': 0,
        'has_awqaf': 0,
        'commercial_units': 0,
        'houses': 0,
        'lands': 0,
        'farms': 0,
        'wells': 0,
        'classification': {}
    }

    mosques = Mosque.objects.all()
    for mosque in mosques:
        mosque_details['types'][mosque.mosque_type] = mosque_details['types'].get(mosque.mosque_type, 0) + 1
        if mosque.womens_prayer_area:
            mosque_details['womens_prayer_area'] += 1
        if mosque.quran_school:
            mosque_details['quran_school'] += 1
        if mosque.islamic_center:
            mosque_details['islamic_center'] += 1
        if mosque.has_awqaf:
            mosque_details['has_awqaf'] += 1
        mosque_details['commercial_units'] += mosque.commercial_units or 0
        mosque_details['houses'] += mosque.houses or 0
        mosque_details['lands'] += mosque.lands or 0
        mosque_details['farms'] += mosque.farms or 0
        mosque_details['wells'] += mosque.wells or 0
        mosque_details['classification'][mosque.classification] = mosque_details['classification'].get(mosque.classification, 0) + 1

    # جمع إحصائيات المديريات
    directorate_details = {}
    directorates = Directorate.objects.all()
    for directorate in directorates:
        areas = Area.objects.filter(directorate=directorate)
        mosques_in_directorate = Mosque.objects.filter(area__in=areas).count()
        directorate_details[directorate.name] = {
            'area_count': areas.count(),
            'mosque_count': mosques_in_directorate
        }

    # إعداد الخط Arial وضبط الاتجاه
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['axes.unicode_minus'] = False

    # إنشاء الرسوم البيانية
    charts = {}

    def create_pie_chart(labels, sizes):
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct=lambda p: '{:.1f}%'.format(p), startangle=90)
        ax.axis('equal')
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        return urllib.parse.quote(base64.b64encode(buf.read()))

    # الرسم البياني لأنواع المساجد
    charts['types'] = create_pie_chart(list(mosque_details['types'].keys()), list(mosque_details['types'].values()))

    # الرسم البياني لتصنيف المكون الدعوي
    charts['classification'] = create_pie_chart(list(mosque_details['classification'].keys()), list(mosque_details['classification'].values()))

    # الرسم البياني لتوزيع المساجد على المديريات
    charts['directorates'] = create_pie_chart(list(directorate_details.keys()), [details['mosque_count'] for details in directorate_details.values()])

    # الرسم البياني لأوقاف المسجد
    has_awqaf_labels = ['لديه أوقاف', 'لا يوجد أوقاف']
    has_awqaf_sizes = [mosque_details['has_awqaf'], mosque_count - mosque_details['has_awqaf']]
    charts['has_awqaf'] = create_pie_chart(has_awqaf_labels, has_awqaf_sizes)

    # الرسم البياني لمصلى النساء
    womens_prayer_area_labels = ['يوجد مصلى للنساء', 'لا يوجد مصلى للنساء']
    womens_prayer_area_sizes = [mosque_details['womens_prayer_area'], mosque_count - mosque_details['womens_prayer_area']]
    charts['womens_prayer_area'] = create_pie_chart(womens_prayer_area_labels, womens_prayer_area_sizes)

    # الرسم البياني لمدرسة تحفيظ القرآن
    quran_school_labels = ['يوجد مدرسة تحفيظ', 'لا يوجد مدرسة تحفيظ']
    quran_school_sizes = [mosque_details['quran_school'], mosque_count - mosque_details['quran_school']]
    charts['quran_school'] = create_pie_chart(quran_school_labels, quran_school_sizes)

    return render(request, 'core/show_statistics.html', {
        'user_count': user_count,
        'directorate_count': directorate_count,
        'area_count': area_count,
        'mosque_count': mosque_count,
        'mosque_details': mosque_details,
        'directorate_details': directorate_details,
        'charts': charts
    })


@login_required
def add_directorate(request):
    if not request.user.userrole.role == 'admin':
        return HttpResponseForbidden("لا يمكنك الوصول إلى هذه الصفحة.")
    
    if request.method == 'POST':
        form = DirectorateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_directorates')
    else:
        form = DirectorateForm()
    
    return render(request, 'core/add_directorate.html', {'form': form})



@login_required
def edit_directorate(request):
    if not request.user.userrole.role == 'admin':
        return HttpResponseForbidden("لا يمكنك الوصول إلى هذه الصفحة.")
    
    if request.method == 'POST' and 'select_directorate' in request.POST:
        directorate_id = request.POST.get('directorate_id')
        if not directorate_id:
            return render(request, 'core/edit_directorate.html', {
                'error': 'حدد المديرية التي تريد تعديلها.',
                'directorates': Directorate.objects.all()
            })
        
        directorate = get_object_or_404(Directorate, id=directorate_id)
        form = DirectorateForm(instance=directorate)
        return render(request, 'core/edit_directorate_form.html', {'form': form, 'directorate': directorate})

    if request.method == 'POST' and 'save_directorate' in request.POST:
        directorate_id = request.POST.get('directorate_id')
        directorate = get_object_or_404(Directorate, id=directorate_id)
        form = DirectorateForm(request.POST, instance=directorate)
        if form.is_valid():
            form.save()
            return redirect('manage_directorates')
    
    return render(request, 'core/edit_directorate.html', {
        'directorates': Directorate.objects.all()
    })



@login_required
def delete_directorate(request):
    if not request.user.userrole.role == 'admin':
        return HttpResponseForbidden("لا يمكنك الوصول إلى هذه الصفحة.")

    if request.method == 'POST':
        directorate_id = request.POST.get('directorate_id')
        if not directorate_id:
            return render(request, 'core/delete_directorate.html', {
                'error': 'حدد المديرية التي تريد حذفها.',
                'directorates': Directorate.objects.all()
            })
        
        directorate = get_object_or_404(Directorate, id=directorate_id)
        if 'confirm_delete' in request.POST:
            directorate.delete()
            return redirect('manage_directorates')

        return render(request, 'core/confirm_delete_directorate.html', {'directorate': directorate})

    return render(request, 'core/delete_directorate.html', {
        'directorates': Directorate.objects.all()
    })



@login_required
def delete_directorate(request):
    if not request.user.userrole.role == 'admin':
        return HttpResponseForbidden("لا يمكنك الوصول إلى هذه الصفحة.")

    if request.method == 'POST':
        directorate_id = request.POST.get('directorate_id')
        if not directorate_id:
            return render(request, 'core/delete_directorate.html', {
                'error': 'حدد المديرية التي تريد حذفها.',
                'directorates': Directorate.objects.all()
            })
        
        directorate = get_object_or_404(Directorate, id=directorate_id)
        if 'confirm_delete' in request.POST:
            directorate.delete()
            return redirect('manage_directorates')

        return render(request, 'core/confirm_delete_directorate.html', {'directorate': directorate})

    return render(request, 'core/delete_directorate.html', {
        'directorates': Directorate.objects.all()
    })



@login_required
def choose_area_to_edit(request):
    user = request.user
    try:
        user_role = UserRole.objects.get(user=user)
    except UserRole.DoesNotExist:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")
    
    if user_role.role == 'admin':
        areas = Area.objects.all()
    elif user_role.role == 'manager':
        directorates = Directorate.objects.filter(manager=user)
        areas = Area.objects.filter(directorate__in=directorates)
    elif user_role.role == 'directorate_supervisor':
        directorate = Directorate.objects.filter(supervisor=user)
        areas = Area.objects.filter(directorate=directorate)
    else:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")

    if request.method == 'POST':
        area_id = request.POST.get('area_id')
        if not area_id:
            return render(request, 'core/choose_area_to_edit.html', {
                'error': 'حدد المنطقة التي تريد تعديلها.',
                'areas': areas
            })
        
        return redirect('edit_area', area_id=area_id)

    return render(request, 'core/choose_area_to_edit.html', {'areas': areas})

@login_required
def edit_area(request, area_id):
    user = request.user
    area = get_object_or_404(Area, id=area_id)
    original_name = area.name  # حفظ الاسم الأصلي
    original_directorate = area.directorate.id  # حفظ المديرية الأصلية
    try:
        user_role = UserRole.objects.get(user=user)
    except UserRole.DoesNotExist:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")
    
    if user_role.role == 'manager' and area.directorate.manager != user:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة لتعديل هذه المنطقة.")
    elif user_role.role == 'directorate_supervisor' and area.directorate.supervisor != user:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة لتعديل هذه المنطقة.")
    
    if request.method == 'POST':
        form = AreaForm(request.POST, instance=area)
        if form.is_valid():
            original_data = {
                'name': area.name,
                'directorate': area.directorate.id,
            }

            form.save()


            # تسجيل العملية الجديدة مع حفظ البيانات الأصلية
            Operation.objects.create(
                supervisor=request.user,
                operation_type='تعديل_منطقة',
                entity_name=area.name,
                entity_id=area.id,
                original_data=json.dumps({
                    'name': original_name,
                    'directorate': original_directorate
                })  # حفظ البيانات الأصلية
            )
            if user_role.role == 'admin':
                return redirect('manage_directorates')
            elif user_role.role == 'manager':
                return redirect('manager_page')
            elif user_role.role == 'directorate_supervisor':
                return redirect('directorate_supervisor_page')
    else:
        form = AreaForm(instance=area)
    
    return render(request, 'core/edit_area_form.html', {'form': form, 'area': area})



@login_required
def choose_area_to_delete(request):
    user = request.user
    try:
        user_role = UserRole.objects.get(user=user)
    except UserRole.DoesNotExist:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")
    
    if user_role.role == 'admin':
        areas = Area.objects.all()
    elif user_role.role == 'manager':
        directorates = Directorate.objects.filter(manager=user)
        areas = Area.objects.filter(directorate__in=directorates)
    elif user_role.role == 'directorate_supervisor':
        directorate = Directorate.objects.filter(supervisor=user).first()
        areas = Area.objects.filter(directorate=directorate)
    else:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")

    if request.method == 'POST':
        area_id = request.POST.get('area_id')
        if not area_id:
            return render(request, 'core/choose_area_to_delete.html', {
                'error': 'حدد المنطقة التي تريد حذفها.',
                'areas': areas
            })
        
        return redirect('delete_area_form', area_id=area_id)

    return render(request, 'core/choose_area_to_delete.html', {'areas': areas})






@login_required
def delete_area_form(request, area_id):
    user = request.user
    area = get_object_or_404(Area, id=area_id)
    try:
        user_role = UserRole.objects.get(user=user)
        user_directorate = area.directorate  # تعريف user_directorate
    except UserRole.DoesNotExist:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")
    
    if user_role.role == 'manager' and area.directorate.manager != user:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة لحذف هذه المنطقة.")
    elif user_role.role == 'directorate_supervisor' and area.directorate.supervisor != user:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة لحذف هذه المنطقة.")
    
    if request.method == 'POST':
        area_to_delete = area.id  # تحديد معرف المنطقة للحذف

        # تخزين معلومات المنطقة التي سيتم حذفها قبل الحذف
        area_info = Area.objects.filter(id=area_to_delete, directorate=user_directorate).first()

        # تسجيل العملية الجديدة للمنطقة المحذوفة
        if area_info:
            Operation.objects.create(
                supervisor=request.user,
                operation_type='حذف_منطقة',
                entity_name=area_info.name,
                entity_id=area_info.id,
                shown=False,  # تعيين العملية كغير معروضة
                original_data=json.dumps({'name': area_info.name, 'directorate': area_info.directorate.id})  # حفظ البيانات الأصلية
            )

            # حذف المنطقة
            area_info.delete()

        if user_role.role == 'admin':
            return redirect('admin_dashboard')
        elif user_role.role == 'manager':
            return redirect('manager_page')
        elif user_role.role == 'directorate_supervisor':
            return redirect('directorate_supervisor_page')
    
    return render(request, 'core/delete_area_confirm.html', {'area': area, 'area_name': area.name})







@login_required
def choose_area_to_add_mosque(request):
    user = request.user
    try:
        user_role = UserRole.objects.get(user=user)
    except UserRole.DoesNotExist:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")
    
    if user_role.role == 'admin':
        areas = Area.objects.all()
    elif user_role.role == 'manager':
        directorates = Directorate.objects.filter(manager=user)
        areas = Area.objects.filter(directorate__in=directorates)
    elif user_role.role == 'directorate_supervisor':
        directorate = Directorate.objects.filter(supervisor=user)
        areas = Area.objects.filter(directorate=directorate)
    else:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")

    if request.method == 'POST':
        area_id = request.POST.get('area_id')
        if not area_id:
            return render(request, 'core/choose_area_to_add_mosque.html', {
                'error': 'حدد المنطقة التي تريد إضافة المسجد فيها.',
                'areas': areas
            })
        
        return redirect('add_mosque_form', area_id=area_id)

    return render(request, 'core/choose_area_to_add_mosque.html', {'areas': areas})




@login_required
def add_mosque_form(request, area_id):
    user = request.user
    try:
        user_role = UserRole.objects.get(user=user)
    except UserRole.DoesNotExist:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")
    
    area = Area.objects.get(id=area_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        mosque_type = request.POST.get('mosque_type')
        womens_prayer_area = request.POST.get('womens_prayer_area') == 'true'
        quran_school = request.POST.get('quran_school') == 'true'
        islamic_center = request.POST.get('islamic_center') == 'true'
        has_awqaf = request.POST.get('has_awqaf') == 'true'
        commercial_units = request.POST.get('commercial_units')
        houses = request.POST.get('houses')
        farms = request.POST.get('farms')
        rental_apartments = request.POST.get('rental_apartments')
        lands = request.POST.get('lands')
        wells = request.POST.get('wells')
        khatib_name = request.POST.get('khatib_name')
        khatib_phone = request.POST.get('khatib_phone')
        khatib_whatsapp = request.POST.get('khatib_whatsapp')
        imam_name = request.POST.get('imam_name')
        imam_phone = request.POST.get('imam_phone')
        imam_whatsapp = request.POST.get('imam_whatsapp')
        classification = request.POST.get('classification') if user_role.role in ['admin', 'manager'] else None

        new_mosque = Mosque.objects.create(
            name=name,
            mosque_type=mosque_type,
            womens_prayer_area=womens_prayer_area,
            quran_school=quran_school,
            islamic_center=islamic_center,
            has_awqaf=has_awqaf,
            commercial_units=commercial_units,
            houses=houses,
            farms=farms,
            rental_apartments=rental_apartments,
            lands=lands,
            wells=wells,
            khatib_name=khatib_name,
            khatib_phone=khatib_phone,
            khatib_whatsapp=khatib_whatsapp,
            imam_name=imam_name,
            imam_phone=imam_phone,
            imam_whatsapp=imam_whatsapp,
            classification=classification,
            area=area
        )

        # تسجيل العملية الجديدة
        Operation.objects.create(
            supervisor=user,
            operation_type='إضافة_مسجد',
            entity_name=new_mosque.name,
            entity_id=new_mosque.id
        )

        if user_role.role == 'admin':
            return redirect('manage_directorates')
        elif user_role.role == 'manager':
            return redirect('manager_page')
        elif user_role.role == 'directorate_supervisor':
            return redirect('directorate_supervisor_page')
        else:
            return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")

    return render(request, 'core/add_mosque_form.html', {'area': area, 'user_role': user_role})


@login_required
def choose_mosque_to_edit(request):
    user = request.user
    try:
        user_role = UserRole.objects.get(user=user)
    except UserRole.DoesNotExist:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")
    
    if user_role.role == 'admin':
        mosques = Mosque.objects.all()
    elif user_role.role == 'manager':
        directorates = Directorate.objects.filter(manager=user)
        areas = Area.objects.filter(directorate__in=directorates)
        mosques = Mosque.objects.filter(area__in=areas)
    elif user_role.role == 'directorate_supervisor':
        directorate = Directorate.objects.filter(supervisor=user).first()
        areas = Area.objects.filter(directorate=directorate)
        mosques = Mosque.objects.filter(area__in=areas)
    else:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")
    
    if request.method == 'POST':
        mosque_id = request.POST.get('mosque_id')
        if not mosque_id:
            return render(request, 'core/choose_mosque_to_edit.html', {
                'error': 'حدد المسجد الذي تريد تعديله.',
                'mosques': mosques
            })
        
        return redirect('edit_mosque_form', mosque_id=mosque_id)

    return render(request, 'core/choose_mosque_to_edit.html', {'mosques': mosques})

@login_required
def edit_mosque_form(request, mosque_id):
    user = request.user
    try:
        user_role = UserRole.objects.get(user=user)
    except UserRole.DoesNotExist:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")
    
    mosque = get_object_or_404(Mosque, id=mosque_id)
    
    if user_role.role == 'manager':
        directorates = Directorate.objects.filter(manager=user)
        areas = Area.objects.filter(directorate__in=directorates)
        if mosque.area not in areas:
            return HttpResponseForbidden("ليس لديك الأذونات المطلوبة لتعديل هذا المسجد.")
    
    if user_role.role == 'directorate_supervisor':
        directorate = Directorate.objects.filter(supervisor=user).first()
        areas = Area.objects.filter(directorate=directorate)
        if mosque.area not in areas:
            return HttpResponseForbidden("ليس لديك الأذونات المطلوبة لتعديل هذا المسجد.")
    
    if request.method == 'POST':
        mosque.name = request.POST.get('name')
        mosque.mosque_type = request.POST.get('mosque_type')
        mosque.womens_prayer_area = request.POST.get('womens_prayer_area') == 'true'
        mosque.quran_school = request.POST.get('quran_school') == 'true'
        mosque.islamic_center = request.POST.get('islamic_center') == 'true'
        mosque.has_awqaf = request.POST.get('has_awqaf') == 'true'
        mosque.commercial_units = request.POST.get('commercial_units')
        mosque.houses = request.POST.get('houses')
        mosque.farms = request.POST.get('farms')
        mosque.rental_apartments = request.POST.get('rental_apartments')
        mosque.lands = request.POST.get('lands')
        mosque.wells = request.POST.get('wells')
        mosque.khatib_name = request.POST.get('khatib_name')
        mosque.khatib_phone = request.POST.get('khatib_phone')
        mosque.khatib_whatsapp = request.POST.get('khatib_whatsapp')
        mosque.imam_name = request.POST.get('imam_name')
        mosque.imam_phone = request.POST.get('imam_phone')
        mosque.imam_whatsapp = request.POST.get('imam_whatsapp')
        if user_role.role in ['admin', 'manager']:
            mosque.classification = request.POST.get('classification')
        mosque.save()

        # تسجيل العملية الجديدة
        Operation.objects.create(
            supervisor=user,
            operation_type='تعديل_مسجد',
            entity_name=mosque.name,
            entity_id=mosque_id
        )

        if user_role.role == 'admin':
            return redirect('manage_directorates')
        elif user_role.role == 'manager':
            return redirect('manager_page')
        elif user_role.role == 'directorate_supervisor':
            return redirect('directorate_supervisor_page')
        else:
            return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")

    return render(request, 'core/edit_mosque_form.html', {'mosque': mosque, 'user_role': user_role})


@login_required
def choose_mosque_to_delete(request):
    user = request.user
    try:
        user_role = UserRole.objects.get(user=user)
    except UserRole.DoesNotExist:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")
    
    if user_role.role == 'admin':
        mosques = Mosque.objects.all()
    elif user_role.role == 'manager':
        directorates = Directorate.objects.filter(manager=user)
        areas = Area.objects.filter(directorate__in=directorates)
        mosques = Mosque.objects.filter(area__in=areas)
    elif user_role.role == 'directorate_supervisor':
        directorate = Directorate.objects.filter(supervisor=user).first()
        areas = Area.objects.filter(directorate=directorate)
        mosques = Mosque.objects.filter(area__in=areas)
    else:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")
    
    if request.method == 'POST':
        mosque_id = request.POST.get('mosque_id')
        print("Mosque ID to delete:", mosque_id)
        if not mosque_id:
            return render(request, 'choose_mosque_to_delete.html', {
                'error': 'حدد المسجد الذي تريد حذفه.',
                'mosques': mosques
            })
        
        return redirect('delete_mosque_confirm', mosque_id=mosque_id)

    return render(request, 'core/choose_mosque_to_delete.html', {'mosques': mosques})




@login_required
def delete_mosque_confirm(request, mosque_id):
    user = request.user
    try:
        user_role = UserRole.objects.get(user=user)
    except UserRole.DoesNotExist:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")
    
    try:
        mosque = Mosque.objects.get(id=mosque_id)
    except Mosque.DoesNotExist:
        return HttpResponseNotFound("لم يتم العثور على المسجد المطلوب.")
    
    if user_role.role == 'manager':
        directorates = Directorate.objects.filter(manager=user)
        areas = Area.objects.filter(directorate__in=directorates)
        if mosque.area not in areas:
            return HttpResponseForbidden("ليس لديك الأذونات المطلوبة لحذف هذا المسجد.")
    
    if user_role.role == 'directorate_supervisor':
        directorate = Directorate.objects.filter(supervisor=user).first()
        areas = Area.objects.filter(directorate=directorate)
        if mosque.area not in areas:
            return HttpResponseForbidden("ليس لديك الأذونات المطلوبة لحذف هذا المسجد.")
    
    if request.method == 'POST':
        # تخزين بيانات المسجد قبل الحذف
        mosque_data = {
            'name': mosque.name,
            'area': mosque.area.id,
            'directorate': mosque.area.directorate.id,
            'mosque_type': mosque.mosque_type,
            'womens_prayer_area': mosque.womens_prayer_area,
            'quran_school': mosque.quran_school,
            'islamic_center': mosque.islamic_center,
            'has_awqaf': mosque.has_awqaf,
            'commercial_units': mosque.commercial_units,
            'houses': mosque.houses,
            'farms': mosque.farms,
            'rental_apartments': mosque.rental_apartments,
            'lands': mosque.lands,
            'wells': mosque.wells,
            'khatib_name': mosque.khatib_name,
            'khatib_phone': mosque.khatib_phone,
            'khatib_whatsapp': mosque.khatib_whatsapp,
            'imam_name': mosque.imam_name,
            'imam_phone': mosque.imam_phone,
            'imam_whatsapp': mosque.imam_whatsapp
        }
        
        mosque.delete()

        # تسجيل العملية الجديدة
        Operation.objects.create(
            supervisor=user,
            operation_type='حذف_مسجد',
            entity_name=mosque_data['name'],
            entity_id=mosque_id,
            original_data=json.dumps(mosque_data)  # حفظ البيانات الأصلية
        )

        if user_role.role == 'admin':
            return redirect('manage_directorates')
        elif user_role.role == 'manager':
            return redirect('manager_page')
        elif user_role.role == 'directorate_supervisor':
            return redirect('directorate_supervisor_page')
        else:
            return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")

    return render(request, 'core/delete_mosque_confirm.html', {'mosque': mosque, 'user_role': user_role})









@login_required
def new_operations(request):
    user = request.user
    try:
        user_role = UserRole.objects.get(user=user)
    except UserRole.DoesNotExist:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")

    if user_role.role not in ['admin']:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")

    # جلب العمليات التي لم تُعرض بعد
    operations = Operation.objects.filter(shown=False).order_by('-id')
    
    directorates = Directorate.objects.all()

    return render(request, 'core/new_operations.html', {'operations': operations, 'directorates': directorates})





@login_required
def approve_operation(request, operation_id):
    operation = get_object_or_404(Operation, id=operation_id)
    operation.approved = True
    operation.shown = True  # تعيين العملية كمعروضة عند الموافقة
    operation.save()

    # احذف البيانات الأصلية المرتبطة بالعملية بعد الموافقة
    Operation.objects.filter(entity_id=operation.entity_id, operation_type=operation.operation_type).delete()
    
    return JsonResponse({'success': True})

@login_required
def delete_operation(request, operation_id):
    operation = get_object_or_404(Operation, id=operation_id)
    
    if request.method == 'POST':
        if operation.operation_type == 'تعديل_مسجد':
            # إعادة البيانات إلى حالتها الأصلية للمسجد
            original_data = json.loads(operation.original_data)
            mosque = get_object_or_404(Mosque, id=operation.entity_id)
            mosque.name = original_data['name']
            mosque.area_id = original_data['area']
            mosque.mosque_type = original_data['mosque_type']
            mosque.womens_prayer_area = original_data['womens_prayer_area']
            mosque.quran_school = original_data['quran_school']
            mosque.islamic_center = original_data['islamic_center']
            mosque.has_awqaf = original_data['has_awqaf']
            mosque.commercial_units = original_data['commercial_units']
            mosque.houses = original_data['houses']
            mosque.farms = original_data['farms']
            mosque.rental_apartments = original_data['rental_apartments']
            mosque.lands = original_data['lands']
            mosque.wells = original_data['wells']
            mosque.khatib_name = original_data['khatib_name']
            mosque.khatib_phone = original_data['khatib_phone']
            mosque.khatib_whatsapp = original_data['khatib_whatsapp']
            mosque.imam_name = original_data['imam_name']
            mosque.imam_phone = original_data['imam_phone']
            mosque.imam_whatsapp = original_data['imam_whatsapp']
            mosque.save()

        elif 'إضافة_مسجد' in operation.operation_type:
            # حذف الكيان المرتبط بالمسجد
            Mosque.objects.filter(id=operation.entity_id).delete()
        elif 'تعديل_منطقة' in operation.operation_type:
            # إعادة البيانات إلى حالتها الأصلية للمنطقة
            original_data = json.loads(operation.original_data)
            area = get_object_or_404(Area, id=operation.entity_id)
            area.name = original_data['name']
            area.save()
        elif 'إضافة_منطقة' in operation.operation_type:
            # حذف الكيان المرتبط بالمنطقة
            Area.objects.filter(id=operation.entity_id).delete()
        elif 'حذف_منطقة' in operation.operation_type:
            # استعادة الكيان المحذوف للمنطقة
            original_data = json.loads(operation.original_data)
            Area.objects.create(id=operation.entity_id, name=original_data['name'], directorate_id=original_data['directorate'])
        elif operation.operation_type == 'حذف_مسجد':
            # إعادة البيانات إلى حالتها الأصلية للمسجد
            original_data = json.loads(operation.original_data)
            Mosque.objects.create(
                id=operation.entity_id,
                name=original_data['name'],
                area_id=original_data['area'],
                mosque_type=original_data['mosque_type'],
                womens_prayer_area=original_data['womens_prayer_area'],
                quran_school=original_data['quran_school'],
                islamic_center=original_data['islamic_center'],
                has_awqaf=original_data['has_awqaf'],
                commercial_units=original_data['commercial_units'],
                houses=original_data['houses'],
                farms=original_data['farms'],
                rental_apartments=original_data['rental_apartments'],
                lands=original_data['lands'],
                wells=original_data['wells'],
                khatib_name=original_data['khatib_name'],
                khatib_phone=original_data['khatib_phone'],
                khatib_whatsapp=original_data['khatib_whatsapp'],
                imam_name=original_data['imam_name'],
                imam_phone=original_data['imam_phone'],
                imam_whatsapp=original_data['imam_whatsapp']
            )

        # حذف العملية
        operation.delete()
        
        return JsonResponse({'success': True})
    
    return HttpResponseNotFound("طريقة الطلب غير مدعومة.")








@login_required
def edit_mosque_form(request, mosque_id):
    user = request.user
    try:
        user_role = UserRole.objects.get(user=user)
    except UserRole.DoesNotExist:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")
    
    mosque = get_object_or_404(Mosque, id=mosque_id)
    
    if user_role.role == 'manager':
        directorates = Directorate.objects.filter(manager=user)
        areas = Area.objects.filter(directorate__in=directorates)
        if mosque.area not in areas:
            return HttpResponseForbidden("ليس لديك الأذونات المطلوبة لتعديل هذا المسجد.")
    
    if user_role.role == 'directorate_supervisor':
        directorate = Directorate.objects.filter(supervisor=user).first()
        areas = Area.objects.filter(directorate=directorate)
        if mosque.area not in areas:
            return HttpResponseForbidden("ليس لديك الأذونات المطلوبة لتعديل هذا المسجد.")
    
    if request.method == 'POST':
        mosque.name = request.POST.get('name')
        mosque.mosque_type = request.POST.get('mosque_type')
        mosque.womens_prayer_area = request.POST.get('womens_prayer_area') == 'true'
        mosque.quran_school = request.POST.get('quran_school') == 'true'
        mosque.islamic_center = request.POST.get('islamic_center') == 'true'
        mosque.has_awqaf = request.POST.get('has_awqaf') == 'true'
        mosque.commercial_units = request.POST.get('commercial_units')
        mosque.houses = request.POST.get('houses')
        mosque.farms = request.POST.get('farms')
        mosque.rental_apartments = request.POST.get('rental_apartments')
        mosque.lands = request.POST.get('lands')
        mosque.wells = request.POST.get('wells')
        mosque.khatib_name = request.POST.get('khatib_name')
        mosque.khatib_phone = request.POST.get('khatib_phone')
        mosque.khatib_whatsapp = request.POST.get('khatib_whatsapp')
        mosque.imam_name = request.POST.get('imam_name')
        mosque.imam_phone = request.POST.get('imam_phone')
        mosque.imam_whatsapp = request.POST.get('imam_whatsapp')
        if user_role.role in ['admin', 'manager']:
            mosque.classification = request.POST.get('classification')
        mosque.save()

        # تسجيل العملية الجديدة
        Operation.objects.create(
            supervisor=user,
            operation_type='تعديل_مسجد',
            entity_name=mosque.name,
            entity_id=mosque_id
        )

        if user_role.role == 'admin':
            return redirect('manage_directorates')
        elif user_role.role == 'manager':
            return redirect('manager_page')
        elif user_role.role == 'directorate_supervisor':
            return redirect('directorate_supervisor_page')
        else:
            return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")

    return render(request, 'core/edit_mosque_form.html', {'mosque': mosque, 'user_role': user_role})

@login_required
def edit_area_form(request, area_id):
    user = request.user
    try:
        user_role = UserRole.objects.get(user=user)
    except UserRole.DoesNotExist:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")

    area = get_object_or_404(Area, id=area_id)
    
    if user_role.role == 'manager':
        directorates = Directorate.objects.filter(manager=user)
        if area.directorate not in directorates:
            return HttpResponseForbidden("ليس لديك الأذونات المطلوبة لتعديل هذه المنطقة.")
    
    if user_role.role == 'directorate_supervisor':
        directorate = Directorate.objects.filter(supervisor=user).first()
        if area.directorate != directorate:
            return HttpResponseForbidden("ليس لديك الأذونات المطلوبة لتعديل هذه المنطقة.")
    
    if request.method == 'POST':
        area.name = request.POST.get('name')
        area.save()

        # تسجيل العملية الجديدة
        Operation.objects.create(
            supervisor=user,
            operation_type='تعديل_منطقة',
            entity_name=area.name,
            entity_id=area_id
        )

        if user_role.role == 'admin':
            return redirect('manage_directorates')
        elif user_role.role == 'manager':
            return redirect('manager_page')
        elif user_role.role == 'directorate_supervisor':
            return redirect('directorate_supervisor_page')
        else:
            return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")

    return render(request, 'core/edit_area_form.html', {'area': area})






def export_directorate_data(request, directorate_id=None):
    user_role = UserRole.objects.get(user=request.user)

    if user_role.role == 'directorate_supervisor':
        directorate = user_role.directorate
        mosques = Mosque.objects.filter(area__directorate=directorate).select_related('area__directorate')

        data = []
        for mosque in mosques:
            mosque_data = {
                'اسم المديرية': mosque.area.directorate.name,
                'اسم المنطقة': mosque.area.name,
                'اسم المسجد': mosque.name,
                'نوع الجامع': mosque.mosque_type,
                'مصلى النساء': 'نعم' if mosque.womens_prayer_area else 'لا',
                'مدرسة تحفيظ القرآن الكريم': 'نعم' if mosque.quran_school else 'لا',
                'مركز للعلوم الشرعية': 'نعم' if mosque.islamic_center else 'لا',
                'هل للجامع أوقاف': 'نعم' if mosque.has_awqaf else 'لا',
                'عدد المحلات التجارية': mosque.commercial_units if mosque.has_awqaf else '',
                'عدد البيوت': mosque.houses if mosque.has_awqaf else '',
                'عدد المزارع': mosque.farms if mosque.has_awqaf else '',
                'عدد الشقق المؤجرة': mosque.rental_apartments if mosque.has_awqaf else '',
                'عدد الأراضي': mosque.lands if mosque.has_awqaf else '',
                'عدد الآبار': mosque.wells if mosque.has_awqaf else '',
                'اسم الخطيب': mosque.khatib_name,
                'رقم هاتف الخطيب': mosque.khatib_phone,
                'رقم واتساب الخطيب': mosque.khatib_whatsapp,
                'اسم إمام المسجد': mosque.imam_name,
                'رقم هاتف إمام المسجد': mosque.imam_phone,
                'رقم واتساب إمام المسجد': mosque.imam_whatsapp,
            }
            data.append(mosque_data)

    elif user_role.role in ['manager', 'admin']:
        if not directorate_id:
            return HttpResponseForbidden("يجب تحديد المديرية.")

        try:
            directorate = Directorate.objects.get(id=directorate_id)
        except Directorate.DoesNotExist:
            return HttpResponseForbidden("المديرية غير موجودة.")

        if user_role.role == 'director' and directorate.supervisor != request.user:
            return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه المديرية.")

        mosques = Mosque.objects.filter(area__directorate=directorate).select_related('area__directorate')

        data = []
        for mosque in mosques:
            mosque_data = {
                'اسم المديرية': mosque.area.directorate.name,
                'اسم المنطقة': mosque.area.name,
                'اسم المسجد': mosque.name,
                'نوع الجامع': mosque.mosque_type,
                'مصلى النساء': 'نعم' if mosque.womens_prayer_area else 'لا',
                'مدرسة تحفيظ القرآن الكريم': 'نعم' if mosque.quran_school else 'لا',
                'مركز للعلوم الشرعية': 'نعم' if mosque.islamic_center else 'لا',
                'هل للجامع أوقاف': 'نعم' if mosque.has_awqaf else 'لا',
                'عدد المحلات التجارية': mosque.commercial_units if mosque.has_awqaf else '',
                'عدد البيوت': mosque.houses if mosque.has_awqaf else '',
                'عدد المزارع': mosque.farms if mosque.has_awqaf else '',
                'عدد الشقق المؤجرة': mosque.rental_apartments if mosque.has_awqaf else '',
                'عدد الأراضي': mosque.lands if mosque.has_awqaf else '',
                'عدد الآبار': mosque.wells if mosque.has_awqaf else '',
                'اسم الخطيب': mosque.khatib_name,
                'رقم هاتف الخطيب': mosque.khatib_phone,
                'رقم واتساب الخطيب': mosque.khatib_whatsapp,
                'اسم إمام المسجد': mosque.imam_name,
                'رقم هاتف إمام المسجد': mosque.imam_phone,
                'رقم واتساب إمام المسجد': mosque.imam_whatsapp,
                'التصنيف الدعوي': mosque.classification if user_role.role in ['manager', 'admin'] else ''
            }
            data.append(mosque_data)

    else:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")

    df = pd.DataFrame(data)

    # إعداد ملف الإكسل
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=directorate_data.xlsx'

    # كتابة ملف إكسل باللغة العربية باستخدام openpyxl
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='بيانات المديرية')
        workbook = writer.book
        worksheet = writer.sheets['بيانات المديرية']

        # إعداد الاتجاه من اليمين لليسار
        worksheet.sheet_view.rightToLeft = True

    return response



@login_required
def director_mosques_view(request):
    user_role = UserRole.objects.get(user=request.user)

    if user_role.role != 'manager':
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")

    # الحصول على المساجد ذات التصنيف الافتراضي
    mosques = Mosque.objects.filter(classification='default_classification').select_related('area__directorate')

    # إعداد البيانات للعرض
    mosques_data = []
    for mosque in mosques:
        mosque_data = {
            'directorate_name': mosque.area.directorate.name,
            'supervisor_name': mosque.area.directorate.supervisor.username,
            'area_name': mosque.area.name,
            'mosque_name': mosque.name,
            'mosque_id': mosque.id
        }
        mosques_data.append(mosque_data)

    return render(request, 'core/manager_page.html', {'mosques_data': mosques_data})




@login_required
def export_statistics_pdf(request):
    user_count = User.objects.count()
    directorate_count = Directorate.objects.count()
    area_count = Area.objects.count()
    mosque_count = Mosque.objects.count()

    # جمع تفاصيل المساجد
    mosque_details = {
        'types': {},
        'womens_prayer_area': 0,
        'quran_school': 0,
        'islamic_center': 0,
        'has_awqaf': 0,
        'commercial_units': 0,
        'houses': 0,
        'lands': 0,
        'farms': 0,
        'wells': 0,
        'classification': {}
    }

    mosques = Mosque.objects.all()
    for mosque in mosques:
        mosque_details['types'][mosque.mosque_type] = mosque_details['types'].get(mosque.mosque_type, 0) + 1
        if mosque.womens_prayer_area:
            mosque_details['womens_prayer_area'] += 1
        if mosque.quran_school:
            mosque_details['quran_school'] += 1
        if mosque.islamic_center:
            mosque_details['islamic_center'] += 1
        if mosque.has_awqaf:
            mosque_details['has_awqaf'] += 1
        mosque_details['commercial_units'] += mosque.commercial_units or 0
        mosque_details['houses'] += mosque.houses or 0
        mosque_details['lands'] += mosque.lands or 0
        mosque_details['farms'] += mosque.farms or 0
        mosque_details['wells'] += mosque.wells or 0
        mosque_details['classification'][mosque.classification] = mosque_details['classification'].get(mosque.classification, 0) + 1

    # جمع إحصائيات المديريات
    directorate_details = {}
    directorates = Directorate.objects.all()
    for directorate in directorates:
        areas = Area.objects.filter(directorate=directorate)
        mosques_in_directorate = Mosque.objects.filter(area__in=areas).count()
        directorate_details[directorate.name] = {
            'area_count': areas.count(),
            'mosque_count': mosques_in_directorate
        }

    # دالة لإنشاء الرسوم البيانية
    def create_pie_chart(labels, sizes):
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct=lambda p: '{:.1f}%'.format(p), startangle=90)
        ax.axis('equal')
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)  # تأكد من إغلاق الشكل لتجنب التحذيرات غير الضرورية
        buf.seek(0)
        return buf

    # دالة لإضافة الصور إلى ملف PDF
    def add_image_to_pdf(pdf_canvas, img_buf, x, y, width, height):
        imgdata = img_buf.getvalue()
        img = utils.ImageReader(io.BytesIO(imgdata))
        pdf_canvas.drawImage(img, x, y, width=width, height=height)

    # إعداد ملف PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="statistics.pdf"'

    p = canvas.Canvas(response, pagesize=landscape(letter))
    width, height = landscape(letter)

    # عنوان
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, "إحصائيات المساجد")

    # إضافة الإحصائيات النصية
    p.setFont("Helvetica", 12)
    y = height - 100
    p.drawString(100, y, f"عدد المستخدمين: {user_count}")
    y -= 20
    p.drawString(100, y, f"عدد المديريات: {directorate_count}")
    y -= 20
    p.drawString(100, y, f"عدد المناطق: {area_count}")
    y -= 20
    p.drawString(100, y, f"عدد المساجد: {mosque_count}")
    y -= 20
    p.drawString(100, y, f"مصلى النساء: {mosque_details['womens_prayer_area']}")
    y -= 20
    p.drawString(100, y, f"مدارس تحفيظ القرآن: {mosque_details['quran_school']}")
    y -= 20
    p.drawString(100, y, f"المراكز الإسلامية: {mosque_details['islamic_center']}")
    y -= 20
    p.drawString(100, y, f"أوقاف المسجد: {mosque_details['has_awqaf']}")

    # إعداد الرسوم البيانية
    charts = {
        'types': create_pie_chart(list(mosque_details['types'].keys()), list(mosque_details['types'].values())),
        'classification': create_pie_chart(list(mosque_details['classification'].keys()), list(mosque_details['classification'].values())),
        'directorates': create_pie_chart(list(directorate_details.keys()), [details['mosque_count'] for details in directorate_details.values()]),
        'has_awqaf': create_pie_chart(['لديه أوقاف', 'لا يوجد أوقاف'], [mosque_details['has_awqaf'], mosque_count - mosque_details['has_awqaf']]),
        'womens_prayer_area': create_pie_chart(['يوجد مصلى للنساء', 'لا يوجد مصلى للنساء'], [mosque_details['womens_prayer_area'], mosque_count - mosque_details['womens_prayer_area']]),
        'quran_school': create_pie_chart(['يوجد مدرسة تحفيظ', 'لا يوجد مدرسة تحفيظ'], [mosque_details['quran_school'], mosque_count - mosque_details['quran_school']])
    }

    # إضافة الرسوم البيانية إلى ملف PDF
    y -= 60
    for chart_title, chart_buf in charts.items():
        add_image_to_pdf(p, chart_buf, 100, y, width=400, height=200)
        y -= 240

    p.showPage()
    p.save()

    return response



def search(request):
    user_role = UserRole.objects.get(user=request.user)
    query = request.GET.get('q', '')

    if user_role.role == 'admin':
        mosques = Mosque.objects.filter(name__icontains=query)
        areas = Area.objects.filter(name__icontains=query)
        directorates = Directorate.objects.filter(name__icontains=query)
    elif user_role.role == 'manager':
        directorates = Directorate.objects.filter(supervisor=request.user, name__icontains=query)
        areas = Area.objects.filter(directorate__supervisor=request.user, name__icontains=query)
        mosques = Mosque.objects.filter(area__directorate__supervisor=request.user, name__icontains=query)
    elif user_role.role == 'directorate_supervisor':
        directorate = user_role.directorate
        areas = Area.objects.filter(directorate=directorate, name__icontains=query)
        mosques = Mosque.objects.filter(area__directorate=directorate, name__icontains=query)
        directorates = Directorate.objects.none()
    else:
        return HttpResponseForbidden("ليس لديك الأذونات المطلوبة للوصول إلى هذه الصفحة.")

    results = {
        'mosques': [{'name': mosque.name, 'area': mosque.area.name, 'directorate': mosque.area.directorate.name} for mosque in mosques],
        'areas': [{'name': area.name, 'directorate': area.directorate.name} for area in areas],
        'directorates': [{'name': directorate.name} for directorate in directorates]
    }
    
    return JsonResponse(results)





@login_required
def add_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password != confirm_password:
            return render(request, 'core/add_user.html', {'error': 'كلمة المرور وتأكيد كلمة المرور غير متطابقين'})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'core/add_user.html', {'error': 'اسم المستخدم هذا موجود بالفعل'})

        try:
            user = User.objects.create_user(username=username, password=password)
            return redirect('user_details', user_id=user.id)
        except IntegrityError:
            return render(request, 'core/add_user.html', {'error': 'حدث خطأ أثناء إنشاء المستخدم، حاول مرة أخرى'})

    return render(request, 'core/add_user.html')

@login_required
def user_details(request, user_id):
    user = get_object_or_404(User, id=user_id)
    directorates = Directorate.objects.all()
    groups = Group.objects.all()  # جلب جميع مجموعات المستخدمين

    if request.method == 'POST':
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.is_active = 'active' in request.POST
        user.is_staff = 'staff' in request.POST
        user.save()
        
        # تحديث مجموعات المستخدمين
        selected_groups = request.POST.getlist('groups')
        user.groups.set(selected_groups)  # استخدام set لإعادة تعيين المجموعات

        # تحديث المديريات
        selected_directorates = request.POST.getlist('directorates')
        directorates_to_add = []
        for directorate_id in selected_directorates:
            directorate = get_object_or_404(Directorate, id=directorate_id)
            directorates_to_add.append(directorate)
        user.directorates.set(directorates_to_add)  # استخدام set لإعادة تعيين المديريات
        
        user.save()
        
        return redirect('manage_users')

    return render(request, 'core/user_details.html', {'user': user, 'directorates': directorates, 'groups': groups})
