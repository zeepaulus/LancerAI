import React, { useEffect, useState } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import * as keys from '../../config/storageKeys';
import { me as apiMe } from '../../api/auth';

/**
 * AuthGuard protects authenticated routes while the access token is verified.
 */
const AuthGuard = () => {
    const location = useLocation();
    const token = localStorage.getItem(keys.LANCERAI_ACCESS_TOKEN);

    const [status, setStatus] = useState(
        token ? 'verifying' : 'unauthenticated'
    );

    useEffect(() => {
        if (!token) return;

        let cancelled = false;

        apiMe()
            .then((profile) => {
                if (cancelled) return;
                localStorage.setItem(keys.LANCERAI_USER_PROFILE, JSON.stringify(profile));
                setStatus('authenticated');
            })
            .catch(() => {
                if (cancelled) return;
                localStorage.removeItem(keys.LANCERAI_ACCESS_TOKEN);
                localStorage.removeItem(keys.LANCERAI_USER_PROFILE);
                setStatus('unauthenticated');
            });

        return () => { cancelled = true; };
    }, [token]);

    if (status === 'verifying') {
        return (
            <div className="auth-guard-loading" role="status" aria-live="polite" aria-label="Verifying session">
                <div className="auth-guard-spinner" />
            </div>
        );
    }

    if (status === 'unauthenticated') {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return <Outlet />;
};

export default AuthGuard;
