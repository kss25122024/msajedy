from django import forms
from .models import Directorate,Area, Mosque




class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['name', 'directorate']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم المنطقة'}),
        }





        

class DirectorateForm(forms.ModelForm):
    class Meta:
        model = Directorate
        fields = ['name', 'manager', 'supervisor']


class MosqueForm(forms.ModelForm):
    class Meta:
        model = Mosque
        fields = ['name', 'area',  'mosque_type', 'womens_prayer_area', 'quran_school', 'islamic_center', 'has_awqaf', 'commercial_units', 'houses', 'farms', 'rental_apartments', 'lands', 'wells', 'khatib_name', 'khatib_phone', 'khatib_whatsapp', 'imam_name', 'imam_phone', 'imam_whatsapp' ]
        
        labels = {
            
             'name': ' اسم المسجد ',
        'mosque_type': 'نوع المسجد ',
        'womens_prayer_area': 'مصلى النساء',
        'quran_school': 'مدرسة تحفيظ القران الكريم',
        'islamic_center': 'مركز للعلوم الشرعية',
        'has_awqaf': 'هل للمسجد أوقاف',
        'commercial_units': 'محلات تجارية',
        'houses': 'بيوت',
        'farms': 'مزارع',
        'rental_apartments': 'شقق للإيجار',
        'lands': 'أراضي',
        'wells': 'آبار',
        'khatib_name': 'اسم خطيب المسجد',
        'khatib_phone': 'رقم هاتف خطيب المسجد',
        'khatib_whatsapp': 'رقم واتس خطيب المسجد',
        'imam_name': 'اسم إمام المسجد',
        'imam_phone': 'رقم هاتف امام المسجد',
        'imam_whatsapp': 'رقم واتس امام المسجد',
    
            
            
            
            
            
        }
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم المسجد'}),
            'area': forms.Select(attrs={'class': 'form-control'}),
        }

