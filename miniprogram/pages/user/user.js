// pages/user/user.js - 高端定制版逻辑
const app = getApp();
const { api } = require('../../utils/api');

Page({
    data: {
        userInfo: null,
        // 会员数据
        points: 0,
        couponCount: 0,
        balance: '0.00',
        // 会员等级信息
        memberLevel: '',
        memberLevelName: '',
        discountRate: '',
        isMemberValid: false,
        memberExpireDate: '',
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
        let userInfo = app.globalData.userInfo || wx.getStorageSync('userInfo');

        // 如果是字符串（可能是旧版本残留），尝试转成对象或包装成对象
        if (typeof userInfo === 'string') {
            try {
                userInfo = JSON.parse(userInfo);
            } catch (e) {
                userInfo = { username: userInfo };
            }
        }

        // 计算会员等级显示
        const levelMap = {
            'regular': { name: '普通会员', discount: '100%' },
            'silver': { name: '银卡会员', discount: '95折' },
            'gold': { name: '金卡会员', discount: '9折' },
            'platinum': { name: '铂金会员', discount: '85折' }
        };

        const level = userInfo?.member_level || 'regular';
        const levelInfo = levelMap[level] || levelMap['regular'];

        // 计算会员有效期
        let isMemberValid = false;
        let memberExpireDate = '';
        if (userInfo?.member_expire_at && level !== 'regular') {
            const expire = new Date(userInfo.member_expire_at);
            isMemberValid = expire > new Date();
            memberExpireDate = expire.toLocaleDateString('zh-CN');
        }

        this.setData({
            userInfo,
            memberLevel: level,
            memberLevelName: levelInfo.name,
            discountRate: isMemberValid ? levelInfo.discount : '100%',
            isMemberValid,
            memberExpireDate,
            points: userInfo?.points || 0
        });
    },

    loadUserStats() {
        const token = wx.getStorageSync('token');
        if (!token) return;

        api.getUserStats().then(res => {
            this.setData({
                points: res.points || 0,
                couponCount: res.coupon_count || 0
            });
        }).catch(err => {
            console.error('获取用户统计失败:', err);
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
        wx.navigateTo({ url: '/pages/user-edit/user-edit' });
    },

    goToOrders(e) {
        const status = e.currentTarget.dataset.status || '';
        wx.navigateTo({ url: `/pages/orders/orders?status=${status}` });
    },

    goToRefund() {
        wx.navigateTo({ url: '/pages/refund/refund' });
    },

    goToSubscription() {
        wx.navigateTo({ url: '/pages/subscription/subscription' });
    },

    goToVip() {
        wx.navigateTo({ url: '/pages/vip/vip' });
    },

    goToAddress() {
        wx.navigateTo({ url: '/pages/address/address' });
    },

    goToFavorites() {
        wx.navigateTo({ url: '/pages/favorites/favorites' });
    },

    goToCoupon() {
        wx.navigateTo({ url: '/pages/coupon/coupon' });
    },

    goToPoints() {
        wx.navigateTo({ url: '/pages/points/points' });
    },

    goToFeedback() {
        wx.navigateTo({ url: '/pages/feedback-list/feedback-list' });
    },

    goToMyReviews() {
        wx.navigateTo({ url: '/pages/my-reviews/my-reviews' });
    },

    goToSettings() {
        wx.navigateTo({ url: '/pages/settings/settings' });
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
