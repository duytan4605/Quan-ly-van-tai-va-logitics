from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q  # 👉 Dùng để tìm kiếm nâng cao (Tên HOẶC SĐT)
from .models import KhoHang, TaiXe, DonHang 
from .forms import TaiXeForm, KhoHangForm, DonHangForm

# ==================== CÁC VIEW NGƯỜI DÙNG (USER VIEWS) ====================

# 1. Trang chủ (Danh sách đơn hàng)
def home(request):
    tat_ca_don_hang = DonHang.objects.all()
    context = {
        'don_hangs': tat_ca_don_hang,
    }
    return render(request, 'home.html', context)

# 2. Chi tiết (Xem lộ trình 1 đơn hàng & Tính cước)
def chi_tiet(request, ma_don):
    don_hang = get_object_or_404(DonHang, ma_don=ma_don)
    context = {
        'dh': don_hang,
    }
    return render(request, 'map.html', context)

# 3. Bản đồ chung (GIS Dashboard - Xem tất cả xe)
def ban_do_chung(request):
    tat_ca_don_hang = DonHang.objects.all()
    context = {
        'ds_don': tat_ca_don_hang,
    }
    return render(request, 'gis.html', context)

# 4. Tối ưu lộ trình (TSP Algorithm)
def toi_uu_lo_trinh(request):
    ds_don = DonHang.objects.all()
    context = {
        'ds_don': ds_don,
    }
    return render(request, 'optimize.html', context)


# ==================== 1. QUẢN LÝ TÀI XẾ (CUSTOM ADMIN) ====================

def quan_ly_tai_xe(request):
    ds_tai_xe = TaiXe.objects.all()
    
    # --- TÌM KIẾM (SEARCH) ---
    query = request.GET.get('q')
    if query:
        # Tìm theo Tên HOẶC Số điện thoại
        ds_tai_xe = ds_tai_xe.filter(
            Q(ten_tai_xe__icontains=query) | 
            Q(sdt__icontains=query)
        )

    # --- SẮP XẾP (SORT) ---
    sort_by = request.GET.get('sort')
    if sort_by == 'ten_az':
        ds_tai_xe = ds_tai_xe.order_by('ten_tai_xe')
    elif sort_by == 'kpi_cao':
        ds_tai_xe = ds_tai_xe.order_by('-tong_don_thang_nay') # Cao xuống thấp
    elif sort_by == 'luong_cao':
        ds_tai_xe = ds_tai_xe.order_by('-doanh_thu_tich_luy')

    # Tính toán KPI
    tong_so = ds_tai_xe.count()
    online = ds_tai_xe.filter(dang_lam_viec=True).count()
    ca_sang = ds_tai_xe.filter(ca_lam_viec='SANG').count()
    
    context = {
        'ds_tai_xe': ds_tai_xe,
        'tong_so_tx': tong_so,
        'dang_online': online,
        'ca_sang': ca_sang,
    }
    return render(request, 'driver_manager.html', context)

# Chức năng THÊM MỚI Tài xế
def them_tai_xe(request):
    if request.method == 'POST':
        form = TaiXeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:quan_ly_tai_xe')
    else:
        form = TaiXeForm()
    return render(request, 'form_taixe.html', {'form': form, 'title': 'Thêm Tài Xế Mới'})

# Chức năng SỬA Tài xế
def sua_tai_xe(request, id):
    taixe = get_object_or_404(TaiXe, id=id)
    if request.method == 'POST':
        form = TaiXeForm(request.POST, instance=taixe)
        if form.is_valid():
            form.save()
            return redirect('core:quan_ly_tai_xe')
    else:
        form = TaiXeForm(instance=taixe)
    return render(request, 'form_taixe.html', {'form': form, 'title': f'Sửa thông tin: {taixe.ten_tai_xe}'})

# Chức năng XÓA Tài xế
def xoa_tai_xe(request, id):
    taixe = get_object_or_404(TaiXe, id=id)
    taixe.delete()
    return redirect('core:quan_ly_tai_xe')


# ==================== 2. QUẢN LÝ KHO HÀNG ====================

def quan_ly_kho(request):
    ds_kho = KhoHang.objects.all()

    # --- TÌM KIẾM ---
    query = request.GET.get('q')
    if query:
        ds_kho = ds_kho.filter(ten_kho__icontains=query)

    # --- SẮP XẾP ---
    sort_by = request.GET.get('sort')
    if sort_by == 'ten_az':
        ds_kho = ds_kho.order_by('ten_kho')

    return render(request, 'warehouse_manager.html', {'ds_kho': ds_kho})

def them_kho(request):
    if request.method == 'POST':
        form = KhoHangForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:quan_ly_kho')
    else:
        form = KhoHangForm()
    return render(request, 'form_general.html', {'form': form, 'title': 'Thêm Kho Mới', 'back_url': 'core:quan_ly_kho'})

def sua_kho(request, id):
    kho = get_object_or_404(KhoHang, id=id)
    if request.method == 'POST':
        form = KhoHangForm(request.POST, instance=kho)
        if form.is_valid():
            form.save()
            return redirect('core:quan_ly_kho')
    else:
        form = KhoHangForm(instance=kho)
    return render(request, 'form_general.html', {'form': form, 'title': f'Sửa Kho: {kho.ten_kho}', 'back_url': 'core:quan_ly_kho'})

def xoa_kho(request, id):
    kho = get_object_or_404(KhoHang, id=id)
    kho.delete()
    return redirect('core:quan_ly_kho')


# ==================== 3. QUẢN LÝ ĐƠN HÀNG ====================

def quan_ly_don_hang(request):
    ds_don = DonHang.objects.all()

    # --- TÌM KIẾM ---
    query = request.GET.get('q')
    if query:
        ds_don = ds_don.filter(
            Q(ma_don__icontains=query) | 
            Q(ten_nguoi_nhan__icontains=query)
        )

    # --- SẮP XẾP ---
    sort_by = request.GET.get('sort')
    if sort_by == 'moi_nhat':
        ds_don = ds_don.order_by('-ngay_tao')
    elif sort_by == 'trang_thai':
        ds_don = ds_don.order_by('trang_thai')

    return render(request, 'order_manager.html', {'ds_don': ds_don})

def them_don_hang(request):
    if request.method == 'POST':
        form = DonHangForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:quan_ly_don_hang')
    else:
        form = DonHangForm()
    return render(request, 'form_general.html', {'form': form, 'title': 'Tạo Đơn Hàng Mới', 'back_url': 'core:quan_ly_don_hang'})

def sua_don_hang(request, id):
    don = get_object_or_404(DonHang, id=id)
    if request.method == 'POST':
        form = DonHangForm(request.POST, instance=don)
        if form.is_valid():
            form.save()
            return redirect('core:quan_ly_don_hang')
    else:
        form = DonHangForm(instance=don)
    return render(request, 'form_general.html', {'form': form, 'title': f'Cập nhật Đơn: {don.ma_don}', 'back_url': 'core:quan_ly_don_hang'})

def xoa_don_hang(request, id):
    don = get_object_or_404(DonHang, id=id)
    don.delete()
    return redirect('core:quan_ly_don_hang')