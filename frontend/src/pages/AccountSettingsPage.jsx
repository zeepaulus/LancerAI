import React, { useEffect, useState } from 'react';
import Navbar from '../components/Layout/Navbar';
import { Alert, Page, PageHero, Panel, StatusBadge } from '../components/Common/AppUI';
import { changePassword, me } from '../api/auth';
import * as keys from '../config/storageKeys';

const initialPasswordForm = {
    current_password: '',
    new_password: '',
    confirm_password: '',
};

const AccountSettingsPage = () => {
    const [profile, setProfile] = useState(() => {
        try {
            return JSON.parse(localStorage.getItem(keys.LANCERAI_USER_PROFILE) || '{}');
        } catch {
            return {};
        }
    });
    const [passwordForm, setPasswordForm] = useState(initialPasswordForm);
    const [showPassword, setShowPassword] = useState(false);
    const [loadingProfile, setLoadingProfile] = useState(false);
    const [savingPassword, setSavingPassword] = useState(false);
    const [passwordMessage, setPasswordMessage] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        let active = true;
        setLoadingProfile(true);
        me()
            .then((data) => {
                if (!active) return;
                setProfile(data || {});
                localStorage.setItem(keys.LANCERAI_USER_PROFILE, JSON.stringify(data || {}));
            })
            .catch((err) => {
                if (active) setError(err.message || 'Không thể tải hồ sơ tài khoản.');
            })
            .finally(() => {
                if (active) setLoadingProfile(false);
            });
        return () => { active = false; };
    }, []);

    const handlePasswordSubmit = async (event) => {
        event.preventDefault();
        setError('');
        setPasswordMessage('');
        if (passwordForm.new_password !== passwordForm.confirm_password) {
            setError('Mật khẩu mới và xác nhận mật khẩu chưa khớp.');
            return;
        }
        if (passwordForm.new_password.length < 8) {
            setError('Mật khẩu mới cần có ít nhất 8 ký tự.');
            return;
        }

        setSavingPassword(true);
        try {
            await changePassword({
                current_password: passwordForm.current_password,
                new_password: passwordForm.new_password,
            });
            setPasswordForm(initialPasswordForm);
            setPasswordMessage('Đã đổi mật khẩu.');
        } catch (err) {
            setError(err.message || 'Không thể đổi mật khẩu.');
        } finally {
            setSavingPassword(false);
        }
    };

    const initials = (profile.display_name || profile.email || 'Người dùng')
        .split(/\s+/)
        .filter(Boolean)
        .slice(0, 2)
        .map((part) => part[0]?.toUpperCase())
        .join('') || 'U';

    return (
        <div className="app-screen">
            <Navbar />
            <Page wide>
                <PageHero
                    kicker="Cài đặt"
                    title="Tài khoản"
                    description="Xem thông tin tài khoản và đổi mật khẩu khi cần."
                    actions={<StatusBadge tone="settings">Tài khoản người dùng</StatusBadge>}
                    tone="settings"
                />

                {error && (
                    <div className="ui-section-gap-bottom">
                        <Alert tone="danger" title="Cần kiểm tra cài đặt">{error}</Alert>
                    </div>
                )}

                <div className="dashboard-grid">
                    <Panel className="span-5" title="Hồ sơ hiện tại" subtitle="Thông tin đang được lưu trong tài khoản.">
                        <div className="settings-profile-card">
                            <span className="lancer-avatar settings-profile-avatar">{initials}</span>
                            <div>
                                <strong>{profile.display_name || 'Chưa đặt tên'}</strong>
                                <p>{profile.email || 'Chưa có email'}</p>
                            </div>
                        </div>
                        <div className="settings-profile-meta">
                            <span>Vai trò</span>
                            <strong>{profile.role || 'user'}</strong>
                            <span>Trạng thái</span>
                            <strong>{loadingProfile ? 'Đang tải' : 'Đã đồng bộ'}</strong>
                        </div>
                    </Panel>

                    <Panel className="span-7" title="Thông tin hồ sơ" subtitle="Thông tin định danh của tài khoản chỉ có thể xem.">
                        <div className="ui-stack">
                            <label htmlFor="settings-full-name" className="ui-field">
                                <span>Họ tên hiển thị</span>
                                <input
                                    id="settings-full-name"
                                    className="text-input"
                                    value={profile.display_name || ''}
                                    readOnly
                                    aria-describedby="settings-display-name-note"
                                    autoComplete="name"
                                />
                            </label>
                            <p id="settings-display-name-note" className="caption">Tên hiển thị được đặt khi đăng ký và không thể chỉnh sửa.</p>
                            <label htmlFor="settings-email" className="ui-field">
                                <span>Email</span>
                                <input
                                    id="settings-email"
                                    className="text-input"
                                    value={profile.email || ''}
                                    readOnly
                                    aria-describedby="settings-email-note"
                                />
                            </label>
                            <p id="settings-email-note" className="caption">Email dùng để đăng nhập và chưa thể chỉnh sửa trong phiên bản này.</p>
                        </div>
                    </Panel>

                    <Panel className="span-12" title="Mật khẩu" subtitle="Đổi mật khẩu định kỳ nếu bạn dùng chung thiết bị hoặc nghi ngờ tài khoản bị lộ.">
                        <form className="settings-password-grid" onSubmit={handlePasswordSubmit}>
                            <PasswordField
                                id="current-password"
                                label="Mật khẩu hiện tại"
                                value={passwordForm.current_password}
                                show={showPassword}
                                autoComplete="current-password"
                                onChange={(value) => setPasswordForm((prev) => ({ ...prev, current_password: value }))}
                            />
                            <PasswordField
                                id="new-password"
                                label="Mật khẩu mới"
                                value={passwordForm.new_password}
                                show={showPassword}
                                autoComplete="new-password"
                                onChange={(value) => setPasswordForm((prev) => ({ ...prev, new_password: value }))}
                            />
                            <PasswordField
                                id="confirm-password"
                                label="Xác nhận mật khẩu mới"
                                value={passwordForm.confirm_password}
                                show={showPassword}
                                autoComplete="new-password"
                                onChange={(value) => setPasswordForm((prev) => ({ ...prev, confirm_password: value }))}
                            />
                            <div className="settings-password-actions">
                                <button className="btn-outline" type="button" onClick={() => setShowPassword((value) => !value)}>
                                    {showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}
                                </button>
                                <button className="btn-primary" type="submit" disabled={savingPassword}>
                                    {savingPassword ? 'Đang lưu...' : 'Lưu mật khẩu'}
                                </button>
                                {passwordMessage && <StatusBadge tone="success">{passwordMessage}</StatusBadge>}
                            </div>
                        </form>
                    </Panel>
                </div>
            </Page>
        </div>
    );
};

const PasswordField = ({ id, label, value, onChange, show, autoComplete }) => (
    <label htmlFor={id} className="ui-field">
        <span>{label}</span>
        <input
            id={id}
            className="text-input"
            type={show ? 'text' : 'password'}
            value={value}
            onChange={(event) => onChange(event.target.value)}
            autoComplete={autoComplete}
        />
    </label>
);

export default AccountSettingsPage;
