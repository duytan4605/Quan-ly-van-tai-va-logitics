# core/serializers.py
from rest_framework import serializers
from .models import DonHang  # Chú ý: Đảm bảo ông có model tên là DonHang nhé

class DonHangSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonHang
        # Các trường thông tin mà Shopee/Tiktok sẽ đẩy sang cho mình
        fields = [
            'ten_nguoi_nhan', 
            'sdt_nguoi_nhan', 
            'dia_chi_nguoi_nhan', 
            'lat_khach', 
            'lng_khach'
        ]