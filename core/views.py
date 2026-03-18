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

# Import models và forms từ thư mục core
from .models import KhoHang, TaiXe, DonHang 
from .forms import TaiXeForm, KhoHangForm, DonHangForm, TaiKhoanForm

# ==============================================================================
# 1. HỆ THỐNG XÁC THỰC & ĐIỀU HƯỚNG (AUTHENTICATION)
# ==============================================================================

def dang_nhap(request):
    """Xử lý đăng nhập: KHÔNG báo thành công, CHỈ báo lỗi khi sai tài khoản"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'taixe'):
            return redirect('core:app_shipper')
        return redirect('core:home')

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        user = authenticate(request, username=u, password=p)
        
        if user is not None:
            login(request, user)
            if hasattr(user, 'taixe'):
                return redirect('core:app_shipper')
            return redirect('core:home')
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
    """Trang chủ hiển thị dashboard và cho phép khách tra cứu đơn hàng"""
    q = request.GET.get('q', '')
    ds_don = DonHang.objects.all().order_by('-id')
    
    if q:
        ds_don = ds_don.filter(Q(ma_don__icontains=q) | Q(sdt_nguoi_nhan__icontains=q))

    if request.user.is_authenticated:
        if hasattr(request.user, 'taixe'): 
            return redirect('core:app_shipper')
        
        top_tai_xe = TaiXe.objects.order_by('-doanh_thu_tich_luy')[:5]
        thong_ke_don = DonHang.objects.values('trang_thai').annotate(so_luong=Count('id'))

        context = {
            'don_hangs': ds_don if q else ds_don[:10],
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
            'q': q
        }
        return render(request, 'home.html', context)
    
    return render(request, 'home.html', {
        'don_hangs': ds_don if q else [],  # <--- THAY ĐỔI TẠI ĐÂY
        'q': q
    })

# ==============================================================================
# 3. CÔNG CỤ BẢN ĐỒ GIS & TỐI ƯU LỘ TRÌNH (CORE LOGIC)
# ==============================================================================

def chi_tiet(request, ma_don):
    don_hang = get_object_or_404(DonHang, ma_don=ma_don)
    return render(request, 'map.html', {'dh': don_hang})

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
            
        trang_thai_moi = request.POST.get('trang_thai')
        don.trang_thai = trang_thai_moi
        don.save()
        
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
    form = DonHangForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('core:quan_ly_don_hang')
    return render(request, 'form_general.html', {'form': form, 'title': 'Tạo Đơn Hàng Mới', 'back_url': 'core:quan_ly_don_hang'})

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