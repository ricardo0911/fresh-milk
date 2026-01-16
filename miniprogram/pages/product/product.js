// pages/product/product.js
const app = getApp();

Page({
    data: {
        product: {},
        images: [],
        currentTab: 'detail',
        reviews: [
            { id: 1, name: '王女士', avatar: 'https://i.pravatar.cc/100?img=1', rating: '⭐⭐⭐⭐⭐', content: '牛奶很新鲜，孩子特别喜欢喝！' },
            { id: 2, name: '李先生', avatar: 'https://i.pravatar.cc/100?img=3', rating: '⭐⭐⭐⭐⭐', content: '品质没得说，比超市的新鲜多了！' }
        ],
        savingAmount: '0',
        cartCount: 0
    },

    onLoad(options) {
        const id = options.id;
        this.loadProduct(id);
    },

    onShow() {
        const cart = wx.getStorageSync('cart') || [];
        const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);
        this.setData({ cartCount });
    },

    loadProduct(id) {
        // 模拟数据
        const mockProducts = {
            1: { id: 1, name: '每日鲜牛奶', specification: '250ml×10瓶', price: '39.90', original_price: '49.90', cover_image: '/assets/products/fresh_milk.jpg', is_hot: true },
            2: { id: 2, name: '有机纯牛奶', specification: '1L×6盒', price: '89.00', original_price: '108.00', cover_image: '/assets/products/organic_milk.jpg', is_hot: true, is_new: true }
        };

        const product = mockProducts[id] || mockProducts[1];
        const savingAmount = product.original_price ? (parseFloat(product.original_price) - parseFloat(product.price)).toFixed(2) : '0';

        // 计算会员价
        let memberPrice = product.price;
        let memberDiscountLabel = '';
        const userInfo = app.globalData.userInfo;

        if (userInfo && userInfo.member_level) {
            const rates = {
                'regular': 1.0,
                'silver': 0.95,
                'gold': 0.90,
                'platinum': 0.85,
            };
            const labels = {
                'regular': '普通会员',
                'silver': '银卡会员',
                'gold': '金卡会员',
                'platinum': '铂金会员',
            };
            const rate = rates[userInfo.member_level] || 1.0;
            if (rate < 1.0) {
                memberPrice = (parseFloat(product.price) * rate).toFixed(2);
                memberDiscountLabel = labels[userInfo.member_level];
            }
        }

        this.setData({
            product,
            images: [
                product.cover_image,
                '/assets/products/organic_milk.jpg',
                '/assets/products/children_milk.jpg'
            ],
            savingAmount,
            memberPrice,
            memberDiscountLabel
        });

        wx.setNavigationBarTitle({ title: product.name });
    },

    previewImage(e) {
        const url = e.currentTarget.dataset.url;
        wx.previewImage({
            current: url,
            urls: this.data.images
        });
    },

    switchTab(e) {
        const tab = e.currentTarget.dataset.tab;
        this.setData({ currentTab: tab });
    },

    addToCart() {
        const { product } = this.data;
        let cart = wx.getStorageSync('cart') || [];

        const existingIndex = cart.findIndex(item => item.product.id === product.id);
        if (existingIndex > -1) {
            cart[existingIndex].quantity += 1;
        } else {
            cart.push({ product, quantity: 1 });
        }

        wx.setStorageSync('cart', cart);
        app.updateCartBadge();

        const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);
        this.setData({ cartCount });

        wx.showToast({ title: '已加入购物车', icon: 'success' });
    },

    buyNow() {
        this.addToCart();
        wx.switchTab({ url: '/pages/cart/cart' });
    },

    goToHome() {
        wx.switchTab({ url: '/pages/index/index' });
    },

    goToCart() {
        wx.switchTab({ url: '/pages/cart/cart' });
    }
});
