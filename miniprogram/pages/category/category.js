// pages/category/category.js
const app = getApp();
const { api } = require('../../utils/api');

Page({
    data: {
        categories: [],
        currentCategory: 0,
        sortBy: 'default',
        products: [],
        allProducts: []
    },

    onLoad(options) {
        if (options.id) {
            this.setData({ currentCategory: parseInt(options.id) });
        }
        this.loadCategories();
        this.loadProducts();
    },

    onShow() {
        app.updateCartBadge();
    },

    async loadCategories() {
        try {
            const res = await api.getCategories();
            const apiCategories = (res.results || res || []).map(c => ({
                id: c.id,
                icon: c.icon || '🥛',
                name: c.name
            }));
            // 添加"全部"选项
            const categories = [{ id: 0, icon: '🥛', name: '全部' }, ...apiCategories];
            this.setData({ categories });
        } catch (err) {
            console.error('加载分类失败:', err);
            // 使用默认分类
            this.setData({
                categories: [
                    { id: 0, icon: '🥛', name: '全部' },
                    { id: 1, icon: '🥛', name: '鲜牛奶' },
                    { id: 2, icon: '🍶', name: '酸奶' },
                    { id: 3, icon: '🧀', name: '奶酪' },
                    { id: 4, icon: '🌿', name: '有机奶' },
                    { id: 5, icon: '👶', name: '儿童奶' }
                ]
            });
        }
    },

    async loadProducts() {
        wx.showLoading({ title: '加载中...' });
        try {
            const res = await api.getProducts({ page_size: 50 });
            const products = (res.results || res || []).map(p => ({
                id: p.id,
                name: p.name,
                specification: p.specification,
                price: p.price,
                original_price: p.original_price,
                cover_image: p.cover_image || '/assets/products/fresh_milk.jpg',
                category: p.category,
                is_hot: p.is_hot,
                is_new: p.is_new,
                sales: p.sales || 0
            }));
            this.setData({ allProducts: products });
            this.filterProducts();
        } catch (err) {
            console.error('加载产品失败:', err);
            // 使用默认数据
            const defaultProducts = [
                { id: 1, name: '每日鲜牛奶', specification: '250ml×10瓶', price: '39.90', original_price: '49.90', cover_image: '/assets/products/fresh_milk.jpg', category: 1, is_hot: true, sales: 1520 },
                { id: 2, name: '有机纯牛奶', specification: '1L×6盒', price: '89.00', original_price: '108.00', cover_image: '/assets/products/organic_milk.jpg', category: 4, is_hot: true, is_new: true, sales: 980 },
                { id: 3, name: '低脂鲜牛奶', specification: '500ml×8瓶', price: '56.80', cover_image: '/assets/products/fresh_milk.jpg', category: 1, sales: 856 },
                { id: 4, name: '儿童成长奶', specification: '200ml×12瓶', price: '68.00', cover_image: '/assets/products/children_milk.jpg', category: 5, is_new: true, sales: 720 },
                { id: 5, name: '草莓酸奶', specification: '100g×12杯', price: '38.00', cover_image: '/assets/products/strawberry_yogurt.jpg', category: 2, is_new: true, sales: 620 }
            ];
            this.setData({ allProducts: defaultProducts });
            this.filterProducts();
        }
        wx.hideLoading();
    },

    selectCategory(e) {
        const id = parseInt(e.currentTarget.dataset.id) || 0;
        this.setData({ currentCategory: id });
        this.filterProducts();
    },

    setSort(e) {
        const sort = e.currentTarget.dataset.sort;
        this.setData({ sortBy: sort });
        this.filterProducts();
    },

    filterProducts() {
        let products = [...this.data.allProducts];

        // 分类筛选
        if (this.data.currentCategory > 0) {
            products = products.filter(p => p.category === this.data.currentCategory);
        }

        // 排序
        if (this.data.sortBy === 'sales') {
            products.sort((a, b) => b.sales - a.sales);
        } else if (this.data.sortBy === 'price') {
            products.sort((a, b) => parseFloat(a.price) - parseFloat(b.price));
        }

        this.setData({ products });
    },

    goToProduct(e) {
        const id = e.currentTarget.dataset.id;
        wx.navigateTo({ url: `/pages/product/product?id=${id}` });
    },

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

        wx.showToast({ title: '已加入购物车', icon: 'success' });
    }
});
