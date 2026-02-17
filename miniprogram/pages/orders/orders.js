// pages/orders/orders.js - 订单列表逻辑
const { api, BASE_URL } = require('../../utils/api');

// 获取媒体文件完整URL
const getMediaUrl = (path) => {
    if (!path) return '/assets/products/fresh_milk.jpg';
    if (path.startsWith('http')) return path;
    if (path.startsWith('/assets')) return path;
    // 后端返回的相对路径，拼接服务器地址
    const serverUrl = BASE_URL.replace('/api/v1', '');
    return serverUrl + (path.startsWith('/') ? path : '/' + path);
};

Page({
    data: {
        currentStatus: '',
        orders: [],
        showPayModal: false,
        currentPayOrder: null
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
            const { currentStatus } = this.data;
            const res = await api.getOrders(currentStatus);
            const orders = (res.results || res || []).map(o => ({
                id: o.id,
                order_no: o.order_no,
                status: o.status,
                status_display: o.status_display || this.getStatusDisplay(o.status),
                total_count: o.total_count || (o.items ? o.items.reduce((sum, item) => sum + (item.quantity || 1), 0) : 0),
                total_amount: o.total_amount,
                is_reviewed: o.is_reviewed,
                items: (o.items || []).map(item => ({
                    id: item.id,
                    product_id: item.product_id || item.product?.id,
                    name: item.product_name || item.product?.name || item.name,
                    specification: item.specification || item.product?.specification,
                    price: item.price,
                    quantity: item.quantity,
                    cover_image: getMediaUrl(item.cover_image || item.product_image || item.product?.cover_image)
                }))
            }));
            this.setData({ orders });
        } catch (err) {
            console.error('加载订单失败:', err);
            // API 失败时显示空列表
            this.setData({ orders: [] });
            wx.showToast({ title: '加载失败', icon: 'none' });
        }
        wx.hideLoading();
    },

    getStatusDisplay(status) {
        const statusMap = {
            'pending': '待付款',
            'paid': '待发货',
            'shipped': '待收货',
            'delivered': '已送达',
            'completed': '已完成',
            'cancelled': '已取消'
        };
        return statusMap[status] || status;
    },

    goToOrderDetail(e) {
        const orderNo = e.currentTarget.dataset.orderno;
        wx.navigateTo({ url: `/pages/order-detail/order-detail?order_no=${orderNo}` });
    },

    async cancelOrder(e) {
        const orderNo = e.currentTarget.dataset.orderno;

        wx.showModal({
            title: '取消订单',
            content: '确定要取消这个订单吗？',
            success: async (res) => {
                if (res.confirm) {
                    wx.showLoading({ title: '处理中...' });
                    try {
                        await api.cancelOrder(orderNo);
                        wx.hideLoading();
                        wx.showToast({ title: '已取消', icon: 'success' });
                        this.loadOrders();
                    } catch (err) {
                        wx.hideLoading();
                        wx.showToast({ title: err.message || '取消失败', icon: 'none' });
                    }
                }
            }
        });
    },

    payOrder(e) {
        const orderNo = e.currentTarget.dataset.orderno;
        const order = this.data.orders.find(o => o.order_no === orderNo);

        if (order) {
            this.setData({
                showPayModal: true,
                currentPayOrder: order
            });
        }
    },

    async onPaySuccess(e) {
        const orderNo = e.detail.orderId;

        try {
            // 调用后端支付接口更新订单状态
            await api.payOrder(orderNo);

            wx.showToast({ title: '支付成功', icon: 'success' });

            this.setData({
                showPayModal: false,
                currentPayOrder: null
            });

            // 刷新订单列表
            setTimeout(() => {
                this.loadOrders();
            }, 1500);
        } catch (err) {
            console.error('支付失败:', err);
            wx.showToast({ title: err.message || '支付失败', icon: 'none' });
            this.setData({
                showPayModal: false,
                currentPayOrder: null
            });
        }
    },

    onPayClose() {
        this.setData({
            showPayModal: false,
            currentPayOrder: null
        });
    },

    async confirmReceive(e) {
        const orderNo = e.currentTarget.dataset.orderno;

        wx.showModal({
            title: '确认收货',
            content: '确认已收到商品吗？',
            success: async (res) => {
                if (res.confirm) {
                    wx.showLoading({ title: '处理中...' });
                    try {
                        const result = await api.confirmOrder(orderNo);
                        wx.hideLoading();
                        // 显示获得的积分
                        const points = result.points_earned || 0;
                        if (points > 0) {
                            wx.showToast({ title: `收货成功，+${points}积分`, icon: 'success', duration: 2000 });
                        } else {
                            wx.showToast({ title: '已确认收货', icon: 'success' });
                        }
                        this.loadOrders();
                    } catch (err) {
                        wx.hideLoading();
                        wx.showToast({ title: err.message || '操作失败', icon: 'none' });
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
        const orderNo = e.currentTarget.dataset.orderno;
        wx.navigateTo({ url: `/pages/review/review?order_no=${orderNo}` });
    },

    goShopping() {
        wx.switchTab({ url: '/pages/index/index' });
    }
});
