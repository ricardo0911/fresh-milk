// pages/login/login.js - 登录页面（支持真机登录）
const app = getApp();
const { api } = require('../../utils/api');

Page({
    data: {
        phone: '',
        password: '',
        isLoading: false
    },

    onPhoneInput(e) {
        this.setData({ phone: e.detail.value });
    },

    onPasswordInput(e) {
        this.setData({ password: e.detail.value });
    },

    // 账号密码登录
    async login() {
        const { phone, password } = this.data;

        if (!phone || phone.length !== 11) {
            wx.showToast({ title: '请输入正确的手机号', icon: 'none' });
            return;
        }

        if (!password || password.length < 6) {
            wx.showToast({ title: '请输入密码（至少6位）', icon: 'none' });
            return;
        }

        this.setData({ isLoading: true });
        wx.showLoading({ title: '登录中...' });

        try {
            // 调用后端登录API
            const res = await api.login({ username: phone, password });
            const token = res.access;
            const userInfo = res.user || {
                id: res.user_id,
                phone,
                username: res.username || phone
            };

            wx.hideLoading();
            this.handleLoginSuccess(token, userInfo);
        } catch (error) {
            wx.hideLoading();
            console.error('登录失败:', error);
            wx.showToast({ title: error.detail || error.message || '登录失败', icon: 'none' });
        } finally {
            this.setData({ isLoading: false });
        }
    },





    // 处理登录成功
    handleLoginSuccess(token, userInfo) {
        // 保存登录状态
        wx.setStorageSync('token', token);
        wx.setStorageSync('userInfo', userInfo);
        app.globalData.token = token;
        app.globalData.userInfo = userInfo;

        wx.showToast({ title: '登录成功', icon: 'success' });

        setTimeout(() => {
            // 返回上一页或跳转首页
            const pages = getCurrentPages();
            if (pages.length > 1) {
                wx.navigateBack();
            } else {
                wx.switchTab({ url: '/pages/index/index' });
            }
        }, 1500);
    },



    // 模拟延迟
    simulateDelay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },

    goToRegister() {
        wx.navigateTo({ url: '/pages/register/register' });
    },

    goToForgotPassword() {
        wx.navigateTo({ url: '/pages/forgot-password/forgot-password' });
    }
});
