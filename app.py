import math
from flask import Flask, render_template, request, jsonify
from scipy.special import jn_zeros, jnp_zeros

app = Flask(__name__)

# ===== HẰNG SỐ VẬT LÝ (giá trị chuẩn CODATA) =====
C_SPEED = 299792458.0                 # Vận tốc ánh sáng (m/s)
EPS0 = 8.8541878128e-12               # Hằng số điện môi chân không (F/m)
MU0 = 4.0 * math.pi * 1e-7            # Độ từ thẩm chân không (H/m)
ETA0 = MU0 * C_SPEED                  # Trở kháng sóng chân không ≈ 376.73 Ω


class InputError(Exception):
    """Lỗi dữ liệu đầu vào -> trả về HTTP 400."""


def _cap(text):
    return text if text[:1] in "εμ" else text[:1].upper() + text[1:]


def get_float(data, key, default=None, name=None):
    """Đọc một số thực từ JSON, báo lỗi tiếng Việt nếu ô bị trống hoặc sai định dạng."""
    raw = data.get(key, default)
    if raw is None or str(raw).strip() == '':
        raise InputError(f'Vui lòng nhập {name or key}!')
    try:
        val = float(raw)
    except (TypeError, ValueError):
        raise InputError(_cap(f'{name or key} phải là một số!'))
    if not math.isfinite(val):
        raise InputError(_cap(f'{name or key} không hợp lệ!'))
    return val


def get_int(data, key, default=None, name=None):
    """Đọc chỉ số mode (số nguyên). Từ chối giá trị lẻ như 1.5."""
    val = get_float(data, key, default, name)
    if val != int(val):
        raise InputError(_cap(f'{name or key} phải là số nguyên!'))
    return int(val)


def get_mode(data):
    mode_type = str(data.get('mode_type', 'TE')).upper().strip()
    if mode_type not in ('TE', 'TM'):
        raise InputError('Loại sóng phải là TE hoặc TM!')
    return mode_type


def handle(func):
    """Bọc mỗi route: lỗi nhập liệu -> 400, lỗi khác -> 500."""
    def wrapper():
        try:
            data = request.get_json(silent=True)
            if not isinstance(data, dict):
                raise InputError('Dữ liệu gửi lên không hợp lệ!')
            return jsonify(func(data))
        except InputError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'Lỗi hệ thống: {e}'}), 500
    wrapper.__name__ = func.__name__
    return wrapper


def wave_impedance(mode_type, eta, fc_hz, f_hz):
    """Trở kháng sóng của ống dẫn sóng; trả về chuỗi thông báo nếu f <= fc."""
    if f_hz <= fc_hz:
        return 'Cắt sóng (f ≤ fc)'
    factor = math.sqrt(1.0 - (fc_hz / f_hz) ** 2)
    z = eta / factor if mode_type == 'TE' else eta * factor
    return round(z, 2)


@app.route('/')
def home():
    return render_template('index.html')


# 1. CÁP ĐỒNG TRỤC (Coaxial Cable)
@app.route('/calculate_coaxial', methods=['POST'])
@handle
def calculate_coaxial(data):
    er = get_float(data, 'er', name='εr')
    d = get_float(data, 'd', name='đường kính lõi d')
    D = get_float(data, 'D', name='đường kính vỏ D')

    if er <= 0 or d <= 0 or D <= 0:
        raise InputError('Các tham số phải lớn hơn 0!')
    if D <= d:
        raise InputError('Đường kính vỏ ngoài D phải lớn hơn đường kính lõi d!')

    ln_ratio = math.log(D / d)
    sqrt_er = math.sqrt(er)

    z0 = ETA0 / (2.0 * math.pi * sqrt_er) * ln_ratio          # ≈ 138.06·log10(D/d)/√εr (Ω)
    c_val = 2.0 * math.pi * EPS0 * er / ln_ratio * 1e12        # ≈ 24.16·εr/log10(D/d) (pF/m)
    l_val = MU0 / (2.0 * math.pi) * ln_ratio * 1e9             # ≈ 460.5·log10(D/d) (nH/m)
    # TE11: fc ≈ c / (π·(a+b)·√εr), a = d/2, b = D/2 -> fc = 2c / (π·(D+d)·√εr)
    fc_ghz = 2.0 * C_SPEED / (math.pi * (D + d) * 1e-3 * sqrt_er) / 1e9
    vp_m_s = C_SPEED / sqrt_er
    td_ns_m = 1e9 / vp_m_s

    return {
        'z0': round(z0, 2),
        'C': round(c_val, 2),
        'L': round(l_val, 2),
        'fc': round(fc_ghz, 3),
        'vp': round(vp_m_s / 1000.0, 2),
        'td': round(td_ns_m, 2),
    }


