// pages/register/register.js - 注册页面
const app = getApp();
const { api } = require('../../utils/api');

Page({
    data: {
        phone: '',
        password: '',
        confirmPassword: '',
        isLoading: false
    },

    onPhoneInput(e) {
        this.setData({ phone: e.detail.value });
    },

    onPasswordInput(e) {
        this.setData({ password: e.detail.value });
    },

    onConfirmPasswordInput(e) {
        this.setData({ confirmPassword: e.detail.value });
    },

    // 注册
    async register() {
        const { phone, password, confirmPassword } = this.data;

        // 验证手机号
        if (!phone || phone.length !== 11) {
            wx.showToast({ title: '请输入正确的手机号', icon: 'none' });
            return;
        }

        // 验证密码
        if (!password || password.length < 6) {
            wx.showToast({ title: '密码至少6位', icon: 'none' });
            return;
        }

        // 验证确认密码
        if (password !== confirmPassword) {
            wx.showToast({ title: '两次密码不一致', icon: 'none' });
            return;
        }

        this.setData({ isLoading: true });
        wx.showLoading({ title: '注册中...' });

        try {
            // 调用注册API
            const res = await api.register({
                username: phone,
                phone: phone,
                password: password,
                password_confirm: confirmPassword
            });

            wx.hideLoading();
            wx.showToast({ title: '注册成功', icon: 'success' });

            setTimeout(() => {
                // 返回登录页
                wx.navigateBack();
            }, 1500);
        } catch (error) {
            wx.hideLoading();
            console.error('注册失败:', error);
            const msg = error.password?.[0] || error.username?.[0] || error.phone?.[0] || error.message || '注册失败';
            wx.showToast({ title: msg, icon: 'none' });
        } finally {
            this.setData({ isLoading: false });
        }
    },

    goToLogin() {
        wx.navigateBack();
    }
});
