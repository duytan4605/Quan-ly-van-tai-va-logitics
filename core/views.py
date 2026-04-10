import json
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import DonHangSerializer
# Import models và forms từ thư mục core
from .models import KhoHang, LichSuKho, TaiXe, DonHang 
from .forms import TaiXeForm, KhoHangForm, DonHangForm, TaiKhoanForm
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import openpyxl
from .models import DonHang # Đảm bảo đúng tên model
# Sửa dòng 18 trong views.py
from .models import KhoHang, TaiXe, DonHang, LichSuKho  # Thêm LichSuKho vào đây
from .forms import TaiXeForm, KhoHangForm, DonHangForm, TaiKhoanForm, LichSuKhoForm # Thêm LichSuKhoForm vào đây
# ==============================================================================
# 1. HỆ THỐNG XÁC THỰC & ĐIỀU HƯỚNG (AUTHENTICATION)
# ==============================================================================

def dang_nhap(request):
    """Xử lý đăng nhập: KHÔNG báo thành công, CHỈ báo lỗi khi sai tài khoản"""
    if request.user.is_authenticated:
        if request.user.is_staff: # Thêm dòng này: Nếu là Admin
            return redirect('core:home')
        if hasattr(request.user, 'taixe'): # Nếu là Shipper
            return redirect('core:app_shipper')
        return redirect('core:partner_demo') # Không phải 2 thằng trên -> Chắc chắn là Đối tác

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        user = authenticate(request, username=u, password=p)
        
        if user is not None:
            login(request, user)
            if user.is_staff: # Nếu là Admin
                return redirect('core:home')
            if hasattr(user, 'taixe'): # Nếu là Shipper
                return redirect('core:app_shipper')
            return redirect('core:partner_demo') # Đối tác bay thẳng vào form đẩy đơn
        else:
            # GIỮ LẠI DUY NHẤT THÔNG BÁO LỖI NÀY
            messages.error(request, 'Sai tên đăng nhập hoặc mật khẩu!')
            
    return render(request, 'login.html')

def dang_xuat(request):
    """Đăng xuất: Thoát thẳng ra trang chủ, im lặng 100%"""
    logout(request)
    return redirect('core:home')

# ==============================================================================
# 2. TRANG CHỦ & DASHBOARD THỐNG KÊ (ADMIN DASHBOARD)
# ==============================================================================

