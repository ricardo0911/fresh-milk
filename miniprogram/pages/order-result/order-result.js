// pages/order-result/order-result.js - 支付结果页
Page({
    data: {
        status: 'success',
        orderId: '',
        amount: '0.00',
        message: '',
        recommendProducts: []
    },

    onLoad(options) {
        this.setData({
            status: options.status || 'success',
            orderId: options.orderId || '',
            amount: options.amount || '0.00',
            message: options.message || ''
        });

        if (options.status === 'success') {
            this.loadRecommendProducts();
        }
    },

    loadRecommendProducts() {
        // 模拟推荐商品
        const products = [
            { id: 1, name: '每日鲜牛奶', price: '39.90', cover_image: 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&q=80' },
            { id: 2, name: '有机纯牛奶', price: '89.00', cover_image: 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80' },
            { id: 3, name: '草莓酸奶', price: '38.00', cover_image: 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&q=80' }
        ];
        this.setData({ recommendProducts: products });
    },

    viewOrder() {
        wx.redirectTo({
            url: '/pages/orders/orders'
        });
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
    }
});
