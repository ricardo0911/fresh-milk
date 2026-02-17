// pages/coupon/coupon.js - 优惠券中心逻辑
const { api } = require('../../utils/api');

Page({
    data: {
        currentTab: 'available',
        statusFilter: 'unused',
        availableCoupons: [],
        myCoupons: [],
        selectMode: false  // 是否从订单页跳转过来选择优惠券
    },

    onLoad(options) {
        // 如果是选择模式，直接显示我的优惠券-未使用
        if (options.select === '1') {
            this.setData({
                selectMode: true,
                currentTab: 'my',
                statusFilter: 'unused'
            });
            this.loadMyCoupons();
        } else {
            this.loadAvailableCoupons();
        }
    },

    onShow() {
        if (this.data.currentTab === 'my') {
            this.loadMyCoupons();
        }
    },

    switchTab(e) {
        const tab = e.currentTarget.dataset.tab;
        this.setData({ currentTab: tab });
        if (tab === 'available') {
            this.loadAvailableCoupons();
        } else {
            this.loadMyCoupons();
        }
    },

    goToAvailable() {
        this.setData({ currentTab: 'available' });
    },

    setStatusFilter(e) {
        this.setData({ statusFilter: e.currentTarget.dataset.status });
        this.loadMyCoupons();
    },

    async loadAvailableCoupons() {
        wx.showLoading({ title: '加载中...' });
        try {
            const res = await api.getAvailableCoupons();
            const data = res.data?.results || res.results || res.data || res || [];
            const coupons = (Array.isArray(data) ? data : []).map(c => ({
                id: c.id,
                name: c.name || '优惠券',
                description: c.description || '全场通用',
                amount: parseFloat(c.discount_amount || c.amount || 0),
                min_amount: parseFloat(c.min_amount || 0),
                expire_date: c.end_time ? c.end_time.split('T')[0] : ''
            }));
            this.setData({ availableCoupons: coupons });
        } catch (err) {
            console.error('加载优惠券失败:', err);
            // 如果API失败，使用模拟数据
            const mockCoupons = [
                { id: 1, name: '新人优惠券', description: '全场通用', amount: 10, min_amount: 50, expire_date: '2024-02-28' },
                { id: 2, name: '周期购专享', description: '周期购订单可用', amount: 20, min_amount: 100, expire_date: '2024-03-31' },
                { id: 3, name: '满减优惠', description: '全场通用', amount: 15, min_amount: 80, expire_date: '2024-02-15' }
            ];
            this.setData({ availableCoupons: mockCoupons });
        }
        wx.hideLoading();
    },

    async loadMyCoupons() {
        wx.showLoading({ title: '加载中...' });
        try {
            const res = await api.getMyCoupons(this.data.statusFilter);
            console.log('My coupons response:', JSON.stringify(res));
            const data = res.data?.results || res.results || res.data || res || [];
            const coupons = (Array.isArray(data) ? data : []).map(c => {
                // 后端返回 coupon_detail 包含优惠券详情，coupon 只是 ID
                const couponDetail = c.coupon_detail || (typeof c.coupon === 'object' ? c.coupon : null) || {};
                // 处理日期格式（可能是 "2026-02-12T00:00:00" 或 "2026-02-12 00:00:00"）
                const endTime = couponDetail.end_time || c.expire_date || '';
                const expireDate = endTime.split('T')[0].split(' ')[0];
                return {
                    id: c.id,
                    coupon_id: couponDetail.id || c.coupon_id || c.coupon,
                    name: couponDetail.name || c.name || '优惠券',
                    description: couponDetail.description || c.description || '全场通用',
                    amount: parseFloat(couponDetail.discount_amount || couponDetail.amount || c.amount || 0),
                    min_amount: parseFloat(couponDetail.min_amount || c.min_amount || 0),
                    expire_date: expireDate,
                    status: c.status || 'unused'
                };
            });
            this.setData({ myCoupons: coupons });
        } catch (err) {
            console.error('加载优惠券失败:', err);
            // 如果API失败，使用模拟数据
            const allCoupons = [
                { id: 10, name: '新人优惠券', description: '全场通用', amount: 10, min_amount: 50, expire_date: '2024-02-28', status: 'unused' },
                { id: 11, name: '满减优惠', description: '全场通用', amount: 5, min_amount: 30, expire_date: '2024-01-10', status: 'used' },
                { id: 12, name: '周期购优惠', description: '周期购订单可用', amount: 15, min_amount: 60, expire_date: '2023-12-31', status: 'expired' }
            ];
            const filtered = allCoupons.filter(c => c.status === this.data.statusFilter);
            this.setData({ myCoupons: filtered });
        }
        wx.hideLoading();
    },

    async claimCoupon(e) {
        const id = e.currentTarget.dataset.id;
        const token = wx.getStorageSync('token');

        if (!token) {
            wx.showModal({
                title: '提示',
                content: '请先登录',
                confirmText: '去登录',
                success: (res) => {
                    if (res.confirm) {
                        wx.navigateTo({ url: '/pages/login/login' });
                    }
                }
            });
            return;
        }

        wx.showLoading({ title: '领取中...' });
        try {
            await api.claimCoupon(id);

            wx.hideLoading();
            wx.showToast({ title: '领取成功', icon: 'success' });

            // 从可领取列表中移除
            const availableCoupons = this.data.availableCoupons.filter(c => c.id !== id);
            this.setData({ availableCoupons });
        } catch (err) {
            wx.hideLoading();
            wx.showToast({ title: err.message || '领取失败', icon: 'none' });
        }
    },

    // 使用优惠券 (从订单页跳转过来时)
    useCoupon(e) {
        const coupon = e.currentTarget.dataset.coupon;

        if (this.data.selectMode) {
            // 将选中的优惠券存入 storage，供订单页读取
            wx.setStorageSync('selectedCoupon', coupon);
            wx.showToast({ title: '已选择优惠券', icon: 'success', duration: 800 });

            setTimeout(() => {
                wx.navigateBack();
            }, 800);
        } else {
            // 非选择模式，跳转到首页去购物
            wx.switchTab({ url: '/pages/index/index' });
        }
    }
});

