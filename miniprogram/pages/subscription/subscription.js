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
            // 使用模拟数据（后端连接后可切换为API）
            const mockProducts = [
                { id: 1, name: '每日鲜牛奶', specification: '250ml×1瓶', price: '3.99', original_price: '4.99', subscription_price: '3.59', cover_image: 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&q=80' },
                { id: 2, name: 'A2蛋白鲜牛奶', specification: '260ml×1瓶', price: '7.99', original_price: '9.99', subscription_price: '7.19', cover_image: 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80' },
                { id: 3, name: '有机纯牛奶', specification: '200ml×1盒', price: '5.99', original_price: '7.50', subscription_price: '5.39', cover_image: 'https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=400&q=80' },
                { id: 4, name: '低脂鲜牛奶', specification: '500ml×1瓶', price: '8.99', original_price: '11.00', subscription_price: '8.09', cover_image: 'https://images.unsplash.com/photo-1572443490709-e57652c96a1b?w=400&q=80' }
            ];
            this.setData({ products: mockProducts });

            // TODO: 使用真实API
            // const res = await api.getSubscriptionProducts();
            // this.setData({ products: res.results || res });
        } catch (err) {
            console.error('加载产品失败:', err);
        }
        wx.hideLoading();
    },

    async loadSubscriptions() {
        wx.showLoading({ title: '加载中...' });
        try {
            // 使用模拟数据
            const mockSubscriptions = [
                {
                    id: 1,
                    subscription_no: 'SUB202401001',
                    status: 'active',
                    status_display: '配送中',
                    product: { name: '每日鲜牛奶', cover_image: 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&q=80' },
                    frequency_display: '每周一次',
                    total_periods: 12,
                    delivered_count: 3,
                    next_delivery_date: '2024-01-15',
                    period_price: '3.59'
                }
            ];
            this.setData({ subscriptions: mockSubscriptions });

            // TODO: 使用真实API
            // const res = await api.getSubscriptions();
            // this.setData({ subscriptions: res.results || res });
        } catch (err) {
            console.error('加载订阅失败:', err);
        }
        wx.hideLoading();
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
            // TODO: 调用真实API
            // await api.createSubscription({
            //   product_id: selectedProduct.id,
            //   frequency,
            //   total_periods: periods,
            //   quantity,
            //   start_date: startDate
            // });

            // 模拟成功
            await new Promise(resolve => setTimeout(resolve, 1000));

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
                        // TODO: 调用真实API
                        // await api.cancelSubscription(id);
                        await new Promise(resolve => setTimeout(resolve, 500));

                        wx.hideLoading();
                        wx.showToast({ title: '已暂停', icon: 'success' });
                        this.loadSubscriptions();
                    } catch (err) {
                        wx.hideLoading();
                        wx.showToast({ title: '操作失败', icon: 'none' });
                    }
                }
            }
        });
    }
});
