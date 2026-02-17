// pages/order-result/order-result.js - 支付结果页
const { api } = require('../../utils/api');

Page({
    data: {
        status: 'success',
        orderId: '',
        amount: '0.00',
        message: '',
        payMethod: '微信支付',
        payTime: '',
        recommendProducts: [],
        countdown: 0,
        countdownText: ''
    },

    countdownTimer: null,

    onLoad(options) {
        const now = new Date();
        const payTime = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;

        this.setData({
            status: options.status || 'success',
            orderId: options.orderId || '',
            amount: options.amount || '0.00',
            message: options.message || '',
            payMethod: options.method === 'balance' ? '账户余额' : '微信支付',
            payTime: payTime
        });

        // 设置页面标题
        if (options.status === 'success') {
            wx.setNavigationBarTitle({ title: '支付成功' });
        } else if (options.status === 'fail') {
            wx.setNavigationBarTitle({ title: '支付失败' });
        } else if (options.status === 'pending') {
            wx.setNavigationBarTitle({ title: '待支付' });
            this.startCountdown(30 * 60);
        }

        if (options.status === 'success') {
            this.loadRecommendProducts();
        }
    },

    onUnload() {
        if (this.countdownTimer) {
            clearInterval(this.countdownTimer);
        }
    },

    startCountdown(seconds) {
        this.setData({ countdown: seconds });
        this.updateCountdownText();

        this.countdownTimer = setInterval(() => {
            const countdown = this.data.countdown - 1;
            if (countdown <= 0) {
                clearInterval(this.countdownTimer);
                this.setData({
                    countdown: 0,
                    countdownText: '已超时'
                });
                wx.showToast({ title: '订单已超时', icon: 'none' });
            } else {
                this.setData({ countdown });
                this.updateCountdownText();
            }
        }, 1000);
    },

    updateCountdownText() {
        const { countdown } = this.data;
        const minutes = Math.floor(countdown / 60);
        const seconds = countdown % 60;
        this.setData({
            countdownText: `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
        });
    },

    async loadRecommendProducts() {
        try {
            const res = await api.getProducts({ page_size: 4 });
            const products = (res.results || res || []).map(p => ({
                id: p.id,
                name: p.name,
                price: p.price,
                cover_image: p.cover_image || '/assets/products/fresh_milk.jpg'
            }));
            if (products.length > 0) {
                this.setData({ recommendProducts: products });
            } else {
                // 默认推荐
                this.setData({
                    recommendProducts: [
                        { id: 1, name: '每日鲜牛奶', price: '39.90', cover_image: '/assets/products/fresh_milk.jpg' },
                        { id: 2, name: '有机纯牛奶', price: '89.00', cover_image: '/assets/products/organic_milk.jpg' }
                    ]
                });
            }
        } catch (err) {
            console.error('加载推荐商品失败:', err);
            this.setData({
                recommendProducts: [
                    { id: 1, name: '每日鲜牛奶', price: '39.90', cover_image: '/assets/products/fresh_milk.jpg' },
                    { id: 2, name: '有机纯牛奶', price: '89.00', cover_image: '/assets/products/organic_milk.jpg' }
                ]
            });
        }
    },

    viewOrder() {
        if (this.data.orderId) {
            wx.redirectTo({
                url: `/pages/order-detail/order-detail?id=${this.data.orderId}`
            });
        } else {
            wx.redirectTo({
                url: '/pages/orders/orders'
            });
        }
    },

    goHome() {
        wx.switchTab({
            url: '/pages/index/index'
        });
    },

    goToProduct(e) {
        const id = e.currentTarget.dataset.id;
        wx.navigateTo({
            url: `/pages/product/product?id=${id}`
        });
    },

    retryPay() {
        wx.navigateBack();
    },

    payNow() {
        if (this.data.orderId) {
            wx.redirectTo({
                url: `/pages/order-detail/order-detail?id=${this.data.orderId}&action=pay`
            });
        }
    }
});
