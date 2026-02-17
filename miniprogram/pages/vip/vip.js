// pages/vip/vip.js - 会员中心逻辑
const app = getApp();
const { api } = require('../../utils/api');

Page({
    data: {
        userInfo: null,
        memberLevel: 'regular',
        memberLevelName: '普通会员',
        isMemberValid: false,
        expireDate: '',
        discountRate: '无折扣',
        plans: [],
        selectedPlanId: null,
        selectedPrice: '0.00',
        // 支付弹窗相关
        showPayModal: false,
        currentOrderId: '',
        userBalance: '0.00'
    },

    onLoad() {
        this.loadUserInfo();
        this.loadPlans();
        this.loadUserBalance();
    },

    onShow() {
        this.loadUserInfo();
    },

    loadUserInfo() {
        const userInfo = app.globalData.userInfo || wx.getStorageSync('userInfo');
        if (!userInfo) {
            this.setData({ userInfo: null });
            return;
        }

        const levelMap = {
            'regular': { name: '普通会员', discount: '无折扣' },
            'silver': { name: '银卡会员', discount: '95折' },
            'gold': { name: '金卡会员', discount: '9折' },
            'platinum': { name: '铂金会员', discount: '85折' }
        };

        const level = userInfo.member_level || 'regular';
        const levelInfo = levelMap[level] || levelMap['regular'];

        // 检查会员是否有效
        let isMemberValid = false;
        let expireDate = '';
        if (userInfo.member_expire_at && level !== 'regular') {
            const expire = new Date(userInfo.member_expire_at);
            isMemberValid = expire > new Date();
            expireDate = expire.toLocaleDateString('zh-CN');
        }

        this.setData({
            userInfo,
            memberLevel: level,
            memberLevelName: levelInfo.name,
            isMemberValid,
            expireDate,
            discountRate: isMemberValid ? levelInfo.discount : '无折扣'
        });
    },

    loadUserBalance() {
        const userInfo = app.globalData.userInfo || wx.getStorageSync('userInfo');
        if (userInfo && userInfo.balance) {
            this.setData({ userBalance: userInfo.balance });
        } else {
            // 模拟余额
            this.setData({ userBalance: '128.50' });
        }
    },

    async loadPlans() {
        try {
            const res = await api.getMembershipPlans();
            const plans = (res.results || res || []).map((p, index) => ({
                ...p,
                isHot: index === Math.floor((res.results || res || []).length / 2) // 中间的标为推荐
            }));

            this.setData({ plans });

            // 如果有套餐，默认选中推荐的
            const hotPlan = plans.find(p => p.isHot);
            if (hotPlan) {
                this.selectPlan({ currentTarget: { dataset: { id: hotPlan.id } } });
            }
        } catch (err) {
            console.error('加载会员套餐失败:', err);
            // 使用默认套餐数据以便测试
            const defaultPlans = [
                { id: 1, name: '银卡月卡', level: 'silver', level_display: '银卡会员', duration_days: 30, original_price: 29, price: 19, discount_display: '95折', isHot: false },
                { id: 2, name: '金卡季卡', level: 'gold', level_display: '金卡会员', duration_days: 90, original_price: 99, price: 69, discount_display: '9折', isHot: true },
                { id: 3, name: '铂金年卡', level: 'platinum', level_display: '铂金会员', duration_days: 365, original_price: 299, price: 199, discount_display: '85折', isHot: false }
            ];
            this.setData({ plans: defaultPlans });
            this.selectPlan({ currentTarget: { dataset: { id: 2 } } });
        }
    },

    selectPlan(e) {
        const planId = e.currentTarget.dataset.id;
        const plan = this.data.plans.find(p => p.id === planId);
        if (plan) {
            this.setData({
                selectedPlanId: planId,
                selectedPrice: plan.price
            });
        }
    },

    async buyMembership() {
        if (!this.data.selectedPlanId) {
            wx.showToast({ title: '请选择套餐', icon: 'none' });
            return;
        }

        const token = wx.getStorageSync('token');
        if (!token) {
            wx.showModal({
                title: '提示',
                content: '请先登录后再购买会员',
                confirmText: '去登录',
                success: (res) => {
                    if (res.confirm) {
                        wx.navigateTo({ url: '/pages/login/login' });
                    }
                }
            });
            return;
        }

        const selectedPlan = this.data.plans.find(p => p.id === this.data.selectedPlanId);
        if (!selectedPlan) return;

        wx.showLoading({ title: '创建订单...' });

        try {
            // 创建会员订单
            const orderRes = await api.createMembershipOrder(this.data.selectedPlanId);

            this.setData({
                currentOrderId: orderRes.id,
                showPayModal: true
            });

            wx.hideLoading();
        } catch (err) {
            wx.hideLoading();
            console.error('购买会员失败:', err);
            wx.showToast({ title: err.message || '创建订单失败', icon: 'none' });
        }
    },

    // 支付成功回调
    async onPaySuccess(e) {
        const { orderId, amount } = e.detail;
        const selectedPlan = this.data.plans.find(p => p.id === this.data.selectedPlanId);

        try {
            wx.showLoading({ title: '处理中...' });
            // 调用支付接口
            await api.payMembershipOrder(orderId);

            this.setData({ showPayModal: false });
            wx.hideLoading();

            wx.showModal({
                title: '🎉 开通成功',
                content: `恭喜您成为${selectedPlan?.level_display || '会员'}！会员权益已生效。`,
                showCancel: false,
                success: () => {
                    this.refreshUserInfo();
                }
            });
        } catch (err) {
            wx.hideLoading();
            wx.showToast({ title: '支付确认失败', icon: 'none' });
        }
    },

    // 支付弹窗关闭
    onPayClose() {
        this.setData({ showPayModal: false });
        wx.showToast({ title: '已取消支付', icon: 'none' });
    },

    async refreshUserInfo() {
        try {
            const res = await api.getUserInfo();
            app.globalData.userInfo = res;
            wx.setStorageSync('userInfo', res);
            this.loadUserInfo();
        } catch (err) {
            console.error('刷新用户信息失败:', err);
        }
    }
});
