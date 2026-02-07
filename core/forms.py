# core/forms.py
from django import forms
from .models import TaiXe, KhoHang, DonHang

# 1. Form cho Tài xế
class TaiXeForm(forms.ModelForm):
    class Meta:
        model = TaiXe
        fields = '__all__' # Lấy tất cả các trường để nhập
        widgets = {
            'ca_lam_viec': forms.Select(attrs={'class': 'form-control'}),
            'loai_xe': forms.Select(attrs={'class': 'form-control'}),
            'ten_tai_xe': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập họ tên'}),
            'sdt': forms.TextInput(attrs={'class': 'form-control'}),
            'bien_so': forms.TextInput(attrs={'class': 'form-control'}),
            'trang_thai': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
# 2. Form cho Kho Hàng
class KhoHangForm(forms.ModelForm):
    class Meta:
        model = KhoHang
        fields = '__all__'
        widgets = {
            'ten_kho': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên kho...'}),
            'dia_chi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Địa chỉ...'}),
            'lat': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'lng': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
        }

# 3. Form cho Đơn Hàng
class DonHangForm(forms.ModelForm):
    class Meta:
        model = DonHang
        fields = '__all__'
        exclude = ['ngay_tao'] # Ngày tạo tự động, không cần nhập
        widgets = {
            'ma_don': forms.TextInput(attrs={'class': 'form-control'}),
            'ten_nguoi_nhan': forms.TextInput(attrs={'class': 'form-control'}),
            'dia_chi_nguoi_nhan': forms.TextInput(attrs={'class': 'form-control'}),
            'sdt_nguoi_nhan': forms.TextInput(attrs={'class': 'form-control'}),
            'lat_khach': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'lng_khach': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'khoi_luong': forms.NumberInput(attrs={'class': 'form-control'}),
            'kho_xuat_phat': forms.Select(attrs={'class': 'form-control'}),
            'tai_xe': forms.Select(attrs={'class': 'form-control'}),
            'trang_thai': forms.TextInput(attrs={'class': 'form-control'}),
        }