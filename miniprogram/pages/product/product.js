// pages/product/product.js
const app = getApp();
const { api } = require('../../utils/api');

Page({
    data: {
        product: {},
        images: [],
        reviews: [],
        currentTab: 'detail',
        savingAmount: '0',
        cartCount: 0,
        memberPrice: '',
        memberDiscountLabel: ''
    },

    onLoad(options) {
        const id = options.id;
        if (id) {
            this.loadProduct(id);
            this.loadReviews(id);
        }
    },

    onShow() {
        const cart = wx.getStorageSync('cart') || [];
        const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);
        this.setData({ cartCount });
    },

    loadProduct(id) {
        wx.showLoading({ title: '加载中...' });

        api.getProduct(id).then(product => {
            wx.hideLoading();

            const savingAmount = product.original_price
                ? (parseFloat(product.original_price) - parseFloat(product.price)).toFixed(2)
                : '0';

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

            // 图片列表：优先使用 images 字段，否则使用 cover_image
            const images = product.images && product.images.length > 0
                ? product.images
                : (product.cover_image ? [product.cover_image] : []);

            this.setData({
                product,
                images,
                savingAmount,
                memberPrice,
                memberDiscountLabel
            });

            wx.setNavigationBarTitle({ title: product.name });
        }).catch(err => {
            wx.hideLoading();
            wx.showToast({ title: '加载失败', icon: 'none' });
            console.error('加载产品失败:', err);
        });
    },

    loadReviews(productId) {
        // 从评论 API 获取该产品的评价
        if (api.getProductReviews) {
            api.getProductReviews(productId).then(reviews => {
                this.setData({ reviews: reviews || [] });
            }).catch(err => {
                console.error('加载评价失败:', err);
            });
        }
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
        if (!product.id) {
            wx.showToast({ title: '产品信息错误', icon: 'none' });
            return;
        }

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
