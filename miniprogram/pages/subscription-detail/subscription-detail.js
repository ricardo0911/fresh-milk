// pages/subscription-detail/subscription-detail.js - 周期购详情逻辑
const { api } = require('../../utils/api');

Page({
    data: {
        subscriptionId: null,
        subscription: null,
        deliveryRecords: []
    },

    onLoad(options) {
        if (options.id) {
            this.setData({ subscriptionId: options.id });
            this.loadSubscriptionDetail();
        }
    },

    onShow() {
        if (this.data.subscriptionId) {
            this.loadSubscriptionDetail();
        }
    },

    onPullDownRefresh() {
        this.loadSubscriptionDetail().then(() => {
            wx.stopPullDownRefresh();
        });
    },

    async loadSubscriptionDetail() {
        wx.showLoading({ title: '加载中...' });
        try {
            const res = await api.getSubscription(this.data.subscriptionId);
            const subscription = {
                id: res.id,
                subscription_no: res.subscription_no,
                status: res.status,
                status_display: res.status_display || this.getStatusDisplay(res.status),
                product: {
                    id: res.product?.id || res.product_id,
                    name: res.product?.name || res.product_name,
                    specification: res.product?.specification,
                    price: res.product?.price,
                    subscription_price: res.product?.subscription_price || res.period_price,
                    cover_image: res.product?.cover_image || '/assets/products/fresh_milk.jpg'
                },
                quantity: res.quantity || 1,
                frequency: res.frequency,
                frequency_display: res.frequency_display || this.getFrequencyDisplay(res.frequency),
                delivery_day: res.delivery_day,
                delivery_time: res.delivery_time,
                total_periods: res.total_periods,
                delivered_count: res.delivered_count || 0,
                remaining_count: res.total_periods - (res.delivered_count || 0),
                period_price: res.period_price,
                total_price: res.total_price,
                paid_amount: res.paid_amount,
                receiver_name: res.receiver_name || res.address?.name,
                receiver_phone: res.receiver_phone || res.address?.phone,
                receiver_address: res.receiver_address || res.address?.full_address,
                start_date: res.start_date,
                next_delivery_date: res.next_delivery_date,
                end_date: res.end_date,
                created_at: res.created_at
            };

            // 配送记录
            const deliveryRecords = (res.delivery_records || []).map(r => ({
                id: r.id,
                period: r.period,
                status: r.status,
                status_display: r.status_display || this.getDeliveryStatusDisplay(r.status),
                delivery_date: r.delivery_date,
                delivery_time: r.delivery_time,
                delivery_person: r.delivery_person ? {
                    name: r.delivery_person.name,
                    phone: r.delivery_person.phone,
                    avatar: r.delivery_person.avatar || '/assets/default_avatar.png'
                } : null,
                signed_by: r.signed_by,
                is_rated: r.is_rated,
                rating: r.rating
            }));

            // 生成未来配送记录
            const futureRecords = [];
            for (let i = subscription.delivered_count + 1; i <= subscription.total_periods; i++) {
                futureRecords.push({
                    id: 100 + i,
                    period: i,
                    status: i === subscription.delivered_count + 1 ? 'pending' : 'scheduled',
                    status_display: i === subscription.delivered_count + 1 ? '待配送' : '计划中',
                    delivery_date: this.calculateFutureDate(subscription.next_delivery_date, i - subscription.delivered_count - 1, 7),
                    delivery_time: '',
                    delivery_person: null
                });
            }

            this.setData({
                subscription,
                deliveryRecords: [...futureRecords.reverse(), ...deliveryRecords]
            });
        } catch (err) {
            console.error('加载订阅详情失败:', err);
            wx.showToast({ title: '加载失败', icon: 'none' });
        }
        wx.hideLoading();
    },

    getStatusDisplay(status) {
        const map = { 'active': '配送中', 'paused': '已暂停', 'completed': '已完成', 'cancelled': '已取消' };
        return map[status] || status;
    },

    getFrequencyDisplay(frequency) {
        const map = { 'daily': '每天', 'weekly': '每周一次', 'biweekly': '每两周一次', 'monthly': '每月一次' };
        return map[frequency] || frequency;
    },

    getDeliveryStatusDisplay(status) {
        const map = { 'pending': '待配送', 'delivering': '配送中', 'delivered': '已送达', 'scheduled': '计划中' };
        return map[status] || status;
    },

    calculateFutureDate(startDate, weeksToAdd, daysPerWeek) {
        const date = new Date(startDate);
        date.setDate(date.getDate() + weeksToAdd * daysPerWeek);
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    },

    // 拨打配送员电话
    callDelivery(e) {
        const phone = e.currentTarget.dataset.phone;
        if (phone) {
            wx.makePhoneCall({ phoneNumber: phone });
        }
    },

    // 评价配送
    rateDelivery(e) {
        const recordId = e.currentTarget.dataset.id;
        wx.showToast({ title: '评价功能开发中', icon: 'none' });
    },

    // 暂停订阅
    pauseSubscription() {
        wx.showModal({
            title: '暂停订阅',
            content: '暂停后将不再配送，确定暂停吗？您可以随时恢复。',
            success: async (res) => {
                if (res.confirm) {
                    wx.showLoading({ title: '处理中...' });
                    try {
                        await api.pauseSubscription(this.data.subscriptionId);
                        wx.hideLoading();
                        wx.showToast({ title: '已暂停', icon: 'success' });
                        this.loadSubscriptionDetail();
                    } catch (err) {
                        wx.hideLoading();
                        wx.showToast({ title: err.message || '操作失败', icon: 'none' });
                    }
                }
            }
        });
    },

    // 取消订阅
    cancelSubscription() {
        wx.showModal({
            title: '取消订阅',
            content: '取消后剩余期数将不再配送，已付款项将按比例退还。确定取消吗？',
            confirmColor: '#e53935',
            success: async (res) => {
                if (res.confirm) {
                    wx.showLoading({ title: '处理中...' });
                    try {
                        await api.cancelSubscription(this.data.subscriptionId);
                        wx.hideLoading();
                        wx.showToast({ title: '已取消', icon: 'success' });
                        setTimeout(() => wx.navigateBack(), 1500);
                    } catch (err) {
                        wx.hideLoading();
                        wx.showToast({ title: err.message || '操作失败', icon: 'none' });
                    }
                }
            }
        });
    },

    // 修改地址
    changeAddress() {
        wx.navigateTo({ url: '/pages/address/address?select=1' });
    },

    // 修改配送时间
    changeDeliveryTime() {
        wx.showToast({ title: '功能开发中', icon: 'none' });
    }
});
