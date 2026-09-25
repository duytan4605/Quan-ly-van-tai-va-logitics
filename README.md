# 🚚 Quản Lý Vận Tải và Logistics

Hệ thống quản lý vận tải và logistics xây dựng trên nền tảng **Django**, hỗ trợ quản lý dữ liệu vận tải, xuất/nhập báo cáo và cung cấp API cho các ứng dụng khác.

> **Ghi chú:** phần "Tính năng" bên dưới được suy ra từ cấu trúc thư mục và các thư viện trong `requirements.txt`, vì công cụ tự động không thể duyệt sâu vào mã nguồn trong `core/`. Bạn nên chỉnh sửa lại phần này cho khớp chính xác với nghiệp vụ thực tế của ứng dụng.

## 📋 Giới thiệu

`Quan-ly-van-tai-va-logitics` là một ứng dụng web viết bằng Python/Django, gồm giao diện quản trị dựng bằng Django templates và một lớp API (Django REST Framework) phục vụ các nghiệp vụ vận tải – logistics.

## ✨ Tính năng chính

- Quản lý dữ liệu vận tải/logistics qua giao diện web và REST API
- Nhập/xuất dữ liệu Excel (`openpyxl`, `pandas`, `django-import-export`)
- Xuất báo cáo/chứng từ dạng PDF, hỗ trợ ký số PDF (`xhtml2pdf`, `reportlab`, `pyHanko`)
- Hiển thị bản đồ, định vị và tính khoảng cách tuyến đường (`folium`, `geopy`, `geographiclib`)
- Hỗ trợ phân tích dữ liệu (`pandas`, `numpy`, `scipy`, `scikit-learn`)
- Kết nối cơ sở dữ liệu SQL Server qua `mssql-django` (kèm sẵn `db.sqlite3` để chạy thử nhanh)
- Bộ Postman collection (`.postman/`) để kiểm thử API

## 🛠️ Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Backend | Python, Django 6.0 |
| API | Django REST Framework |
| Cơ sở dữ liệu | SQL Server (`mssql-django`) / SQLite (mặc định) |
| Xuất/nhập Excel | openpyxl, pandas, django-import-export |
| Xuất PDF | xhtml2pdf, reportlab, pyHanko |
| Bản đồ & định vị | folium, geopy, geographiclib |
| Phân tích dữ liệu | numpy, scipy, scikit-learn |
| Kiểm thử API | Postman |

## 📁 Cấu trúc thư mục

```
Quan-ly-van-tai-va-logitics/
├── LogisticsProject/   # Cấu hình chính của Django (settings.py, urls.py, wsgi.py, asgi.py)
├── core/               # Ứng dụng Django chính (models, views, forms, ...)
├── templates/          # Giao diện HTML
├── static/             # CSS, JavaScript, hình ảnh tĩnh
├── Document/           # Tài liệu dự án
├── .postman/           # Postman collection để kiểm thử API
├── manage.py           # Script quản lý Django
├── db.sqlite3          # CSDL SQLite mặc định (dùng khi phát triển)
├── requirements.txt    # Danh sách thư viện Python cần cài
└── .gitattributes
```

## ⚙️ Yêu cầu hệ thống

- Python 3.10+
- pip
- (Tuỳ chọn) Microsoft SQL Server + ODBC Driver 17/18, nếu muốn dùng SQL Server thay vì SQLite

## 🚀 Cài đặt và chạy thử

1. **Clone repository**
   ```bash
   git clone https://github.com/duytan4605/Quan-ly-van-tai-va-logitics.git
   cd Quan-ly-van-tai-va-logitics
   ```

2. **Tạo và kích hoạt môi trường ảo**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Cài đặt thư viện**
   ```bash
   pip install -r requirements.txt
   ```

4. **Cấu hình cơ sở dữ liệu**
   - Dự án có sẵn `db.sqlite3` nên có thể chạy ngay mà không cần cấu hình thêm.
   - Nếu muốn dùng SQL Server, chỉnh phần `DATABASES` trong `LogisticsProject/settings.py` theo thông tin server của bạn (`mssql-django`, `pyodbc` đã có sẵn trong `requirements.txt`, cần cài thêm ODBC Driver cho SQL Server).

5. **Chạy migrate**
   ```bash
   python manage.py migrate
   ```

6. **Tạo tài khoản quản trị**
   ```bash
   python manage.py createsuperuser
   ```

7. **Khởi chạy server**
   ```bash
   python manage.py runserver
   ```
   Truy cập ứng dụng tại `http://127.0.0.1:8000/` và trang quản trị tại `http://127.0.0.1:8000/admin/`.

## 🧪 Kiểm thử API

Import bộ collection trong thư mục [`.postman/`](./.postman) vào [Postman](https://www.postman.com/) để gọi thử các endpoint REST.

## 📚 Tài liệu

Xem thêm tài liệu chi tiết trong thư mục [`Document/`](./Document).

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh:

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/ten-tinh-nang`)
3. Commit thay đổi (`git commit -m "Thêm tính năng ..."`)
4. Push branch (`git push origin feature/ten-tinh-nang`)
5. Tạo Pull Request

## 📄 Giấy phép

Dự án hiện chưa có giấy phép cụ thể. Nếu muốn công khai điều khoản sử dụng, hãy thêm file `LICENSE` phù hợp (MIT, Apache 2.0, ...).

## 👤 Tác giả

- **duytan4605** – [GitHub](https://github.com/duytan4605)