# 2. ỐNG DẪN SÓNG HÌNH CHỮ NHẬT (Rectangular Waveguide)
@app.route('/calculate_rect_wg', methods=['POST'])
@handle
def calculate_rect_wg(data):
    a_mm = get_float(data, 'a', name='chiều rộng a')
    b_mm = get_float(data, 'b', name='chiều cao b')
    er = get_float(data, 'er', 1.0, name='εr')
    mode_type = get_mode(data)
    m = get_int(data, 'm', 1, name='chỉ số m')
    n = get_int(data, 'n', 0, name='chỉ số n')
    f_ghz = get_float(data, 'f', name='tần số f')

    if a_mm <= 0 or b_mm <= 0 or f_ghz <= 0 or er <= 0:
        raise InputError('Kích thước, tần số và εr phải lớn hơn 0!')
    if m < 0 or n < 0:
        raise InputError('Chỉ số m và n phải lớn hơn hoặc bằng 0!')
    if m == 0 and n == 0:
        raise InputError(f'Mode {mode_type}00 không tồn tại!')
    if mode_type == 'TM' and (m == 0 or n == 0):
        raise InputError('Mode TM yêu cầu m ≥ 1 và n ≥ 1!')

    a = a_mm / 1000.0
    b = b_mm / 1000.0
    v = C_SPEED / math.sqrt(er)

    kc = math.sqrt((m * math.pi / a) ** 2 + (n * math.pi / b) ** 2)   # số sóng cắt (rad/m)
    fc_hz = v * kc / (2.0 * math.pi)
    lc_mm = 2.0 * math.pi / kc * 1000.0                                  # bước sóng cắt λc = 2π/kc

    return {
        'fc': round(fc_hz / 1e9, 3),
        'lc': round(lc_mm, 2),
        'zwave': wave_impedance(mode_type, ETA0 / math.sqrt(er), fc_hz, f_ghz * 1e9),
    }


# 3. ỐNG DẪN SÓNG HÌNH TRỤ TRÒN (Circular Waveguide)
@app.route('/calculate_circ_wg', methods=['POST'])
@handle
def calculate_circ_wg(data):
    a_mm = get_float(data, 'a', name='bán kính a')
    er = get_float(data, 'er', 1.0, name='εr')
    ur = get_float(data, 'ur', 1.0, name='μr')
    mode_type = get_mode(data)
    m = get_int(data, 'm', 1, name='chỉ số m')
    n = get_int(data, 'n', 1, name='chỉ số n')
    f_ghz = get_float(data, 'f', name='tần số f')

    if a_mm <= 0 or er <= 0 or ur <= 0 or f_ghz <= 0:
        raise InputError('Kích thước, tần số, εr và μr phải lớn hơn 0!')
    if m < 0 or n < 0:
        raise InputError('Chỉ số m và n phải lớn hơn hoặc bằng 0!')
    if n == 0:
        raise InputError('Ống dẫn sóng tròn yêu cầu n ≥ 1!')

    # p_mn: nghiệm thứ n của J_m(x) = 0 (TM) hoặc J'_m(x) = 0 (TE)
    if mode_type == 'TM':
        p_mn = float(jn_zeros(m, n)[n - 1])
    else:
        p_mn = float(jnp_zeros(m, n)[n - 1])

    a = a_mm / 1000.0
    v = C_SPEED / math.sqrt(er * ur)

    kc = p_mn / a
    fc_hz = v * kc / (2.0 * math.pi)
    lc_mm = 2.0 * math.pi / kc * 1000.0

    return {
        'fc': round(fc_hz / 1e9, 3),
        'lc': round(lc_mm, 2),
        'zwave': wave_impedance(mode_type, ETA0 * math.sqrt(ur / er), fc_hz, f_ghz * 1e9),
    }


# 4. ĐƯỜNG TRUYỀN MẠCH IN (Microstrip Line) — công thức gần đúng Hammerstad (Pozar)
@app.route('/calculate_microstrip', methods=['POST'])
@handle
def calculate_microstrip(data):
    w = get_float(data, 'w', name='chiều rộng W')
    d = get_float(data, 'd', name='độ dày d')
    er = get_float(data, 'er', name='εr')

    if w <= 0 or d <= 0 or er <= 0:
        raise InputError('Các tham số phải lớn hơn 0!')
    if er < 1:
        raise InputError('Hằng số điện môi εr của đế phải ≥ 1!')

    wd = w / d
    eeff = (er + 1.0) / 2.0 + (er - 1.0) / 2.0 / math.sqrt(1.0 + 12.0 / wd)

    if wd <= 1.0:
        z0 = 60.0 / math.sqrt(eeff) * math.log(8.0 / wd + wd / 4.0)
    else:
        z0 = 120.0 * math.pi / (math.sqrt(eeff) * (wd + 1.393 + 0.667 * math.log(wd + 1.444)))

    return {
        'wd_ratio': round(wd, 3),
        'eeff': round(eeff, 3),
        'z0': round(z0, 2),
    }


# 5. ĐƯỜNG TRUYỀN HAI DÂY (Two-Wire Line)
@app.route('/calculate_twowire', methods=['POST'])
@handle
def calculate_twowire(data):
    er = get_float(data, 'er', 1.0, name='εr')
    d = get_float(data, 'd', name='đường kính dây d')      # đường kính mỗi dây (mm)
    D = get_float(data, 'D', name='khoảng cách tâm D')     # khoảng cách giữa tâm 2 dây (mm)

    if er <= 0 or d <= 0 or D <= 0:
        raise InputError('Các tham số phải lớn hơn 0!')
    if D <= d:
        raise InputError('Khoảng cách D giữa hai tâm dây phải lớn hơn đường kính dây d!')

    sqrt_er = math.sqrt(er)
    x = math.acosh(D / d)        # ≈ ln(2D/d) khi D >> d

    z0 = ETA0 / (math.pi * sqrt_er) * x            # ≈ (119.9/√εr)·acosh(D/d) (Ω)
    c_val = math.pi * EPS0 * er / x * 1e12         # pF/m
    l_val = MU0 / math.pi * x * 1e9                # nH/m
    vp_m_s = C_SPEED / sqrt_er
    td_ns_m = 1e9 / vp_m_s

    return {
        'z0': round(z0, 2),
        'C': round(c_val, 2),
        'L': round(l_val, 2),
        'vp': round(vp_m_s / 1000.0, 2),
        'td': round(td_ns_m, 2),
    }


if __name__ == '__main__':
    app.run(debug=True, port=5000)
