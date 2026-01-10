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
            // TODO: 调用真实后端API
            // const res = await api.login({ phone, password });
            // const { token, user } = res;

            // 模拟登录成功
            await this.simulateDelay(1000);

            const token = 'token_' + Date.now();
            const userInfo = {
                id: 1,
                phone,
                username: '用户' + phone.slice(-4),
                avatar: 'https://i.pravatar.cc/200?u=' + phone
            };

            this.handleLoginSuccess(token, userInfo);
        } catch (error) {
            wx.showToast({ title: error.message || '登录失败', icon: 'none' });
        } finally {
            wx.hideLoading();
            this.setData({ isLoading: false });
        }
    },

    // 微信一键登录（获取微信用户信息）
    async wxLogin() {
        this.setData({ isLoading: true });
        wx.showLoading({ title: '微信登录中...' });

        try {
            // 1. 获取微信登录code
            const loginRes = await this.wxLoginPromise();
            const code = loginRes.code;
            console.log('微信登录code:', code);

            // 2. 获取用户信息（需要用户授权）
            const userProfile = await this.getUserProfilePromise();
            console.log('用户信息:', userProfile);

            // 3. 发送到后端验证并获取token
            // TODO: 调用真实后端API
            // const res = await api.wxLogin({
            //   code,
            //   userInfo: userProfile.userInfo,
            //   encryptedData: userProfile.encryptedData,
            //   iv: userProfile.iv
            // });

            // 模拟后端返回
            await this.simulateDelay(800);

            const token = 'wx_token_' + Date.now();
            const userInfo = {
                id: 1,
                username: userProfile.userInfo.nickName,
                avatar: userProfile.userInfo.avatarUrl,
                phone: ''
            };

            this.handleLoginSuccess(token, userInfo);
        } catch (error) {
            console.error('微信登录失败:', error);
            if (error.errMsg && error.errMsg.includes('cancel')) {
                wx.showToast({ title: '已取消授权', icon: 'none' });
            } else {
                wx.showToast({ title: error.message || '微信登录失败', icon: 'none' });
            }
        } finally {
            wx.hideLoading();
            this.setData({ isLoading: false });
        }
    },

    // 手机号快捷登录（真机才能使用）
    async onGetPhoneNumber(e) {
        console.log('getPhoneNumber result:', e.detail);

        if (e.detail.errMsg !== 'getPhoneNumber:ok') {
            if (e.detail.errMsg.includes('deny') || e.detail.errMsg.includes('cancel')) {
                wx.showToast({ title: '已取消授权', icon: 'none' });
            }
            return;
        }

        this.setData({ isLoading: true });
        wx.showLoading({ title: '登录中...' });

        try {
            // 1. 获取登录code
            const loginRes = await this.wxLoginPromise();
            const code = loginRes.code;

            // 2. 发送到后端解密手机号并登录
            // TODO: 调用真实后端API
            // const res = await api.phoneLogin({
            //   code,
            //   encryptedData: e.detail.encryptedData,
            //   iv: e.detail.iv
            // });

            // 模拟后端返回
            await this.simulateDelay(800);

            const token = 'phone_token_' + Date.now();
            const userInfo = {
                id: 1,
                phone: '138****8888',
                username: '用户8888',
                avatar: 'https://i.pravatar.cc/200'
            };

            this.handleLoginSuccess(token, userInfo);
        } catch (error) {
            console.error('手机号登录失败:', error);
            wx.showToast({ title: error.message || '登录失败', icon: 'none' });
        } finally {
            wx.hideLoading();
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

    // wx.login Promise 封装
    wxLoginPromise() {
        return new Promise((resolve, reject) => {
            wx.login({
                success: resolve,
                fail: reject
            });
        });
    },

    // wx.getUserProfile Promise 封装
    getUserProfilePromise() {
        return new Promise((resolve, reject) => {
            wx.getUserProfile({
                desc: '用于完善用户资料',
                success: resolve,
                fail: reject
            });
        });
    },

    // 模拟延迟
    simulateDelay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },

    goToRegister() {
        wx.navigateTo({ url: '/pages/register/register' });
    }
});
