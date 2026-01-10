// pages/user/user.js - 高端定制版逻辑
const app = getApp();

Page({
    data: {
        userInfo: null,
        // 会员数据
        points: 0,
        couponCount: 0,
        balance: '0.00',
        // 订单角标数据
        pendingCount: 0,
        paidCount: 0,
        shippedCount: 0
    },

    onShow() {
        this.loadUserInfo();
        this.loadUserStats(); // 加载会员数据
        this.loadOrderCounts(); // 加载订单数量
        app.updateCartBadge();
    },

    loadUserInfo() {
        const userInfo = app.globalData.userInfo || wx.getStorageSync('userInfo');
        this.setData({ userInfo });
    },

    loadUserStats() {
        // 模拟会员数据 (后续接API)
        this.setData({
            points: 1280,
            couponCount: 5,
            balance: '88.00'
        });
    },

    loadOrderCounts() {
        // 模拟订单数量 (后续接API)
        this.setData({
            pendingCount: 1,
            paidCount: 0,
            shippedCount: 2
        });
    },

    // --- 导航方法 ---

    goToLogin() {
        wx.navigateTo({ url: '/pages/login/login' });
    },

    goToProfile() {
        // 个人资料页 (暂未实现，可提示)
        wx.showToast({ title: '个人资料', icon: 'none' });
    },

    goToOrders(e) {
        const status = e.currentTarget.dataset.status || '';
        wx.navigateTo({ url: `/pages/orders/orders?status=${status}` });
    },

    goToRefund() {
        // 售后页 (暂未实现)
        wx.showToast({ title: '售后/退款功能开发中', icon: 'none' });
    },

    goToSubscription() {
        wx.navigateTo({ url: '/pages/subscription/subscription' });
    },

    goToAddress() {
        wx.navigateTo({ url: '/pages/address/address' });
    },

    goToFavorites() {
        // wx.navigateTo({ url: '/pages/favorites/favorites' });
        wx.showToast({ title: '收藏功能开发中', icon: 'none' });
    },

    goToFeedback() {
        // wx.navigateTo({ url: '/pages/feedback/feedback' });
        wx.showToast({ title: '意见反馈功能开发中', icon: 'none' });
    },

    goToSettings() {
        // wx.navigateTo({ url: '/pages/settings/settings' });
        wx.showToast({ title: '设置功能开发中', icon: 'none' });
    },

    callService() {
        wx.makePhoneCall({ phoneNumber: '400-888-8888' });
    },

    logout() {
        wx.showModal({
            title: '提示',
            content: '确定要退出登录吗？',
            success: (res) => {
                if (res.confirm) {
                    wx.removeStorageSync('token');
                    wx.removeStorageSync('userInfo');
                    app.globalData.token = null;
                    app.globalData.userInfo = null;
                    this.setData({ userInfo: null });
                    // 清空数据
                    this.setData({
                        points: 0,
                        couponCount: 0,
                        balance: '0.00',
                        pendingCount: 0,
                        paidCount: 0,
                        shippedCount: 0
                    });
                    wx.showToast({ title: '已退出', icon: 'success' });
                }
            }
        });
    }
});
