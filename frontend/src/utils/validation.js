// Hàm kiểm tra logic form

export const validateAuthForm = (isLogin, formData) => {
    let errors = {};

    // 1. Kiểm tra bỏ trống
    if (!formData.password) errors.password = "Không được bỏ trống mật khẩu!";
    if (isLogin) {
        if (!formData.usernameOrEmail) errors.usernameOrEmail = "Vui lòng nhập Email hoặc Tên người dùng!";
    } else {
        if (!formData.username) errors.username = "Không được bỏ trống Tên tài khoản!";
        if (!formData.email) errors.email = "Không được bỏ trống Email!";
    }

    // 2. Kiểm tra format Email (chỉ áp dụng cho đăng ký)
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!isLogin && formData.email && !emailRegex.test(formData.email)) {
        errors.email = "Email không đúng định dạng!";
    }
    // Cảnh báo mật khẩu yếu
    if (!isLogin && formData.password && formData.password.length < 6) {
        errors.password = "Mật khẩu yếu: Phải có ít nhất 6 ký tự!";
    }


    // 3. Kiểm tra Username (chỉ chữ cái và số)
    const usernameRegex = /^[a-zA-Z0-9]+$/;
    if (!isLogin && formData.username && !usernameRegex.test(formData.username)) {
        errors.username = "Tên người dùng chỉ được chứa chữ cái và số!";
    }
    
    return errors;
};