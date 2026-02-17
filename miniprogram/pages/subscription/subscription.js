// pages/subscription/subscription.js - 周期购逻辑
const { api } = require('../../utils/api');

Page({
    data: {
        currentTab: 'products',
        products: [],
        subscriptions: [],
        showModal: false,
        selectedProduct: null,
        frequency: 'weekly',
        periods: 12,
        quantity: 1,
        startDate: '',
        minDate: '',
        periodPrice: '0.00',
        totalPrice: '0.00'
    },

    onLoad() {
        this.initDate();
        this.loadProducts();
    },

    onShow() {
        if (this.data.currentTab === 'my') {
            this.loadSubscriptions();
        }
    },

    initDate() {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        const dateStr = this.formatDate(tomorrow);
        this.setData({
            startDate: dateStr,
            minDate: dateStr
        });
    },

    formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    },

    switchTab(e) {
        const tab = e.currentTarget.dataset.tab;
        this.setData({ currentTab: tab });
        if (tab === 'my') {
            this.loadSubscriptions();
        }
    },

    switchToProducts() {
        this.setData({ currentTab: 'products' });
    },

    async loadProducts() {
        wx.showLoading({ title: '加载中...' });
        try {
            const res = await api.getSubscriptionProducts();
            const products = (res.results || res || []).map(p => ({
                id: p.id,
                name: p.name,
                specification: p.specification,
                price: p.price,
                original_price: p.original_price,
                subscription_price: p.subscription_price || (parseFloat(p.price) * 0.9).toFixed(2),
                cover_image: p.cover_image || '/assets/products/fresh_milk.jpg'
            }));
            if (products.length > 0) {
                this.setData({ products });
            } else {
                // 如果没有数据，使用默认数据
                this.setData({
                    products: [
                        { id: 1, name: '每日鲜牛奶', specification: '250ml×1瓶', price: '3.99', original_price: '4.99', subscription_price: '3.59', cover_image: '/assets/products/fresh_milk.jpg' },
                        { id: 2, name: 'A2蛋白鲜牛奶', specification: '260ml×1瓶', price: '7.99', original_price: '9.99', subscription_price: '7.19', cover_image: '/assets/products/organic_milk.jpg' }
                    ]
                });
            }
        } catch (err) {
            console.error('加载产品失败:', err);
            // API 失败时使用默认数据
            this.setData({
                products: [
                    { id: 1, name: '每日鲜牛奶', specification: '250ml×1瓶', price: '3.99', original_price: '4.99', subscription_price: '3.59', cover_image: '/assets/products/fresh_milk.jpg' },
                    { id: 2, name: 'A2蛋白鲜牛奶', specification: '260ml×1瓶', price: '7.99', original_price: '9.99', subscription_price: '7.19', cover_image: '/assets/products/organic_milk.jpg' }
                ]
            });
        }
        wx.hideLoading();
    },

    async loadSubscriptions() {
        wx.showLoading({ title: '加载中...' });
        try {
            const res = await api.getSubscriptions();
            const subscriptions = (res.results || res || []).map(s => ({
                id: s.id,
                subscription_no: s.subscription_no,
                status: s.status,
                status_display: s.status_display || this.getStatusDisplay(s.status),
                product: {
                    name: s.product?.name || s.product_name,
                    cover_image: s.product?.cover_image || '/assets/products/fresh_milk.jpg'
                },
                frequency_display: s.frequency_display || this.getFrequencyDisplay(s.frequency),
                total_periods: s.total_periods,
                delivered_count: s.delivered_count || 0,
                next_delivery_date: s.next_delivery_date,
                period_price: s.period_price
            }));
            this.setData({ subscriptions });
        } catch (err) {
            console.error('加载订阅失败:', err);
            this.setData({ subscriptions: [] });
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

    selectProduct(e) {
        const product = e.currentTarget.dataset.product;
        this.setData({
            selectedProduct: product,
            showModal: true
        });
        this.calculatePrice();
    },

    closeModal() {
        this.setData({ showModal: false });
    },

    setFrequency(e) {
        this.setData({ frequency: e.currentTarget.dataset.value });
        this.calculatePrice();
    },

    setPeriods(e) {
        this.setData({ periods: parseInt(e.currentTarget.dataset.value) });
        this.calculatePrice();
    },

    setStartDate(e) {
        this.setData({ startDate: e.detail.value });
    },

    increaseQty() {
        this.setData({ quantity: this.data.quantity + 1 });
        this.calculatePrice();
    },

    decreaseQty() {
        if (this.data.quantity > 1) {
            this.setData({ quantity: this.data.quantity - 1 });
            this.calculatePrice();
        }
    },

    calculatePrice() {
        const { selectedProduct, quantity, periods } = this.data;
        if (!selectedProduct) return;

        const unitPrice = parseFloat(selectedProduct.subscription_price || selectedProduct.price);
        const periodPrice = (unitPrice * quantity).toFixed(2);
        const totalPrice = (unitPrice * quantity * periods).toFixed(2);

        this.setData({ periodPrice, totalPrice });
    },

    async confirmSubscription() {
        const { selectedProduct, frequency, periods, quantity, startDate } = this.data;

        // 检查登录状态
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

        wx.showLoading({ title: '创建订阅中...' });
        try {
            await api.createSubscription({
                product_id: selectedProduct.id,
                frequency,
                total_periods: periods,
                quantity,
                start_date: startDate
            });

            wx.hideLoading();
            wx.showToast({ title: '订阅成功', icon: 'success' });
            this.setData({ showModal: false, currentTab: 'my' });
            this.loadSubscriptions();
        } catch (err) {
            wx.hideLoading();
            wx.showToast({ title: err.message || '订阅失败', icon: 'none' });
        }
    },

    async cancelSubscription(e) {
        const id = e.currentTarget.dataset.id;

        wx.showModal({
            title: '确认暂停',
            content: '暂停后将不再配送，确定暂停吗？',
            success: async (res) => {
                if (res.confirm) {
                    wx.showLoading({ title: '处理中...' });
                    try {
                        await api.cancelSubscription(id);
                        wx.hideLoading();
                        wx.showToast({ title: '已暂停', icon: 'success' });
                        this.loadSubscriptions();
                    } catch (err) {
                        wx.hideLoading();
                        wx.showToast({ title: err.message || '操作失败', icon: 'none' });
                    }
                }
            }
        });
    },

    // 跳转到订阅详情页
    goToSubscriptionDetail(e) {
        const id = e.currentTarget.dataset.id;
        wx.navigateTo({
            url: `/pages/subscription-detail/subscription-detail?id=${id}`
        });
    }
});
