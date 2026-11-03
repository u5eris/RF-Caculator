# Hướng dẫn cài đặt và chạy web tính toán đường truyền (Flask) trên máy local

## Tổng quan

Sau khoảng 15–20 phút làm theo 5 bước dưới đây, bạn sẽ mở được web tính toán (cáp đồng trục, ống dẫn sóng, microstrip, đường hai dây) tại địa chỉ http://127.0.0.1:5000 trên máy của mình. Web chạy bằng Python với framework Flask, nên máy chỉ cần Python, Git và hai thư viện Flask, SciPy.

Bạn cần chuẩn bị:

- Máy tính Windows 10/11, macOS hoặc Linux, có kết nối Internet
- Khoảng 500 MB dung lượng trống (chủ yếu cho Python và SciPy)
- Một trình duyệt bất kỳ (Chrome, Edge, Firefox, Safari)

Các lệnh trong hướng dẫn được gõ vào **cửa sổ dòng lệnh**: trên Windows là *Command Prompt* hoặc *PowerShell* (bấm phím Windows, gõ `cmd`), trên macOS là *Terminal* (bấm Cmd + Space, gõ `Terminal`).

## Bước 1: Cài Python

Cài Python 3.10 trở lên (khuyên dùng bản 3.12) từ trang chính thức https://www.python.org/downloads/.

**Windows**

1. Tải file cài đặt (nút *Download Python 3.x.x*) và mở nó.
2. Ở màn hình đầu tiên, **tick vào ô "Add python.exe to PATH"** ở phía dưới. Đây là bước người mới hay quên nhất.
3. Bấm *Install Now* và chờ cài xong.

**macOS**

1. Tải file `.pkg` từ python.org, mở và bấm *Continue* cho đến khi xong.
2. Trên macOS, các lệnh bên dưới dùng `python3` và `pip3` thay cho `python` và `pip`.

**Linux (Ubuntu/Debian)**

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

**Kiểm tra:** mở cửa sổ dòng lệnh **mới** và gõ:

```bash
python --version
```

Nếu hiện `Python 3.12.x` (hoặc 3.10 trở lên) là thành công. Trên macOS/Linux gõ `python3 --version`.

## Bước 2: Tải dự án từ GitHub

Có hai cách; cách A tiện hơn nếu sau này bạn muốn cập nhật code, cách B không cần cài gì thêm.

**Cách A: dùng Git (khuyên dùng)**

1. Cài Git từ https://git-scm.com/downloads (Windows: cứ bấm *Next* với tùy chọn mặc định). Trên macOS, gõ `git --version` trong Terminal, máy sẽ tự đề nghị cài. Trên Ubuntu: `sudo apt install git`.
2. Kiểm tra bằng lệnh `git --version`.
3. Di chuyển tới thư mục muốn lưu dự án rồi tải về (thay đường link bằng link repo của bạn):

```bash
cd Desktop
git clone https://github.com/<ten-tai-khoan>/<ten-repo>.git
cd <ten-repo>
```

**Cách B: tải file ZIP**

1. Mở trang repo trên GitHub, bấm nút xanh **Code** → **Download ZIP**.
2. Giải nén file ZIP ra một thư mục, ví dụ trên Desktop.
3. Mở cửa sổ dòng lệnh và `cd` vào thư mục vừa giải nén, ví dụ `cd Desktop\<ten-repo>-main`.

Mẹo trên Windows: mở thư mục dự án trong File Explorer, gõ `cmd` vào thanh địa chỉ rồi Enter, cửa sổ dòng lệnh sẽ mở sẵn đúng thư mục đó.

## Bước 3: Kiểm tra cấu trúc thư mục

Flask chỉ tìm giao diện trong thư mục `templates/` và ảnh trong thư mục `static/`, nên nếu `index.html` nằm chung chỗ với `app.py` thì web sẽ báo lỗi `TemplateNotFound`. Thư mục dự án cần có dạng:

```
ten-repo/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    └── images/
        ├── model.jpg
        ├── model1.jpg
        └── ... (các ảnh model khác mà index.html dùng)
```

Nếu repo của bạn chưa đúng như trên, hãy tạo thư mục `templates`, chuyển `index.html` vào đó, và đặt các ảnh vào `static/images/`. Nên sửa luôn trên GitHub để người khác clone về là chạy được ngay.

Tạo thêm file `requirements.txt` cạnh `app.py` với nội dung:

```
flask
scipy
```

