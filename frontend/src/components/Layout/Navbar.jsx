// Thanh điều hướng cho trang chính (trang hiển thị sau khi đăng nhập)

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Navbar = () => {
    const navigate = useNavigate();
    const [showDropdown, setShowDropdown] = useState(false);

    const handleLogout = () => {
        localStorage.removeItem('mockUserDB'); // Xóa dữ liệu tạm
        // TODO: Gọi API logout lên backend để hủy session/token
        navigate('/'); // Về trang Landing
    };

    return (
        <nav style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 20px', background: '#f5f5f5' }}>
            {/* Logo */}
            <div style={{ fontWeight: 'bold', cursor: 'pointer' }} onClick={() => navigate('/dashboard')}>
                LOGO_CV_AI
            </div>

            {/* Các nút chức năng */}
            <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
                <button>Phỏng vấn</button>
                <button>Đánh giá CV</button>

                {/* Dropdown Avatar */}
                <div style={{ position: 'relative' }}>
                    <button 
                        style={{ borderRadius: '50%', width: '40px', height: '40px' }}
                        onClick={() => setShowDropdown(!showDropdown)}
                    >
                        👤
                    </button>

                    {showDropdown && (
                        <div style={{ position: 'absolute', right: 0, top: '50px', background: 'white', border: '1px solid #ccc', display: 'flex', flexDirection: 'column', width: '150px' }}>
                            <button>Profile của tôi</button>
                            <button>Quản lý tài khoản</button>
                            <button>Chế độ tối</button>
                            <button>Ảnh đại diện</button>
                            <button>Về chúng tôi</button>
                            <button onClick={handleLogout} style={{color: 'red'}}>Đăng xuất</button>
                        </div>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;