def home(request):
    """Trang chủ: Dashboard cho Admin + Tra cứu cho Khách + Phân trang + Lọc"""
    
    # CHẶN ĐỐI TÁC NGAY TỪ CỬA: Tránh trường hợp nó tự gõ URL /home/
    if request.user.is_authenticated and not request.user.is_staff and not hasattr(request.user, 'taixe'):
        return redirect('core:partner_demo')

    q = request.GET.get('q', '')
    status_filter = request.GET.get('status', 'ALL')
    
    # 1. Lấy danh sách đơn hàng và lọc
    ds_don = DonHang.objects.all().order_by('-id')
    
    if status_filter and status_filter != 'ALL':
        ds_don = ds_don.filter(trang_thai=status_filter)

    if q:
        ds_don = ds_don.filter(Q(ma_don__icontains=q) | Q(sdt_nguoi_nhan__icontains=q))

    # 2. XỬ LÝ PHÂN TRANG (5 đơn / 1 trang)
    paginator = Paginator(ds_don, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.user.is_authenticated:
        # Nếu là tài xế thì đá sang app shipper
        if hasattr(request.user, 'taixe'): 
            return redirect('core:app_shipper')
        
        # Thống kê cho Dashboard (Tui giữ nguyên 100% không mất số liệu của ông)
        top_tai_xe = TaiXe.objects.order_by('-doanh_thu_tich_luy')[:5]
        thong_ke_don = DonHang.objects.values('trang_thai').annotate(so_luong=Count('id'))

        context = {
            'don_hangs': page_obj, 
            'page_obj': page_obj,  
            'current_status': status_filter,
            'q': q,
            'stats': {
                'tong_don': DonHang.objects.count(),
                'don_dang_giao': DonHang.objects.filter(trang_thai='ĐANG VẬN CHUYỂN').count(),
                'tong_doanh_thu': TaiXe.objects.aggregate(Sum('doanh_thu_tich_luy'))['doanh_thu_tich_luy__sum'] or 0,
                'so_tai_xe': TaiXe.objects.count()
            },
            'labels_tai_xe': json.dumps([tx.ten_tai_xe for tx in top_tai_xe]),
            'data_doanh_thu': json.dumps([float(tx.doanh_thu_tich_luy or 0) for tx in top_tai_xe]),
            'labels_trang_thai': json.dumps([item['trang_thai'] for item in thong_ke_don]),
            'data_trang_thai': json.dumps([item['so_luong'] for item in thong_ke_don]),
        }
        return render(request, 'home.html', context)
    
    # Cho khách vãng lai tra cứu
    return render(request, 'home.html', {
        'don_hangs': page_obj if q else [],
        'page_obj': page_obj,
        'current_status': status_filter,
        'q': q
    })
# ==============================================================================
# 3. CÔNG CỤ BẢN ĐỒ GIS & TỐI ƯU LỘ TRÌNH (CORE LOGIC)
# ==============================================================================

def chi_tiet(request, ma_don):
    don_hang = get_object_or_404(DonHang, ma_don=ma_don)
    lich_su = don_hang.lich_su_kho.all().order_by('-thoi_gian')
    return render(request, 'map.html', {'dh': don_hang, 'lich_su': lich_su})

@login_required(login_url='core:login')
def ban_do_chung(request):
    if hasattr(request.user, 'taixe'):
        ds_don = DonHang.objects.filter(tai_xe=request.user.taixe)
    else:
        ds_don = DonHang.objects.all()
    return render(request, 'gis.html', {'ds_don': ds_don})

@login_required(login_url='core:login')
def toi_uu_lo_trinh(request):
    ds_tai_xe = TaiXe.objects.all()
    tai_xe_id = request.GET.get('tai_xe_id')
    
    if hasattr(request.user, 'taixe'):
        tx_dang_chon = request.user.taixe
    else:
        tx_dang_chon = TaiXe.objects.filter(id=tai_xe_id).first() if tai_xe_id else None
    
    ds_don = []
    don_hang_json = '[]'

    if tx_dang_chon:
        ds_don = DonHang.objects.filter(tai_xe=tx_dang_chon, trang_thai='ĐANG VẬN CHUYỂN')
        don_data = []
        for d in ds_don:
            don_data.append({
                'ma_don': d.ma_don,
                'ten': d.ten_nguoi_nhan,
                'dia_chi': d.dia_chi_nguoi_nhan,
                'lat': float(d.lat_khach),
                'lng': float(d.lng_khach)
            })
        don_hang_json = json.dumps(don_data)

    return render(request, 'optimize.html', {
        'ds_tai_xe': ds_tai_xe,
        'tx_dang_chon': tx_dang_chon,
        'ds_don': ds_don,
        'don_hang_json': don_hang_json,
    })

# ==============================================================================
# 4. GIAO DIỆN APP SHIPPER (DÀNH CHO TÀI XẾ)
# ==============================================================================

@login_required(login_url='core:login')
def app_shipper(request):
    if not hasattr(request.user, 'taixe'):
        return redirect('core:home')
        
    tai_xe = request.user.taixe
    don_hangs = DonHang.objects.filter(tai_xe=tai_xe).order_by('-id')
    
    return render(request, 'shipper_dashboard.html', {
        'tai_xe': tai_xe, 
        'don_hangs': don_hangs
    })

@login_required(login_url='core:login')
def shipper_cap_nhat(request, don_id):
    """Cập nhật đơn và Gửi Email Mailtrap ngầm (Im lặng)"""
    if request.method == 'POST':
        don = get_object_or_404(DonHang, id=don_id)
        
        if don.tai_xe != request.user.taixe:
            return redirect('core:app_shipper')
            
        trang_thai_moi = request.POST.get('trang_thai') # Tên biến là trang_thai_moi
        don.trang_thai = trang_thai_moi
        don.save()
        
        LichSuKho.objects.create(
            don_hang=don,
            kho=don.kho_xuat_phat,
            trang_thai_buoc=f"SHIPPER CẬP NHẬT: {trang_thai_moi}", # Phải dùng đúng trang_thai_moi
            ghi_chu=f"Cập nhật bởi tài xế: {request.user.username}"
        )
        # ------------------------------
        # GỬI EMAIL NGẦM KHI GIAO THÀNH CÔNG
        if trang_thai_moi == 'ĐÃ GIAO THÀNH CÔNG':
            try:
                subject = f'🎉 Giao hàng thành công - Đơn hàng #{don.ma_don}'
                message = f"Chào {don.ten_nguoi_nhan},\n\nĐơn hàng #{don.ma_don} đã được giao thành công.\nCảm ơn bạn!"
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ['khachhang_test@gmail.com'])
            except:
                pass # Bỏ qua nếu email lỗi để không hiện thông báo cho shipper
            
    return redirect('core:app_shipper')

