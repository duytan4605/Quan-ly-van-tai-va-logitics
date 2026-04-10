from django import forms
from .models import TaiXe, KhoHang, DonHang
from django.contrib.auth.models import User # 👉 Nhớ import User ở tuốt trên cùng nhé
from django.core.exceptions import ValidationError
from .models import DonHang # Nhớ import model DonHang nếu chưa có
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
            'ma_don': 'Mã Đơn Hàng ',
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

    # HÀM NÀY ĐÃ ĐƯỢC THỤT LỀ VÀO ĐÚNG BÊN TRONG CLASS DonHangForm
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # TỰ ĐỘNG ĐIỀN MÃ ĐƠN HÀNG KHI "THÊM MỚI" (Không áp dụng khi Sửa)
        if not self.instance.pk: 
            last_order = DonHang.objects.all().order_by('id').last()
            
            if not last_order:
                next_ma_don = 'DH001'
            else:
                try:
                    # Cắt chữ 'DH' lấy phần số, cộng thêm 1
                    last_num = int(last_order.ma_don[2:]) 
                    next_ma_don = f'DH{last_num + 1:03d}'
                except ValueError:
                    next_ma_don = 'DH001' # Đề phòng data cũ bị lỗi format
            
            # Ép giá trị ban đầu vào ô input
            self.fields['ma_don'].initial = next_ma_don

        # Khóa luôn ô này, chỉ cho nhìn (Read-only) để không ai sửa bậy làm hỏng cấu trúc
        self.fields['ma_don'].widget.attrs['readonly'] = True
        self.fields['ma_don'].widget.attrs['style'] = 'background-color: #e2e8f0; color: #64748b; cursor: not-allowed; font-weight: bold;'

    def clean(self):
        cleaned_data = super().clean()
        
        # Sửa thành 'kho_xuat_phat' cho đúng với tên trường trong form của bạn
        kho_hang = cleaned_data.get('kho_xuat_phat') 

        if kho_hang:
            # Lấy số đơn đang có trong kho
            so_luong_hien_tai = kho_hang.so_don_dang_luu_tru()

            # Nếu là đang SỬA đơn hàng cũ (đơn này đã nằm sẵn trong kho rồi), thì phải trừ đi 1 
            if self.instance.pk and self.instance.kho_xuat_phat == kho_hang:
                so_luong_hien_tai -= 1

            # BẮT ĐẦU KIỂM TRA SỨC CHỨA
            if so_luong_hien_tai >= kho_hang.suc_chua_toi_da:
                # Quăng lỗi đỏ lên màn hình ngay lập tức!
                raise ValidationError(
                    f"⚠️ LỖI: {kho_hang.ten_kho} đã đạt giới hạn sức chứa ({kho_hang.suc_chua_toi_da} đơn). "
                    f"Vui lòng luân chuyển sang kho lân cận!"
                )

        return cleaned_data
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
    
    from django import forms
    
from .models import LichSuKho
class LichSuKhoForm(forms.ModelForm):
    class Meta:
        model = LichSuKho
        fields = ['don_hang', 'kho', 'trang_thai_buoc', 'ghi_chu']
        widgets = {
            'don_hang': forms.Select(attrs={'class': 'form-control'}),
            'kho': forms.Select(attrs={'class': 'form-control'}),
            # ĐỔI THÀNH SELECT Ở ĐÂY
            'trang_thai_buoc': forms.Select(attrs={'class': 'form-control'}), 
            'ghi_chu': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ghi chú thêm nếu có...'}),
        }