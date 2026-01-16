// pages/orders/orders.js - 订单列表逻辑
const { api } = require('../../utils/api');

Page({
    data: {
        currentStatus: '',
        orders: []
    },

    onLoad(options) {
        if (options.status) {
            this.setData({ currentStatus: options.status });
        }
        this.loadOrders();
    },

    onShow() {
        this.loadOrders();
    },

    onPullDownRefresh() {
        this.loadOrders().then(() => {
            wx.stopPullDownRefresh();
        });
    },

    switchStatus(e) {
        const status = e.currentTarget.dataset.status;
        this.setData({ currentStatus: status });
        this.loadOrders();
    },

    async loadOrders() {
        wx.showLoading({ title: '加载中...' });
        try {
            // 模拟数据
            const allOrders = [
                {
                    id: 1,
                    order_no: 'ORD202401150001',
                    status: 'pending',
                    status_display: '待付款',
                    total_count: 2,
                    total_amount: '89.80',
                    items: [
                        { id: 1, name: '每日鲜牛奶', specification: '250ml×10瓶', price: '39.90', quantity: 1, cover_image: 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&q=80' },
                        { id: 2, name: '有机纯牛奶', specification: '1L×6盒', price: '49.90', quantity: 1, cover_image: 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80' }
                    ]
                },
                {
                    id: 2,
                    order_no: 'ORD202401140002',
                    status: 'shipped',
                    status_display: '配送中',
                    total_count: 1,
                    total_amount: '56.80',
                    items: [
                        { id: 3, name: '低脂鲜牛奶', specification: '500ml×8瓶', price: '56.80', quantity: 1, cover_image: 'https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=400&q=80' }
                    ]
                },
                {
                    id: 3,
                    order_no: 'ORD202401100003',
                    status: 'completed',
                    status_display: '已完成',
                    total_count: 3,
                    total_amount: '128.00',
                    is_reviewed: false,
                    items: [
                        { id: 4, name: '儿童成长奶', specification: '200ml×12瓶', price: '68.00', quantity: 1, cover_image: 'https://images.unsplash.com/photo-1572443490709-e57652c96a1b?w=400&q=80' },
                        { id: 5, name: '草莓味酸奶', specification: '100g×12杯', price: '60.00', quantity: 1, cover_image: 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&q=80' }
                    ]
                }
            ];

            const { currentStatus } = this.data;
            const filtered = currentStatus
                ? allOrders.filter(o => o.status === currentStatus)
                : allOrders;

            this.setData({ orders: filtered });
        } catch (err) {
            console.error('加载订单失败:', err);
        }
        wx.hideLoading();
    },

    goToOrderDetail(e) {
        const id = e.currentTarget.dataset.id;
        wx.navigateTo({ url: `/pages/order-detail/order-detail?id=${id}` });
    },

    async cancelOrder(e) {
        const id = e.currentTarget.dataset.id;

        wx.showModal({
            title: '取消订单',
            content: '确定要取消这个订单吗？',
            success: async (res) => {
                if (res.confirm) {
                    wx.showLoading({ title: '处理中...' });
                    try {
                        // TODO: 调用API
                        // await api.cancelOrder(id);
                        await new Promise(resolve => setTimeout(resolve, 500));

                        wx.hideLoading();
                        wx.showToast({ title: '已取消', icon: 'success' });
                        this.loadOrders();
                    } catch (err) {
                        wx.hideLoading();
                        wx.showToast({ title: '取消失败', icon: 'none' });
                    }
                }
            }
        });
    },

    payOrder(e) {
        const id = e.currentTarget.dataset.id;
        // 跳转到支付页面或调用支付
        wx.showToast({ title: '跳转支付中...', icon: 'loading' });
        setTimeout(() => {
            wx.showToast({ title: '支付成功', icon: 'success' });
            this.loadOrders();
        }, 1500);
    },

    async confirmReceive(e) {
        const id = e.currentTarget.dataset.id;

        wx.showModal({
            title: '确认收货',
            content: '确认已收到商品吗？',
            success: async (res) => {
                if (res.confirm) {
                    wx.showLoading({ title: '处理中...' });
                    try {
                        // TODO: 调用API
                        // await api.confirmOrder(id);
                        await new Promise(resolve => setTimeout(resolve, 500));

                        wx.hideLoading();
                        wx.showToast({ title: '已确认收货', icon: 'success' });
                        this.loadOrders();
                    } catch (err) {
                        wx.hideLoading();
                        wx.showToast({ title: '操作失败', icon: 'none' });
                    }
                }
            }
        });
    },

    buyAgain(e) {
        const order = e.currentTarget.dataset.order;
        // 将商品加入购物车
        let cart = wx.getStorageSync('cart') || [];

        order.items.forEach(item => {
            const existingIndex = cart.findIndex(c => c.product.id === item.id);
            if (existingIndex > -1) {
                cart[existingIndex].quantity += item.quantity;
            } else {
                cart.push({ product: item, quantity: item.quantity });
            }
        });

        wx.setStorageSync('cart', cart);
        wx.showToast({ title: '已加入购物车', icon: 'success' });
    },

    goToReview(e) {
        const id = e.currentTarget.dataset.id;
        wx.navigateTo({ url: `/pages/review/review?order_id=${id}` });
    },

    goShopping() {
        wx.switchTab({ url: '/pages/index/index' });
    }
});