File này liệt kê các thư viện cần cài, giúp người mới chỉ cần một lệnh ở bước sau.

## Bước 4: Tạo môi trường ảo và cài thư viện

Môi trường ảo (virtual environment) là một "hộp riêng" chứa thư viện cho dự án này, tránh xung đột với các dự án Python khác. Mọi lệnh dưới đây chạy **bên trong thư mục dự án** (thư mục có `app.py`).

**1. Tạo môi trường ảo** (chỉ làm một lần):

```bash
python -m venv venv
```

macOS/Linux: `python3 -m venv venv`. Lệnh này tạo thư mục `venv` trong dự án.

**2. Kích hoạt môi trường ảo:**

| Hệ điều hành | Lệnh |
| --- | --- |
| Windows (Command Prompt) | `venv\Scripts\activate` |
| Windows (PowerShell) | `venv\Scripts\Activate.ps1` |
| macOS / Linux | `source venv/bin/activate` |

Kích hoạt thành công khi đầu dòng lệnh hiện chữ `(venv)`.

**3. Cài thư viện:**

```bash
pip install -r requirements.txt
```

Nếu chưa có `requirements.txt`, gõ thẳng `pip install flask scipy`. SciPy khá nặng nên có thể mất vài phút.

Nên thêm dòng `venv/` vào file `.gitignore` để không đẩy thư mục môi trường ảo lên GitHub.

## Bước 5: Chạy web

Với môi trường ảo đã kích hoạt (có `(venv)` ở đầu dòng), gõ:

```bash
python app.py
```

Nếu thành công, màn hình hiện mấy dòng tương tự:

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

Mở trình duyệt và vào địa chỉ **http://127.0.0.1:5000** (hoặc http://localhost:5000). Giao diện tính toán sẽ hiện ra. Giữ nguyên cửa sổ dòng lệnh trong lúc dùng web; đóng nó là web tắt.

Vì app đang bật chế độ debug, khi bạn sửa `app.py` và lưu lại, server sẽ tự khởi động lại; chỉ cần tải lại trang (F5).

## Dừng web và những lần chạy sau

**Dừng web:** bấm `Ctrl + C` trong cửa sổ dòng lệnh đang chạy server.

**Lần sau muốn chạy lại**, không cần cài lại gì, chỉ cần 3 lệnh:

1. `cd` vào thư mục dự án.
2. Kích hoạt môi trường ảo (`venv\Scripts\activate` trên Windows, `source venv/bin/activate` trên macOS/Linux).
3. `python app.py`, rồi mở http://127.0.0.1:5000.

**Cập nhật code mới từ GitHub** (nếu tải bằng Git): chạy `git pull` trong thư mục dự án, sau đó `pip install -r requirements.txt` nếu có thư viện mới.

## Xử lý lỗi thường gặp

| Lỗi hoặc hiện tượng | Nguyên nhân | Cách sửa |
| --- | --- | --- |
| `'python' is not recognized...` | Quên tick "Add python.exe to PATH" khi cài | Chạy lại file cài Python, chọn *Modify* hoặc gỡ ra cài lại và tick ô đó; hoặc thử lệnh `py` thay cho `python` |
| `ModuleNotFoundError: No module named 'flask'` (hoặc `'scipy'`) | Chưa kích hoạt `venv` hoặc chưa cài thư viện | Kích hoạt môi trường ảo (Bước 4) rồi chạy lại `pip install -r requirements.txt` |
| `jinja2.exceptions.TemplateNotFound: index.html` | `index.html` không nằm trong thư mục `templates/` | Sắp xếp lại theo Bước 3 |
| Web chạy nhưng không thấy ảnh | Ảnh không nằm trong `static/images/` hoặc sai tên file | Kiểm tra lại thư mục ảnh theo Bước 3 (tên file phân biệt hoa/thường trên macOS/Linux) |
| PowerShell báo `running scripts is disabled` khi kích hoạt venv | Chính sách bảo mật của PowerShell | Chạy `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, chọn `Y`; hoặc dùng Command Prompt |
| `Address already in use` / port 5000 bị chiếm | Một chương trình khác đang dùng cổng 5000 (trên macOS thường là AirPlay Receiver) | Tắt chương trình đó, hoặc sửa dòng cuối `app.py` thành `port=5001` rồi vào http://127.0.0.1:5001 |
| Bấm tính mà không ra kết quả | Server đã bị tắt | Kiểm tra cửa sổ dòng lệnh còn chạy `python app.py` không |

