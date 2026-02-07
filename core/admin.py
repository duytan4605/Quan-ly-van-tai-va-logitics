from django.contrib import admin
from .models import KhoHang, TaiXe, DonHang

# Đăng ký 3 bảng này để nó hiện lên trang Admin
admin.site.register(KhoHang)
admin.site.register(TaiXe)
admin.site.register(DonHang)