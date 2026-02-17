// pages/forgot-password/forgot-password.js - 忘记密码页面
const app = getApp();
const { api } = require('../../utils/api');

Page({
    data: {
        phone: '',
        newPassword: '',
        confirmPassword: '',
        isLoading: false
    },

    onPhoneInput(e) {
        this.setData({ phone: e.detail.value });
    },

    onNewPasswordInput(e) {
        this.setData({ newPassword: e.detail.value });
    },

    onConfirmPasswordInput(e) {
        this.setData({ confirmPassword: e.detail.value });
    },

    // 重置密码
    async resetPassword() {
        const { phone, newPassword, confirmPassword } = this.data;

        if (!phone || phone.length !== 11) {
            wx.showToast({ title: '请输入正确的手机号', icon: 'none' });
            return;
        }

        if (!newPassword || newPassword.length < 6) {
            wx.showToast({ title: '密码至少6位', icon: 'none' });
            return;
        }

        if (newPassword !== confirmPassword) {
            wx.showToast({ title: '两次密码不一致', icon: 'none' });
            return;
        }

        this.setData({ isLoading: true });
        wx.showLoading({ title: '提交中...' });

        try {
            // 调用重置密码API
            await api.resetPassword({
                phone,
                password: newPassword
            });

            wx.hideLoading();
            wx.showToast({ title: '密码重置成功', icon: 'success' });

            setTimeout(() => {
                wx.navigateBack();
            }, 1500);
        } catch (error) {
            wx.hideLoading();
            console.error('重置密码失败:', error);
            wx.showToast({ title: error.message || '重置失败', icon: 'none' });
        } finally {
            this.setData({ isLoading: false });
        }
    },

    goToLogin() {
        wx.navigateBack();
    }
});
