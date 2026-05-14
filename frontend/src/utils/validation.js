/**
 * Chuẩn hóa với backend `AuthSignupRequest` / `AuthLoginRequest`:
 * — mật khẩu tối thiểu **8** ký tự (backend `min_length=8`).
 * — đăng nhập gửi trường `email`; form dùng `usernameOrEmail` nhưng phải là **email**.
 */

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PW_MIN = 8;
const PW_MAX = 128;

export const validateAuthForm = (isLogin, formData) => {
    const errors = {};

    if (!formData.password) errors.password = 'Không được bỏ trống mật khẩu!';
    else if (formData.password.length < PW_MIN) {
        errors.password = `Mật khẩu ít nhất ${PW_MIN} ký tự.`;
    } else if (formData.password.length > PW_MAX) {
        errors.password = `Mật khẩu tối đa ${PW_MAX} ký tự.`;
    }

    const emailRegex = EMAIL_RE;

    if (isLogin) {
        const em = (formData.usernameOrEmail || '').trim();
        if (!em) errors.usernameOrEmail = 'Vui lòng nhập Email hoặc Tên người dùng!';
    } else {
        if (!formData.username) errors.username = 'Không được bỏ trống tên hiển thị!';
        if (!formData.email) errors.email = 'Không được bỏ trống Email!';
        else if (!emailRegex.test(formData.email)) errors.email = 'Email không đúng định dạng!';

        const usernameRegex = /^[a-zA-Z0-9]+$/;
        if (formData.username && formData.username.length > 120) {
            errors.username = 'Tên hiển thị không quá 120 ký tự.';
        } else if (formData.username && !usernameRegex.test(formData.username)) {
            errors.username = 'Tên hiển thị chỉ chữ và số (dùng làm display_name gửi API).';
        }
    }

    return errors;
};
