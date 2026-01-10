// pages/category/category.js
const app = getApp();

Page({
    data: {
        categories: [
            { id: 0, icon: '🥛', name: '全部' },
            { id: 1, icon: '🥛', name: '鲜牛奶' },
            { id: 2, icon: '🍶', name: '酸奶' },
            { id: 3, icon: '🧀', name: '奶酪' },
            { id: 4, icon: '🌿', name: '有机奶' },
            { id: 5, icon: '👶', name: '儿童奶' }
        ],
        currentCategory: 0,
        sortBy: 'default',
        products: [],
        allProducts: []
    },

    onLoad(options) {
        if (options.id) {
            this.setData({ currentCategory: parseInt(options.id) });
        }
        this.loadProducts();
    },

    onShow() {
        app.updateCartBadge();
    },

    loadProducts() {
        // 模拟数据
        const mockProducts = [
            { id: 1, name: '每日鲜牛奶', specification: '250ml×10瓶', price: '39.90', original_price: '49.90', cover_image: 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&q=80', category: 1, is_hot: true, sales: 1520 },
            { id: 2, name: '有机纯牛奶', specification: '1L×6盒', price: '89.00', original_price: '108.00', cover_image: 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80', category: 4, is_hot: true, is_new: true, sales: 980 },
            { id: 3, name: '低脂鲜牛奶', specification: '500ml×8瓶', price: '56.80', cover_image: 'https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=400&q=80', category: 1, sales: 856 },
            { id: 4, name: '儿童成长奶', specification: '200ml×12瓶', price: '68.00', cover_image: 'https://images.unsplash.com/photo-1572443490709-e57652c96a1b?w=400&q=80', category: 5, is_new: true, sales: 720 },
            { id: 5, name: '草莓酸奶', specification: '100g×12杯', price: '38.00', cover_image: 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&q=80', category: 2, is_new: true, sales: 620 },
            { id: 6, name: '希腊酸奶', specification: '400g×4盒', price: '59.00', cover_image: 'https://images.unsplash.com/photo-1571212515416-fef01fc43637?w=400&q=80', category: 2, sales: 380 },
            { id: 7, name: '马苏里拉奶酪', specification: '200g×3袋', price: '48.00', cover_image: 'https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=400&q=80', category: 3, sales: 280 }
        ];

        this.setData({ allProducts: mockProducts });
        this.filterProducts();
    },

    selectCategory(e) {
        const id = e.currentTarget.dataset.id;
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