# ==============================================================================
# 5. QUẢN LÝ TÀI XẾ, KHO, ĐƠN HÀNG, TÀI KHOẢN (ADMIN CRUD - IM LẶNG 100%)
# ==============================================================================

@login_required(login_url='core:login')
def quan_ly_tai_xe(request):
    ds = TaiXe.objects.all()
    q = request.GET.get('q')
    if q: ds = ds.filter(Q(ten_tai_xe__icontains=q) | Q(sdt__icontains=q))
    sort = request.GET.get('sort')
    if sort == 'ten_az': ds = ds.order_by('ten_tai_xe')
    elif sort == 'luong_cao': ds = ds.order_by('-doanh_thu_tich_luy')
    return render(request, 'driver_manager.html', {'ds_tai_xe': ds, 'tong_so_tx': ds.count(), 'dang_online': ds.filter(dang_lam_viec=True).count(), 'ca_sang': ds.filter(ca_lam_viec='SANG').count()})

@login_required(login_url='core:login')
def them_tai_xe(request):
    form = TaiXeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('core:quan_ly_tai_xe')
    return render(request, 'form_taixe.html', {'form': form, 'title': 'Thêm Tài Xế Mới'})

@login_required(login_url='core:login')
def sua_tai_xe(request, id):
    taixe = get_object_or_404(TaiXe, id=id)
    form = TaiXeForm(request.POST or None, instance=taixe)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('core:quan_ly_tai_xe')
    return render(request, 'form_taixe.html', {'form': form, 'title': f'Sửa Tài Xế: {taixe.ten_tai_xe}'})

@login_required(login_url='core:login')
def xoa_tai_xe(request, id):
    get_object_or_404(TaiXe, id=id).delete()
    return redirect('core:quan_ly_tai_xe')

@login_required(login_url='core:login')
def quan_ly_kho(request):
    ds_kho = KhoHang.objects.all()
    q = request.GET.get('q')
    if q: ds_kho = ds_kho.filter(ten_kho__icontains=q)
    return render(request, 'warehouse_manager.html', {'ds_kho': ds_kho})

@login_required(login_url='core:login')
def them_kho(request):
    form = KhoHangForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('core:quan_ly_kho')
    return render(request, 'form_general.html', {'form': form, 'title': 'Thêm Kho Mới', 'back_url': 'core:quan_ly_kho'})

@login_required(login_url='core:login')
def sua_kho(request, id):
    kho = get_object_or_404(KhoHang, id=id)
    form = KhoHangForm(request.POST or None, instance=kho)
    if form.is_valid():
        form.save()
        return redirect('core:quan_ly_kho')
    return render(request, 'form_general.html', {'form': form, 'title': f'Sửa Kho: {kho.ten_kho}', 'back_url': 'core:quan_ly_kho'})

@login_required(login_url='core:login')
def xoa_kho(request, id):
    get_object_or_404(KhoHang, id=id).delete()
    return redirect('core:quan_ly_kho')

@login_required(login_url='core:login')
def quan_ly_don_hang(request):
    ds = DonHang.objects.all().order_by('-ngay_tao')
    q = request.GET.get('q')
    if q: ds = ds.filter(Q(ma_don__icontains=q) | Q(ten_nguoi_nhan__icontains=q))
    sort = request.GET.get('sort')
    if sort == 'trang_thai': ds = ds.order_by('trang_thai')
    return render(request, 'order_manager.html', {'ds_don': ds})

