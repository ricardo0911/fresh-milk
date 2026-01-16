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
            { id: 5, icon: '👶', name: '儿童奶' },
            { id: 6, icon: '🎁', name: '心意臻选' },   // 送礼场景
            { id: 7, icon: '💪', name: '元气早餐' },   // 早餐搭配
            { id: 8, icon: '🌙', name: '晚安时光' },   // 助眠/晚间
            { id: 9, icon: '👨‍👩‍👧', name: '阖家欢享' }    // 家庭装
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
        // 模拟数据 - 增加场景分类
        const mockProducts = [
            // 鲜牛奶
            { id: 1, name: '每日鲜牛奶', specification: '250ml×10瓶', price: '39.90', original_price: '49.90', cover_image: '/assets/products/fresh_milk.jpg', category: 1, is_hot: true, sales: 1520 },
            { id: 3, name: '低脂鲜牛奶', specification: '500ml×8瓶', price: '56.80', cover_image: '/assets/products/fresh_milk.jpg', category: 1, sales: 856 },

            // 酸奶
            { id: 5, name: '草莓酸奶', specification: '100g×12杯', price: '38.00', cover_image: '/assets/products/strawberry_yogurt.jpg', category: 2, is_new: true, sales: 620 },
            { id: 6, name: '希腊酸奶', specification: '400g×4盒', price: '59.00', cover_image: '/assets/products/strawberry_yogurt.jpg', category: 2, sales: 380 },

            // 奶酪
            { id: 7, name: '马苏里拉奶酪', specification: '200g×3袋', price: '48.00', cover_image: '/assets/products/organic_milk.jpg', category: 3, sales: 280 },

            // 有机奶
            { id: 2, name: '有机纯牛奶', specification: '1L×6盒', price: '89.00', original_price: '108.00', cover_image: '/assets/products/organic_milk.jpg', category: 4, is_hot: true, is_new: true, sales: 980 },

            // 儿童奶
            { id: 4, name: '儿童成长奶', specification: '200ml×12瓶', price: '68.00', cover_image: '/assets/products/children_milk.jpg', category: 5, is_new: true, sales: 720 },
            { id: 11, name: '宝贝DHA牛奶', specification: '190ml×15瓶', price: '88.00', cover_image: '/assets/products/children_milk.jpg', category: 5, sales: 560 },

            // 心意臻选 (送礼)
            { id: 12, name: '沙漠有机礼盒', specification: '250ml×12盒', price: '168.00', original_price: '198.00', cover_image: '/assets/products/organic_milk.jpg', category: 6, is_hot: true, sales: 890 },
            { id: 13, name: '臻享金装礼遇', specification: '1L×8盒', price: '238.00', cover_image: '/assets/products/organic_milk.jpg', category: 6, sales: 450 },
            { id: 14, name: '新春限定礼盒', specification: '250ml×20盒', price: '288.00', cover_image: '/assets/products/fresh_milk.jpg', category: 6, is_new: true, sales: 320 },

            // 元气早餐
            { id: 15, name: '早安蛋白奶', specification: '250ml×10瓶', price: '49.90', cover_image: '/assets/products/fresh_milk.jpg', category: 7, is_hot: true, sales: 1200 },
            { id: 16, name: '谷物燕麦奶', specification: '200ml×12盒', price: '58.00', cover_image: '/assets/products/organic_milk.jpg', category: 7, sales: 780 },

            // 晚安时光
            { id: 17, name: '舒眠热牛奶', specification: '200ml×10瓶', price: '45.00', cover_image: '/assets/products/fresh_milk.jpg', category: 8, sales: 650 },
            { id: 18, name: '晚安香蕉奶', specification: '200ml×8瓶', price: '42.00', cover_image: '/assets/products/strawberry_yogurt.jpg', category: 8, is_new: true, sales: 420 },

            // 阖家欢享 (家庭装)
            { id: 19, name: '家庭畅饮装', specification: '1L×12盒', price: '129.00', original_price: '158.00', cover_image: '/assets/products/fresh_milk.jpg', category: 9, is_hot: true, sales: 2100 },
            { id: 20, name: '全家营养套装', specification: '混合×24件', price: '199.00', cover_image: '/assets/products/organic_milk.jpg', category: 9, sales: 980 }
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
