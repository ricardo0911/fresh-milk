// pages/index/index.js - 首页逻辑
const app = getApp();

Page({
    data: {
        banners: [
            { id: 1, image: 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=800&q=80' },
            { id: 2, image: 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=800&q=80' },
            { id: 3, image: 'https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=800&q=80' }
        ],
        features: [
            { id: 1, icon: '🌿', name: '新鲜直达', type: 'fresh' },
            { id: 2, icon: '📅', name: '周期购', type: 'subscription' },
            { id: 3, icon: '🎁', name: '领券中心', type: 'coupon' },
            { id: 4, icon: '📞', name: '客服', type: 'service' }
        ],
        categories: [
            { id: 1, icon: '🥛', name: '鲜牛奶' },
            { id: 2, icon: '🍶', name: '酸奶' },
            { id: 3, icon: '🧀', name: '奶酪' },
            { id: 4, icon: '🌿', name: '有机奶' },
            { id: 5, icon: '👶', name: '儿童奶' }
        ],
        hotProducts: [],
        newProducts: [],
        guessProducts: []
    },

    onLoad() {
        this.loadProducts();
        this.loadGuessProducts();
    },

    onShow() {
        app.updateCartBadge();
    },

    onPullDownRefresh() {
        Promise.all([
            this.loadProducts(),
            this.loadGuessProducts()
        ]).then(() => {
            wx.stopPullDownRefresh();
        });
    },

    // 加载产品数据
    async loadProducts() {
        // 使用本地图片
        const mockProducts = [
            { id: 1, name: '每日鲜牛奶', specification: '250ml×10瓶', price: '39.90', original_price: '49.90', cover_image: '/assets/products/fresh_milk.jpg', is_hot: true },
            { id: 2, name: '有机纯牛奶', specification: '1L×6盒', price: '89.00', original_price: '108.00', cover_image: '/assets/products/organic_milk.jpg', is_hot: true, is_new: true },
            { id: 3, name: '低脂鲜牛奶', specification: '500ml×8瓶', price: '56.80', cover_image: '/assets/products/fresh_milk.jpg', is_hot: true },
            { id: 4, name: '儿童成长奶', specification: '200ml×12瓶', price: '68.00', cover_image: '/assets/products/children_milk.jpg', is_new: true },
            { id: 5, name: 'A2蛋白鲜牛奶', specification: '950ml×2瓶', price: '45.00', cover_image: '/assets/products/organic_milk.jpg', is_new: true },
            { id: 6, name: '草莓味酸奶', specification: '100g×12杯', price: '38.00', cover_image: '/assets/products/strawberry_yogurt.jpg', is_new: true }
        ];

        this.setData({
            hotProducts: mockProducts.filter(p => p.is_hot),
            newProducts: mockProducts.filter(p => p.is_new)
        });
    },

    // 加载猜你喜欢数据
    async loadGuessProducts() {
        // 使用本地图片
        const guessProducts = [
            {
                id: 7,
                name: '特仑苏有机纯牛奶',
                specification: '250ml×10瓶',
                price: '78',
                cover_image: '/assets/products/organic_milk.jpg',
                fresh_days: 6
            },
            {
                id: 8,
                name: '德国进口有机奶',
                specification: '200ml×12包',
                price: '55',
                cover_image: '/assets/products/fresh_milk.jpg',
                fresh_days: 10
            },
            {
                id: 9,
                name: '有机甄选限定上市',
                specification: '250ml×12盒',
                price: '66',
                cover_image: '/assets/products/organic_milk.jpg',
                fresh_days: 8
            },
            {
                id: 10,
                name: '有机营养家庭周货',
                specification: '250ml×24盒',
                price: '187',
                cover_image: '/assets/products/children_milk.jpg',
                fresh_days: 17
            }
        ];

        this.setData({ guessProducts });
    },

    // 添加到购物车
    addToCart(e) {
        const product = e.currentTarget.dataset.product;
        let cart = wx.getStorageSync('cart') || [];

        const existingIndex = cart.findIndex(item => item.product.id === product.id);
        if (existingIndex > -1) {
            cart[existingIndex].quantity += 1;
        } else {
            cart.push({ product, quantity: 1 });
        }

        wx.setStorageSync('cart', cart);
        app.updateCartBadge();

        wx.showToast({
            title: '已加入购物车',
            icon: 'success'
        });
    },

    // 跳转到搜索
    goToSearch() {
        wx.navigateTo({ url: '/pages/search/search' });
    },

    // 跳转到分类
    goToCategory() {
        wx.switchTab({ url: '/pages/category/category' });
    },

    // 跳转到分类详情
    goToCategoryDetail(e) {
        const id = e.currentTarget.dataset.id;
        wx.navigateTo({ url: `/pages/category/category?id=${id}` });
    },

    // 跳转到产品列表
    goToProducts(e) {
        const filter = e.currentTarget.dataset.filter;
        wx.navigateTo({ url: `/pages/products/products?filter=${filter}` });
    },

    // 跳转到产品详情
    goToProduct(e) {
        const id = e.currentTarget.dataset.id;
        wx.navigateTo({ url: `/pages/product/product?id=${id}` });
    },

    // 跳转到功能页
    goToFeature(e) {
        const type = e.currentTarget.dataset.type;
        switch (type) {
            case 'subscription':
                wx.navigateTo({ url: '/pages/subscription/subscription' });
                break;
            case 'coupon':
                wx.navigateTo({ url: '/pages/coupon/coupon' });
                break;
            case 'service':
                wx.makePhoneCall({ phoneNumber: '400-888-8888' });
                break;
            default:
                break;
        }
    },

    // 周期购
    goToSubscription() {
        wx.navigateTo({ url: '/pages/subscription/subscription' });
    },

    // 会员专区
    goToMember() {
        wx.showToast({ title: '会员功能开发中', icon: 'none' });
        // TODO: 跳转到会员页面
        // wx.navigateTo({ url: '/pages/member/member' });
    }
});
