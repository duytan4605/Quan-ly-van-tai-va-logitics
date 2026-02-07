from django.urls import path
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

    # 5. Trang Dashboard Quản lý Tài xế (Xem danh sách)
    path('quan-ly-tai-xe/', views.quan_ly_tai_xe, name='quan_ly_tai_xe'),
    
    # 6. Trang Thêm Tài xế mới (Create)
    path('them-tai-xe/', views.them_tai_xe, name='them_tai_xe'),

    # 7. Trang Sửa thông tin Tài xế (Update) - Cần ID để biết sửa ai
    path('sua-tai-xe/<int:id>/', views.sua_tai_xe, name='sua_tai_xe'),

    # 8. Chức năng Xóa Tài xế (Delete) - Cần ID để biết xóa ai
    path('xoa-tai-xe/<int:id>/', views.xoa_tai_xe, name='xoa_tai_xe'),
    # ... (Giữ nguyên các path cũ) ...

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

]