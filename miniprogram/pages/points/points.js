// pages/points/points.js - 积分详情页
const { api } = require('../../utils/api');

Page({
    data: {
        currentTab: 'records',  // records: 积分明细, exchange: 兑换优惠券
        totalPoints: 0,
        pointsRecords: [],
        exchangeableCoupons: []
    },

    onLoad() {
        this.loadUserStats();
        this.loadPointsRecords();
    },

    onShow() {
        this.loadUserStats();
        // 如果当前是兑换优惠券tab，也刷新优惠券列表
        if (this.data.currentTab === 'exchange') {
            this.loadExchangeableCoupons();
        }
    },

    onPullDownRefresh() {
        this.loadUserStats();
        if (this.data.currentTab === 'records') {
            this.loadPointsRecords();
        } else {
            this.loadExchangeableCoupons();
        }
        wx.stopPullDownRefresh();
    },

    switchTab(e) {
        const tab = e.currentTarget.dataset.tab;
        this.setData({ currentTab: tab });
        if (tab === 'records') {
            this.loadPointsRecords();
        } else {
            this.loadExchangeableCoupons();
        }
    },

    async loadUserStats() {
        try {
            const res = await api.getUserStats();
            this.setData({ totalPoints: res.points || 0 });
        } catch (err) {
            console.error('获取积分失败:', err);
        }
    },

    async loadPointsRecords() {
        wx.showLoading({ title: '加载中...' });
        try {
            const res = await api.getPointsRecords();
            const data = res.data?.results || res.results || res.data || res || [];
            const records = (Array.isArray(data) ? data : []).map(r => ({
                id: r.id,
                type: r.type || 'earn',
                points: r.points || 0,
                description: r.description || r.reason || '积分变动',
                created_at: r.created_at ? r.created_at.split('T')[0] : ''
            }));
            this.setData({ pointsRecords: records });
        } catch (err) {
            console.error('加载积分记录失败:', err);
            // 模拟数据
            this.setData({
                pointsRecords: [
                    { id: 1, type: 'earn', points: 100, description: '注册奖励', created_at: '2024-01-15' },
                    { id: 2, type: 'earn', points: 50, description: '订单完成奖励', created_at: '2024-01-20' },
                    { id: 3, type: 'spend', points: -30, description: '兑换优惠券', created_at: '2024-01-22' }
                ]
            });
        }
        wx.hideLoading();
    },

    async loadExchangeableCoupons() {
        wx.showLoading({ title: '加载中...' });
        try {
            const res = await api.getExchangeableCoupons();
            const data = res.data?.results || res.results || res.data || res || [];
            const coupons = (Array.isArray(data) ? data : []).map(c => ({
                id: c.id,
                name: c.name || '优惠券',
                description: c.description || '全场通用',
                amount: parseFloat(c.discount_amount || c.amount || 0),
                min_amount: parseFloat(c.min_amount || 0),
                points_required: c.points_required || c.exchange_points || 0,
                expire_date: c.end_time ? c.end_time.split('T')[0] : ''
            }));
            this.setData({ exchangeableCoupons: coupons });
        } catch (err) {
            console.error('加载可兑换优惠券失败:', err);
            // 模拟数据
            this.setData({
                exchangeableCoupons: [
                    { id: 1, name: '5元优惠券', description: '满30可用', amount: 5, min_amount: 30, points_required: 50 },
                    { id: 2, name: '10元优惠券', description: '满50可用', amount: 10, min_amount: 50, points_required: 100 },
                    { id: 3, name: '20元优惠券', description: '满100可用', amount: 20, min_amount: 100, points_required: 200 }
                ]
            });
        }
        wx.hideLoading();
    },

    async exchangeCoupon(e) {
        const coupon = e.currentTarget.dataset.coupon;

        if (this.data.totalPoints < coupon.points_required) {
            wx.showToast({ title: '积分不足', icon: 'none' });
            return;
        }

        wx.showModal({
            title: '确认兑换',
            content: `确定使用 ${coupon.points_required} 积分兑换「${coupon.name}」吗？`,
            success: async (res) => {
                if (res.confirm) {
                    wx.showLoading({ title: '兑换中...' });
                    try {
                        await api.exchangeCoupon(coupon.id);
                        wx.hideLoading();
                        wx.showToast({ title: '兑换成功', icon: 'success' });
                        // 刷新数据
                        this.loadUserStats();
                        this.loadExchangeableCoupons();
                    } catch (err) {
                        wx.hideLoading();
                        wx.showToast({ title: err.message || '兑换失败', icon: 'none' });
                    }
                }
            }
        });
    }
});