@login_required(login_url='core:login')
def them_don_hang(request):
    """
    Hàm chuẩn: Giữ 100% giao diện Map/GIS từ Form chung
    nhưng chèn thêm logic bắn Email thông báo.
    """
    # Sử dụng đúng cái Form mà ông đã định nghĩa (để hiện đủ Kho, Shipper, KG...)
    form = DonHangForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        # 1. Lưu đơn hàng
        don = form.save()
        
        # 2. Logic gửi Mail (Chạy ngầm, không làm hỏng giao diện)
        try:
            subject = f"📦 ĐƠN HÀNG MỚI: #{don.ma_don}"
            message = (
                f"Thông báo: Admin vừa tạo đơn mới.\n\n"
                f"Khách hàng: {don.ten_nguoi_nhan}\n"
                f"Địa chỉ: {don.dia_chi_nguoi_nhan}\n"
                f"Khối lượng: {don.khoi_luong} kg"
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.EMAIL_HOST_USER])
        except:
            pass # Nếu mail lỗi thì thôi, vẫn cho Admin lưu đơn bình thường
            
        return redirect('core:quan_ly_don_hang')

    # Trả về form_general.html để nó vẽ cái Map và các ô nhập liệu Poppins của ông
    return render(request, 'form_general.html', {
        'form': form, 
        'title': 'Tạo Đơn Hàng Mới', 
        'back_url': 'core:quan_ly_don_hang'
    })

@login_required(login_url='core:login')
def sua_don_hang(request, id):
    don = get_object_or_404(DonHang, id=id)
    form = DonHangForm(request.POST or None, instance=don)
    if form.is_valid():
        form.save()
        return redirect('core:quan_ly_don_hang')
    return render(request, 'form_general.html', {'form': form, 'title': f'Cập nhật Đơn: {don.ma_don}', 'back_url': 'core:quan_ly_don_hang'})

@login_required(login_url='core:login')
def xoa_don_hang(request, id):
    get_object_or_404(DonHang, id=id).delete()
    return redirect('core:quan_ly_don_hang')

@login_required(login_url='core:login')
def quan_ly_tai_khoan(request):
    if not request.user.is_staff: return redirect('core:home')
    ds_tk = User.objects.all().order_by('-id')
    q = request.GET.get('q')
    if q: ds_tk = ds_tk.filter(username__icontains=q)
    return render(request, 'account_manager.html', {'ds_tai_khoan': ds_tk})

@login_required(login_url='core:login')
def them_tai_khoan(request):
    if not request.user.is_staff: return redirect('core:home')
    form = TaiKhoanForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('core:quan_ly_tai_khoan')
    return render(request, 'form_taikhoan.html', {'form': form, 'title': 'Tạo Tài Khoản Mới', 'back_url': 'core:quan_ly_tai_khoan'})

@login_required(login_url='core:login')
def sua_tai_khoan(request, id):
    if not request.user.is_staff: return redirect('core:home')
    tk = get_object_or_404(User, id=id)
    form = TaiKhoanForm(request.POST or None, instance=tk)
    if form.is_valid():
        form.save()
        return redirect('core:quan_ly_tai_khoan')
    return render(request, 'form_taikhoan.html', {'form': form, 'title': f'Sửa Tài Khoản: {tk.username}', 'back_url': 'core:quan_ly_tai_khoan'})

@login_required(login_url='core:login')
def xoa_tai_khoan(request, id):
    if not request.user.is_staff: return redirect('core:home')
    tk = get_object_or_404(User, id=id)
    if tk.id != request.user.id:
        tk.delete()
    return redirect('core:quan_ly_tai_khoan')

