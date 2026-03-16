from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# Định danh App là 'core' (Bắt buộc để dùng {% url 'core:...' %})
app_name = 'core'

urlpatterns = [
    # --- CÁC TRANG CŨ (VIEW) ---
    # 1. Trang chủ (Danh sách đơn hàng)
    path('', views.home, name='home'),

    # 2. Trang Bản đồ GIS chung (Xem tất cả xe)
    path('map/', views.ban_do_chung, name='ban_do_chung'),

    # 3. Trang chi tiết lộ trình đơn hàng (Xem 1 đơn)
    path('chi-tiet/<str:ma_don>/', views.chi_tiet, name='chi_tiet'),

    # 4. Trang Tối ưu hóa lộ trình (TSP)
    path('toi-uu-lo-trinh/', views.toi_uu_lo_trinh, name='toi_uu'),

    # --- QUẢN LÝ TÀI XẾ ---
    path('quan-ly-tai-xe/', views.quan_ly_tai_xe, name='quan_ly_tai_xe'),
    path('them-tai-xe/', views.them_tai_xe, name='them_tai_xe'),
    path('sua-tai-xe/<int:id>/', views.sua_tai_xe, name='sua_tai_xe'),
    path('xoa-tai-xe/<int:id>/', views.xoa_tai_xe, name='xoa_tai_xe'),

    # --- QUẢN LÝ KHO ---
    path('quan-ly-kho/', views.quan_ly_kho, name='quan_ly_kho'),
    path('them-kho/', views.them_kho, name='them_kho'),
    path('sua-kho/<int:id>/', views.sua_kho, name='sua_kho'),
    path('xoa-kho/<int:id>/', views.xoa_kho, name='xoa_kho'),

    # --- QUẢN LÝ ĐƠN HÀNG ---
    path('quan-ly-don-hang/', views.quan_ly_don_hang, name='quan_ly_don_hang'),
    path('them-don-hang/', views.them_don_hang, name='them_don_hang'),
    path('sua-don-hang/<int:id>/', views.sua_don_hang, name='sua_don_hang'),
    path('xoa-don-hang/<int:id>/', views.xoa_don_hang, name='xoa_don_hang'),

    # --- ĐĂNG NHẬP / ĐĂNG XUẤT ---
    # 👇 ĐÃ SỬA: Dùng hàm dang_nhap tùy chỉnh để phân quyền Shipper/Admin 👇
    path('login/', views.dang_nhap, name='login'),
    
    # Kêu gọi hàm dang_xuat để Fix lỗi 405
    path('logout/', views.dang_xuat, name='logout'),

    # --- APP SHIPPER ---
    path('app-shipper/', views.app_shipper, name='app_shipper'),
    path('shipper-cap-nhat/<int:don_id>/', views.shipper_cap_nhat, name='shipper_cap_nhat'),

    # --- QUẢN LÝ TÀI KHOẢN ---
    path('quan-ly-tai-khoan/', views.quan_ly_tai_khoan, name='quan_ly_tai_khoan'),
    path('them-tai-khoan/', views.them_tai_khoan, name='them_tai_khoan'),
    path('sua-tai-khoan/<int:id>/', views.sua_tai_khoan, name='sua_tai_khoan'),
    path('xoa-tai-khoan/<int:id>/', views.xoa_tai_khoan, name='xoa_tai_khoan'),
]