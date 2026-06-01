import React, { useEffect, useState } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import * as keys from '../../config/storageKeys';
import { me as apiMe } from '../../api/auth';

/**
 * AuthGuard — bảo vệ các route cần đăng nhập.
 *
 * Chiến lược:
 *   1. Kiểm tra token trong localStorage ngay lập tức (sync).
 *      Nếu không có token → redirect /login ngay, không cần gọi API.
 *   2. Nếu có token → gọi GET /auth/me để verify token còn hợp lệ với server.
 *      - Valid   → render children (Outlet).
 *      - Invalid → xóa localStorage, redirect /login.
 *   3. Trong lúc đang verify → hiển thị màn hình loading tối giản.
 *
 * Lý do verify với server thay vì chỉ kiểm tra localStorage:
 *   Token có thể bị revoke phía server, hoặc hết hạn (exp claim).
 *   Gọi /me là cách duy nhất để chắc chắn.
 */
const AuthGuard = () => {
    const location = useLocation();
    const token = localStorage.getItem(keys.LANCERAI_ACCESS_TOKEN);

    const [status, setStatus] = useState(
        token ? 'verifying' : 'unauthenticated'
    );

    useEffect(() => {
        if (!token) return; // đã set 'unauthenticated' ở trên

        let cancelled = false;

        apiMe()
            .then((profile) => {
                if (cancelled) return;
                // Làm mới profile trong localStorage (display_name, role,...)
                localStorage.setItem(keys.LANCERAI_USER_PROFILE, JSON.stringify(profile));
                setStatus('authenticated');
            })
            .catch(() => {
                if (cancelled) return;
                // Token không hợp lệ hoặc hết hạn
                localStorage.removeItem(keys.LANCERAI_ACCESS_TOKEN);
                localStorage.removeItem(keys.LANCERAI_USER_PROFILE);
                setStatus('unauthenticated');
            });

        return () => { cancelled = true; };
    }, [token]);

    if (status === 'verifying') {
        return (
            <div style={styles.loading}>
                <div style={styles.spinner} />
            </div>
        );
    }

    if (status === 'unauthenticated') {
        // Lưu lại trang user đang cố vào để redirect về sau khi login
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return <Outlet />;
};

const styles = {
    loading: {
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'var(--canvas)',
    },
    spinner: {
        width: '32px',
        height: '32px',
        border: '3px solid var(--hairline)',
        borderTop: '3px solid var(--ink)',
        borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
    },
};

export default AuthGuard;
