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
            // 模拟订阅详情数据
            const mockSubscription = {
                id: this.data.subscriptionId,
                subscription_no: 'SUB202401001',
                status: 'active',
                status_display: '配送中',

                // 商品信息
                product: {
                    id: 1,
                    name: '每日鲜牛奶',
                    specification: '250ml×1瓶',
                    price: '3.99',
                    subscription_price: '3.59',
                    cover_image: 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&q=80'
                },
                quantity: 1,

                // 配送信息
                frequency: 'weekly',
                frequency_display: '每周一次',
                delivery_day: '周一',
                delivery_time: '08:00-10:00',

                // 周期进度
                total_periods: 12,
                delivered_count: 3,
                remaining_count: 9,

                // 价格信息
                period_price: '3.59',
                total_price: '43.08',
                paid_amount: '10.77',

                // 地址
                receiver_name: '张三',
                receiver_phone: '138****8888',
                receiver_address: '浙江省杭州市西湖区文三路999号',

                // 时间
                start_date: '2024-01-01',
                next_delivery_date: '2024-01-22',
                end_date: '2024-03-25',
                created_at: '2024-01-01 09:30:00'
            };

            // 模拟配送记录
            const mockDeliveryRecords = [
                {
                    id: 1,
                    period: 3,
                    status: 'delivered',
                    status_display: '已送达',
                    delivery_date: '2024-01-15',
                    delivery_time: '08:35',
                    delivery_person: {
                        name: '张师傅',
                        phone: '13800138000',
                        avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&q=80'
                    },
                    signed_by: '本人签收',
                    is_rated: true,
                    rating: 5
                },
                {
                    id: 2,
                    period: 2,
                    status: 'delivered',
                    status_display: '已送达',
                    delivery_date: '2024-01-08',
                    delivery_time: '08:42',
                    delivery_person: {
                        name: '张师傅',
                        phone: '13800138000',
                        avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&q=80'
                    },
                    signed_by: '本人签收',
                    is_rated: true,
                    rating: 5
                },
                {
                    id: 3,
                    period: 1,
                    status: 'delivered',
                    status_display: '已送达',
                    delivery_date: '2024-01-01',
                    delivery_time: '09:15',
                    delivery_person: {
                        name: '李师傅',
                        phone: '13900139000',
                        avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&q=80'
                    },
                    signed_by: '家人代收',
                    is_rated: false,
                    rating: 0
                }
            ];

            // 生成未来配送记录
            const futureRecords = [];
            for (let i = mockSubscription.delivered_count + 1; i <= mockSubscription.total_periods; i++) {
                futureRecords.push({
                    id: 100 + i,
                    period: i,
                    status: i === mockSubscription.delivered_count + 1 ? 'pending' : 'scheduled',
                    status_display: i === mockSubscription.delivered_count + 1 ? '待配送' : '计划中',
                    delivery_date: this.calculateFutureDate(mockSubscription.next_delivery_date, i - mockSubscription.delivered_count - 1, 7),
                    delivery_time: '',
                    delivery_person: null
                });
            }

            this.setData({
                subscription: mockSubscription,
                deliveryRecords: [...futureRecords.reverse(), ...mockDeliveryRecords]
            });
        } catch (err) {
            console.error('加载订阅详情失败:', err);
            wx.showToast({ title: '加载失败', icon: 'none' });
        }
        wx.hideLoading();
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
                        await new Promise(resolve => setTimeout(resolve, 500));
                        wx.hideLoading();
                        wx.showToast({ title: '已暂停', icon: 'success' });
                        this.loadSubscriptionDetail();
                    } catch (err) {
                        wx.hideLoading();
                        wx.showToast({ title: '操作失败', icon: 'none' });
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
                        await new Promise(resolve => setTimeout(resolve, 500));
                        wx.hideLoading();
                        wx.showToast({ title: '已取消', icon: 'success' });
                        setTimeout(() => wx.navigateBack(), 1500);
                    } catch (err) {
                        wx.hideLoading();
                        wx.showToast({ title: '操作失败', icon: 'none' });
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
