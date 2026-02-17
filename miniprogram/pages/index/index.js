// pages/index/index.js - 首页逻辑
const app = getApp();
const { api } = require('../../utils/api');

Page({
    data: {
        banners: [],
        features: [
            { id: 1, icon: '🌿', name: '新鲜直达', type: 'fresh' },
            { id: 2, icon: '📅', name: '周期购', type: 'subscription' },
            { id: 3, icon: '🎁', name: '领券中心', type: 'coupon' },
            { id: 4, icon: '📞', name: '客服', type: 'service' }
        ],
        categories: [],
        hotProducts: [],
        newProducts: [],
        guessProducts: []
    },

    onLoad() {
        console.log('首页 onLoad 触发');
        try {
            this.loadBanners();
            this.loadCategories();
            this.loadProducts();
            this.loadGuessProducts();
        } catch (err) {
            console.error('首页加载数据失败:', err);
        }
    },

    onShow() {
        app.updateCartBadge();
    },

    onPullDownRefresh() {
        Promise.all([
            this.loadBanners(),
            this.loadCategories(),
            this.loadProducts(),
            this.loadGuessProducts()
        ]).then(() => {
            wx.stopPullDownRefresh();
        });
    },

    // 加载轮播图
    async loadBanners() {
        try {
            const res = await api.getProducts({ is_banner: true });
            const banners = (res.results || res || []).slice(0, 5).map((p, index) => ({
                id: p.id || index + 1,
                image: p.cover_image || '/assets/products/fresh_milk.jpg'
            }));
            if (banners.length > 0) {
                this.setData({ banners });
            } else {
                // 默认轮播图
                this.setData({
                    banners: [
                        { id: 1, image: '/assets/products/fresh_milk.jpg' },
                        { id: 2, image: '/assets/products/organic_milk.jpg' },
                        { id: 3, image: '/assets/products/strawberry_yogurt.jpg' }
                    ]
                });
            }
        } catch (err) {
            console.error('加载轮播图失败:', err);
            this.setData({
                banners: [
                    { id: 1, image: '/assets/products/fresh_milk.jpg' },
                    { id: 2, image: '/assets/products/organic_milk.jpg' },
                    { id: 3, image: '/assets/products/strawberry_yogurt.jpg' }
                ]
            });
        }
    },

    // 加载分类
    async loadCategories() {
        try {
            const res = await api.getCategories();
            const categories = (res.results || res || []).slice(0, 5).map(c => ({
                id: c.id,
                icon: c.icon || '🥛',
                name: c.name
            }));
            if (categories.length > 0) {
                this.setData({ categories });
            }
        } catch (err) {
            console.error('加载分类失败:', err);
            // 使用默认分类
            this.setData({
                categories: [
                    { id: 1, icon: '🥛', name: '鲜牛奶' },
                    { id: 2, icon: '🍶', name: '酸奶' },
                    { id: 3, icon: '🧀', name: '奶酪' },
                    { id: 4, icon: '🌿', name: '有机奶' },
                    { id: 5, icon: '👶', name: '儿童奶' }
                ]
            });
        }
    },

    // 加载产品数据
    async loadProducts() {
        try {
            // 并行加载热门和新品
            const [hotRes, newRes] = await Promise.all([
                api.getHotProducts(),
                api.getNewProducts()
            ]);

            const hotProducts = (hotRes.results || hotRes || []).map(p => ({
                id: p.id,
                name: p.name,
                specification: p.specification,
                price: p.price,
                original_price: p.original_price,
                cover_image: p.cover_image || '/assets/products/fresh_milk.jpg',
                is_hot: true
            }));

            const newProducts = (newRes.results || newRes || []).map(p => ({
                id: p.id,
                name: p.name,
                specification: p.specification,
                price: p.price,
                original_price: p.original_price,
                cover_image: p.cover_image || '/assets/products/fresh_milk.jpg',
                is_new: true
            }));

            this.setData({ hotProducts, newProducts });
        } catch (err) {
            console.error('加载产品失败:', err);
            // API 失败时使用本地图片的默认数据
            const defaultProducts = [
                { id: 1, name: '每日鲜牛奶', specification: '250ml×10瓶', price: '39.90', original_price: '49.90', cover_image: '/assets/products/fresh_milk.jpg', is_hot: true },
                { id: 2, name: '有机纯牛奶', specification: '1L×6盒', price: '89.00', original_price: '108.00', cover_image: '/assets/products/organic_milk.jpg', is_hot: true, is_new: true },
                { id: 3, name: '低脂鲜牛奶', specification: '500ml×8瓶', price: '56.80', cover_image: '/assets/products/fresh_milk.jpg', is_hot: true },
                { id: 4, name: '儿童成长奶', specification: '200ml×12瓶', price: '68.00', cover_image: '/assets/products/children_milk.jpg', is_new: true },
                { id: 5, name: 'A2蛋白鲜牛奶', specification: '950ml×2瓶', price: '45.00', cover_image: '/assets/products/organic_milk.jpg', is_new: true },
                { id: 6, name: '草莓味酸奶', specification: '100g×12杯', price: '38.00', cover_image: '/assets/products/strawberry_yogurt.jpg', is_new: true }
            ];
            this.setData({
                hotProducts: defaultProducts.filter(p => p.is_hot),
                newProducts: defaultProducts.filter(p => p.is_new)
            });
        }
    },

    // 加载猜你喜欢数据
    async loadGuessProducts() {
        try {
            const res = await api.getProducts({ page_size: 8 });
            let products = (res.results || res || []).map(p => ({
                id: p.id,
                name: p.name,
                specification: p.specification,
                price: p.price,
                original_price: p.original_price,
                cover_image: p.cover_image || '/assets/products/fresh_milk.jpg',
                fresh_days: p.fresh_days || Math.floor(Math.random() * 10) + 5
            }));

            // 随机打乱数组顺序
            products = products.sort(() => Math.random() - 0.5);

            // 为某些项增加随机前缀，增强变化感
            const labels = ['热销', '推荐', '精选', '限时'];
            const changed = products.map(p => ({
                ...p,
                name: (Math.random() > 0.5 ? `[${labels[Math.floor(Math.random() * labels.length)]}] ` : '') + p.name.replace(/\[.*\]\s/, '')
            }));

            this.setData({ guessProducts: changed });
        } catch (err) {
            console.error('加载猜你喜欢失败:', err);
            // 使用本地图片的默认数据
            const guessProducts = [
                { id: 7, name: '特仑苏有机纯牛奶', specification: '250ml×10瓶', price: '78', original_price: '88', cover_image: '/assets/products/organic_milk.jpg', fresh_days: 6 },
                { id: 8, name: '德国进口有机奶', specification: '200ml×12包', price: '55', cover_image: '/assets/products/fresh_milk.jpg', fresh_days: 10 },
                { id: 9, name: '有机甄选限定上市', specification: '250ml×12盒', price: '66', original_price: '86', cover_image: '/assets/products/organic_milk.jpg', fresh_days: 8 },
                { id: 10, name: '有机营养家庭周货', specification: '250ml×24盒', price: '187', cover_image: '/assets/products/children_milk.jpg', fresh_days: 17 }
            ];
            const shuffled = guessProducts.sort(() => Math.random() - 0.5);
            const labels = ['热销', '推荐', '精选', '限时'];
            const changed = shuffled.map(p => ({
                ...p,
                name: (Math.random() > 0.5 ? `[${labels[Math.floor(Math.random() * labels.length)]}] ` : '') + p.name.replace(/\[.*\]\s/, '')
            }));
            this.setData({ guessProducts: changed });
        }
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

    // 跳转到轮播图对应商品
    goToBanner(e) {
        const id = e.currentTarget.dataset.id;
        wx.navigateTo({ url: `/pages/product/product?id=${id}` });
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
        if (filter === 'recommend') {
            // 模拟“换一批”效果
            this.loadGuessProducts();
            wx.showToast({ title: '已更新推荐', icon: 'none' });
            return;
        }
        wx.switchTab({ url: '/pages/category/category' });
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
    },

    // 加入购物车
    addToCart(e) {
        const product = e.currentTarget.dataset.product;
        let cart = wx.getStorageSync('cart') || [];

        const existingIndex = cart.findIndex(item => item.product.id === product.id);
        if (existingIndex > -1) {
            cart[existingIndex].quantity += 1;
        } else {
            cart.push({ product, quantity: 1, selected: true });
        }

        wx.setStorageSync('cart', cart);
        app.updateCartBadge();

        wx.showToast({ title: '已加入购物车', icon: 'success' });
    }
});
