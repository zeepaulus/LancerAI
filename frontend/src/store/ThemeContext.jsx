import React, { createContext, useState, useEffect, useContext } from 'react';

// 1. Tạo Context
const ThemeContext = createContext();

// 2. Tạo Provider để bọc ứng dụng
export const ThemeProvider = ({ children }) => {
    // Kiểm tra xem trước đó người dùng có lưu chế độ tối không
    const [isDarkMode, setIsDarkMode] = useState(() => {
        return localStorage.getItem('theme') === 'dark';
    });

    // Mỗi khi isDarkMode thay đổi, cập nhật giao diện và lưu lại
    useEffect(() => {
        if (isDarkMode) {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
        }
    }, [isDarkMode]);

    const toggleDarkMode = () => {
        setIsDarkMode((prevMode) => !prevMode);
    };

    return (
        <ThemeContext.Provider value={{ isDarkMode, toggleDarkMode }}>
            {children}
        </ThemeContext.Provider>
    );
};

// 3. Tạo Custom Hook để sử dụng cho tiện
export const useTheme = () => useContext(ThemeContext);