# --- CỔNG API NHẬN ĐƠN B2B ---
# --- CỬA HẬU: API nhận đơn từ Shopee/Tiktok ---
# Trong views.py
@api_view(['POST'])
def api_tao_don_hang(request):
    """Cổng API nhận đơn hàng từ đối tác (Đã fix lỗi sập server)"""
    serializer = DonHangSerializer(data=request.data)
    
    if serializer.is_valid():
        # 1. Lưu đơn hàng vào Database trước
        don = serializer.save(trang_thai='CHO_LAY_HANG') 
        
        # 2. Gửi mail thông báo (Bọc trong try-except để tránh lỗi 500)
        try:
            subject = f"🔔 API: ĐƠN HÀNG MỚI #{don.ma_don}"
            message = f"Hệ thống vừa nhận đơn từ API.\nKhách: {don.ten_nguoi_nhan}\nĐịa chỉ: {don.dia_chi_nguoi_nhan}"
            send_mail(
                subject, 
                message, 
                settings.DEFAULT_FROM_EMAIL, 
                [settings.EMAIL_HOST_USER],
                fail_silently=True # Thêm dòng này để nó "im lặng" nếu lỗi mail
            )
        except Exception as e:
            print(f"Lỗi gửi mail API: {e}") # Chỉ in ra console chứ không làm sập server

        return Response({
            "status": "success",
            "message": "Đã tiếp nhận vận đơn từ API!",
            "ma_don": don.ma_don
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # 2. XỬ LÝ PHÂN TRANG (5 đơn / 1 trang)

    paginator = Paginator(ds_don, 5) # Ông muốn mấy đơn 1 trang thì đổi số 5 nhé
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.user.is_authenticated:
        if hasattr(request.user, 'taixe'): 
            return redirect('core:app_shipper')
        
        top_tai_xe = TaiXe.objects.order_by('-doanh_thu_tich_luy')[:5]
        thong_ke_don = DonHang.objects.values('trang_thai').annotate(so_luong=Count('id'))

        context = {
            'don_hangs': page_obj, # Truyền page_obj thay vì ds_don
            'page_obj': page_obj,  # Để dùng vẽ nút phân trang
            'current_status': status_filter,
            'q': q,
            'stats': {
                'tong_don': DonHang.objects.count(),
                'don_dang_giao': DonHang.objects.filter(trang_thai='ĐANG VẬN CHUYỂN').count(),
                'tong_doanh_thu': TaiXe.objects.aggregate(Sum('doanh_thu_tich_luy'))['doanh_thu_tich_luy__sum'] or 0,
                'so_tai_xe': TaiXe.objects.count()
            },
            'labels_tai_xe': json.dumps([tx.ten_tai_xe for tx in top_tai_xe]),
            'data_doanh_thu': json.dumps([float(tx.doanh_thu_tich_luy or 0) for tx in top_tai_xe]),
            'labels_trang_thai': json.dumps([item['trang_thai'] for item in thong_ke_don]),
            'data_trang_thai': json.dumps([item['so_luong'] for item in thong_ke_don]),
        }
        return render(request, 'home.html', context)
    
    return render(request, 'home.html', {
        'don_hangs': page_obj if q else [],
        'page_obj': page_obj,
        'current_status': status_filter,
        'q': q
    })
# 1. XUẤT EXCEL
def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Danh_sach_don_hang.xlsx"'
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Đơn Hàng"
    
    # Header
    columns = ['Mã Đơn', 'Khách Hàng', 'Địa Chỉ', 'Số Điện Thoại', 'Trạng Thái']
    ws.append(columns)
    
    # Lấy dữ liệu (giống hàm home của ông)
    queryset = DonHang.objects.all()
    # ... (Ông có thể copy đoạn lọc q và status từ hàm home vào đây để xuất đúng số lượng đang thấy)
    
    for dh in queryset:
        ws.append([dh.ma_don, dh.ten_nguoi_nhan, dh.dia_chi_nguoi_nhan, dh.sdt_nguoi_nhan, dh.trang_thai])
        
    wb.save(response)
    return response

@login_required
def cap_nhat_kho(request, don_id):
    if request.method == 'POST':
        don = get_object_or_404(DonHang, id=don_id)
        kho_id = request.POST.get('kho_id')
        hanh_dong = request.POST.get('hanh_dong') # NHAP_KHO hoặc XUAT_KHO
        
        kho = get_object_or_404(KhoHang, id=kho_id)
        
        # 1. Ghi lại lịch sử
        LichSuKho.objects.create(
        don_hang=don,
        kho=kho, # Sửa từ kho_den thành kho
        trang_thai_buoc=hanh_dong, # Sửa từ trang_thai_kho thành trang_thai_buoc
        ghi_chu=f"Đơn hàng {hanh_dong.lower()} tại {kho.ten_kho}"
    )
        
        # 2. Cập nhật trạng thái hiển thị của đơn hàng
        don.trang_thai = f"ĐÃ {hanh_dong} - {kho.ten_kho}"
        don.save()
        
    return redirect('core:quan_ly_don_hang')

@login_required(login_url='core:login')
def quan_ly_lich_su(request):
    """Trang danh sách lịch sử luân chuyển"""
    ds = LichSuKho.objects.all().order_by('-thoi_gian')
    q = request.GET.get('q')
    if q:
        ds = ds.filter(Q(don_hang__ma_don__icontains=q) | Q(trang_thai_buoc__icontains=q))
    
    return render(request, 'history_manager.html', {
        'ds_lich_su': ds,
        'title': 'Quản lý Luân chuyển Kho'
    })

@login_required(login_url='core:login')
def them_lich_su(request):
    """Thêm mới một bước luân chuyển"""
    form = LichSuKhoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('core:quan_ly_lich_su')
    return render(request, 'form_general.html', {
        'form': form, 
        'title': 'Thêm Nhật ký Luân chuyển',
        'back_url': 'core:quan_ly_lich_su'
    })

@login_required(login_url='core:login')
def xoa_lich_su(request, id):
    """Xóa nhật ký"""
    get_object_or_404(LichSuKho, id=id).delete()
    return redirect('core:quan_ly_lich_su')

import random
from datetime import datetime

@login_required
def gia_lap_nhan_don(request):
    """Hàm tạo nhanh đơn hàng để giả vờ như có bên ngoài đẩy đơn vào"""
    ten_khach = ['Nguyễn Văn A', 'Trần Thị B', 'Lê Văn C', 'Phạm Minh D']
    dia_chi = ['123 Lê Lợi, Q1', '456 Cộng Hòa, Tân Bình', '789 Mai Chí Thọ, Thủ Đức']
    
    kho_list = KhoHang.objects.all()
    
    for _ in range(3): # Tạo 3 đơn mỗi lần bấm
        don = DonHang.objects.create(
            ten_nguoi_nhan=random.choice(ten_khach),
            dia_chi_nguoi_nhan=random.choice(dia_chi),
            sdt_nguoi_nhan='0901234567',
            lat_khach=10.77 + random.uniform(-0.05, 0.05),
            lng_khach=106.69 + random.uniform(-0.05, 0.05),
            khoi_luong=random.uniform(0.5, 10),
            kho_xuat_phat=random.choice(kho_list),
            trang_thai='CHỜ LẤY HÀNG'
        )
        # Ghi nhật ký tự động cho đơn vừa nhận
        LichSuKho.objects.create(
            don_hang=don,
            kho=don.kho_xuat_phat,
            trang_thai_buoc='HỆ THỐNG: TIẾP NHẬN ĐƠN',
            ghi_chu="Đơn hàng được tiếp nhận tự động từ cổng API đối tác."
        )
        
    messages.success(request, "🚀 Đã nhận thêm 3 đơn hàng mới từ cổng kết nối!")
    return redirect('core:quan_ly_don_hang')

@login_required
def partner_demo_tao_don(request):
    """Trang giả lập dành cho đối tác (Shopee/TikTok) tự đẩy đơn vào hệ thống"""
    # Lấy danh sách kho để đối tác chọn kho gửi hàng
    ds_kho = KhoHang.objects.all()
    
    if request.method == 'POST':
        # 1. Lấy dữ liệu từ Form HTML
        ten = request.POST.get('ten_nguoi_nhan')
        sdt = request.POST.get('sdt_nguoi_nhan')
        dia_chi = request.POST.get('dia_chi_nguoi_nhan')
        kho_id = request.POST.get('kho_xuat_phat')
        khoi_luong = request.POST.get('khoi_luong', 1.0)
        
        # Tọa độ giả lập quanh khu vực HCM để bản đồ hiện đẹp
        import random
        lat = 10.7 + random.uniform(0.01, 0.1)
        lng = 106.6 + random.uniform(0.01, 0.1)
        
        # 2. Tạo đơn hàng mới
        kho_gui = get_object_or_404(KhoHang, id=kho_id)
        don = DonHang.objects.create(
            ten_nguoi_nhan=ten,
            sdt_nguoi_nhan=sdt,
            dia_chi_nguoi_nhan=dia_chi,
            lat_khach=lat,
            lng_khach=lng,
            khoi_luong=khoi_luong,
            kho_xuat_phat=kho_gui,
            trang_thai='CHỜ LẤY HÀNG'
        )
        
        # 3. TỰ ĐỘNG tạo luôn nhật ký bước đầu tiên
        LichSuKho.objects.create(
            don_hang=don,
            kho=kho_gui,
            trang_thai_buoc='NHẬP KHO',
            ghi_chu=f"Đơn hàng được khởi tạo từ Cổng đối tác (Demo)."
        )
        
        messages.success(request, f"🚀 Đã đẩy thành công đơn #{don.ma_don} vào hệ thống!")
        return redirect('core:quan_ly_don_hang')

    return render(request, 'partner_demo.html', {'ds_kho': ds_kho})

# Trong views.py
def partner_demo_tao_don(request):
    """Cổng dành cho đối tác: Tạo đơn và đẩy về trung tâm điều phối của Admin"""
    ds_kho = KhoHang.objects.all() # Lấy danh sách kho để đối tác chọn
    
    if request.method == 'POST':
        # 1. Thu thập dữ liệu từ Form (giống hệt Form của Admin)
        ten = request.POST.get('ten_nguoi_nhan')
        sdt = request.POST.get('sdt_nguoi_nhan')
        dia_chi = request.POST.get('dia_chi_nguoi_nhan')
        lat = request.POST.get('lat_khach')
        lng = request.POST.get('lng_khach')
        kho_id = request.POST.get('kho_xuat_phat')
        khoi_luong = request.POST.get('khoi_luong')

        # 2. Tạo đơn hàng vào bảng chung DonHang
        kho_gui = get_object_or_404(KhoHang, id=kho_id)
        don = DonHang.objects.create(
            ten_nguoi_nhan=ten,
            sdt_nguoi_nhan=sdt,
            dia_chi_nguoi_nhan=dia_chi,
            lat_khach=lat,
            lng_khach=lng,
            khoi_luong=khoi_luong,
            kho_xuat_phat=kho_gui,
            trang_thai='CHỜ LẤY HÀNG' # Trạng thái mặc định để Admin biết đơn mới
        )

        # 3. TỰ ĐỘNG tạo Nhật ký để Admin theo dõi lộ trình
        LichSuKho.objects.create(
            don_hang=don,
            kho=kho_gui,
            trang_thai_buoc='NHẬP KHO',
            ghi_chu=f"Đơn hàng được khởi tạo từ Đối tác B2B."
        )

        # Trả về trang thông báo thành công cho đối tác
        return render(request, 'partner_success.html', {'don': don})

    # Dòng quan trọng: Trả về giao diện khi truy cập bằng GET
    return render(request, 'partner_demo.html', {'ds_kho': ds_kho})

# Trong views.py
from django.http import JsonResponse

# Dán vào cuối views.py
def check_new_orders(request):
    """Hàm này là 'mắt thần' để cái chuông nó thấy đơn mới"""
    # Lấy đúng các đơn có trạng thái giống trong hình của ông
    moi = DonHang.objects.filter(trang_thai='CHỜ LẤY HÀNG').order_by('-id')
    
    data = {
        'count': moi.count(),
        'orders': [
            {'ma_don': d.ma_don, 'khach': d.ten_nguoi_nhan, 'ngay': d.ngay_tao.strftime('%H:%M')} 
            for d in moi[:5] # Chỉ hiện 5 đơn mới nhất cho đẹp
        ]
    }
    return JsonResponse(data)