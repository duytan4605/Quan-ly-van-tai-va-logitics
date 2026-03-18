from django.db import models
from django.contrib.auth.models import User  # 👉 Đã thêm thư viện User

# 1. Bảng Kho Hàng
class KhoHang(models.Model):
    ten_kho = models.CharField(max_length=100)
    dia_chi = models.CharField(max_length=200)
    lat = models.FloatField(help_text="Vĩ độ")
    lng = models.FloatField(help_text="Kinh độ")

    def __str__(self):
        return self.ten_kho

    # Đã được thụt lề vào trong cho đúng chuẩn
    suc_chua_toi_da = models.IntegerField(default=100, verbose_name="Sức chứa tối đa (Đơn)")

    def so_don_dang_luu_tru(self):
        """Hàm đếm số đơn hàng đang nằm trong kho (Bỏ qua các đơn đã giao xong hoặc hủy)"""
        # Lưu ý: Sửa chữ 'donhang_set' thành 'donhangs' nếu bạn có dùng related_name='donhangs'
        return self.donhang_set.exclude(trang_thai__in=['ĐÃ GIAO THÀNH CÔNG', 'HỦY']).count()



# 2. Bảng Tài Xế (Đã nâng cấp cho Tool Quản lý & Liên kết Tài khoản)
class TaiXe(models.Model):
    # --- 👇 TRƯỜNG MỚI: Liên kết với Tài khoản hệ thống 👇 ---
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tài khoản đăng nhập")
    
    # --- Thông tin cơ bản ---
    ten_tai_xe = models.CharField(max_length=100)
    sdt = models.CharField(max_length=15)
    bien_so = models.CharField(max_length=20)
    
    loai_xe = models.CharField(max_length=50, choices=[
        ('Xe máy', 'Xe máy'),
        ('Xe tải', 'Xe tải'),
        ('Xe bán tải', 'Xe bán tải')
    ])
    
    trang_thai = models.CharField(max_length=20, default='Sẵn sàng')

    # --- CÁC TRƯỜNG MỚI CHO QUẢN LÝ (HRM & KPI) ---
    CA_LAM_CHOICES = [
        ('SANG', 'Ca Sáng (6h - 14h)'),
        ('CHIEU', 'Ca Chiều (14h - 22h)'),
        ('DEM', 'Ca Đêm (22h - 6h)'),
    ]
    
    ca_lam_viec = models.CharField(max_length=10, choices=CA_LAM_CHOICES, default='SANG', verbose_name="Ca làm việc")
    
    # Chấm công: True = Đang đi làm, False = Nghỉ
    dang_lam_viec = models.BooleanField(default=False, verbose_name="Đang Online (Chấm công)")
    
    # KPI hiệu suất
    tong_don_thang_nay = models.IntegerField(default=0, verbose_name="KPI Số đơn/Tháng")
    doanh_thu_tich_luy = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="Doanh thu tích lũy")

    def __str__(self):
        # Hiển thị tên + ca làm để dễ chọn trong Admin
        return f"{self.ten_tai_xe} ({self.loai_xe}) - {self.get_ca_lam_viec_display()}"

# 3. Bảng Đơn Hàng
class DonHang(models.Model):
    ma_don = models.CharField(max_length=20, unique=True)
    ten_nguoi_nhan = models.CharField(max_length=100)
    dia_chi_nguoi_nhan = models.CharField(max_length=200)
    sdt_nguoi_nhan = models.CharField(max_length=15)
    
    # Tọa độ khách hàng
    lat_khach = models.FloatField()
    lng_khach = models.FloatField()
    
    khoi_luong = models.FloatField(help_text="Đơn vị: kg")
    
    # Liên kết với Kho và Tài xế
    kho_xuat_phat = models.ForeignKey(KhoHang, on_delete=models.CASCADE)
    tai_xe = models.ForeignKey(TaiXe, on_delete=models.SET_NULL, null=True, blank=True)
    
    trang_thai = models.CharField(max_length=50, default='Đang xử lý')
    ngay_tao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Đơn {self.ma_don}"