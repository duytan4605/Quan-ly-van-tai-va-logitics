from django import forms
from .models import TaiXe, KhoHang, DonHang
from django.contrib.auth.models import User # 👉 Nhớ import User ở tuốt trên cùng nhé
# 1. Form cho Tài xế
class TaiXeForm(forms.ModelForm):
    class Meta:
        model = TaiXe
        fields = '__all__' # Lấy tất cả các trường để nhập
        labels = {
            'ten_tai_xe': 'Họ tên Tài xế',
            'sdt': 'Số điện thoại',
            'bien_so': 'Biển số xe',
            'loai_xe': 'Loại phương tiện',
            'trang_thai': 'Trạng thái hoạt động',
            'ca_lam_viec': 'Ca làm việc',
            'dang_lam_viec': 'Chấm công (Đang online)',
        }
        widgets = {
            'ca_lam_viec': forms.Select(attrs={'class': 'form-control'}),
            'loai_xe': forms.Select(attrs={'class': 'form-control'}),
            'ten_tai_xe': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập họ tên...'}),
            'sdt': forms.TextInput(attrs={'class': 'form-control'}),
            'bien_so': forms.TextInput(attrs={'class': 'form-control'}),
            'trang_thai': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
# 2. Form cho Kho Hàng
class KhoHangForm(forms.ModelForm):
    class Meta:
        model = KhoHang
        fields = '__all__'
        labels = {
            'ten_kho': 'Tên Kho Hàng',
            'dia_chi': 'Địa chỉ Kho',
            'lat': 'Vĩ độ (Lat)',
            'lng': 'Kinh độ (Lng)',
        }
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
        
        # 👇 Đã thêm Labels để Việt hóa chữ trên Form 👇
        labels = {
            'ma_don': 'Mã Đơn Hàng (VD: DH001)',
            'ten_nguoi_nhan': 'Tên Khách Hàng',
            'dia_chi_nguoi_nhan': 'Địa Chỉ Giao Hàng',
            'sdt_nguoi_nhan': 'Số Điện Thoại',
            'lat_khach': 'Vĩ độ (Lat)',
            'lng_khach': 'Kinh độ (Lng)',
            'khoi_luong': 'Khối Lượng (kg)',
            'kho_xuat_phat': 'Kho Xuất Phát',
            'tai_xe': 'Phân Công Shipper',
            'trang_thai': 'Trạng Thái Đơn Hàng',
        }
        
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
            
            # 👇 Đã chuyển đổi thành Select Option thay vì TextInput 👇
            'trang_thai': forms.Select(
                attrs={'class': 'form-control'}, 
                choices=[
                    ('CHỜ TÀI XẾ', 'Chờ tài xế (Mới tạo)'),
                    ('ĐANG VẬN CHUYỂN', 'Đang vận chuyển'),
                    ('ĐÃ GIAO THÀNH CÔNG', 'Đã giao thành công'),
                    ('ĐÃ HỦY', 'Đã hủy đơn'),
                    ('TRẢ HÀNG VỀ KHO', 'Trả hàng về kho'),
                ]
            ),
        }
        # ... (Các form cũ giữ nguyên) ...

# ==================== 4. FORM TÀI KHOẢN (USER) ====================
class TaiKhoanForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nhập mật khẩu mới...'}), 
        required=False, 
        label="Mật khẩu (Để trống nếu không muốn đổi)"
    )
    is_staff = forms.BooleanField(
        required=False, 
        label="Cấp quyền Admin (Tích vào nếu là Sếp, Bỏ tích nếu là Shipper)"
    )

    class Meta:
        model = User
        fields = ['username', 'is_staff']
        labels = {'username': 'Tên đăng nhập (Viết liền không dấu)'}
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: shipper_tuan'}),
        }

    # Hàm lưu tùy chỉnh để mã hóa mật khẩu an toàn
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:  # Nếu có nhập pass mới thì mới cập nhật
            user.set_password(password)
        if commit:
            user.save()
        return user