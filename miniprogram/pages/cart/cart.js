// pages/cart/cart.js
const app = getApp();

Page({
    data: {
        cartItems: [],
        allSelected: true,
        selectedCount: 0,
        totalAmount: '0.00',
        guessProducts: []
    },

    onShow() {
        this.loadCart();
        this.loadGuessProducts();
    },

    loadCart() {
        let cart = wx.getStorageSync('cart') || [];
        // 过滤掉无效的商品（没有product或product.id的）
        cart = cart.filter(item => item.product && item.product.id);
        // 添加selected属性
        cart = cart.map(item => ({ ...item, selected: item.selected !== false }));
        // 保存清理后的购物车
        wx.setStorageSync('cart', cart);
        this.setData({ cartItems: cart });
        this.updateSummary();
    },

    updateSummary() {
        const { cartItems } = this.data;
        const selectedItems = cartItems.filter(item => item.selected);
        const selectedCount = selectedItems.reduce((sum, item) => sum + item.quantity, 0);
        const totalAmount = selectedItems.reduce((sum, item) => sum + parseFloat(item.product.price) * item.quantity, 0);
        const allSelected = cartItems.length > 0 && cartItems.every(item => item.selected);

        this.setData({
            selectedCount,
            totalAmount: totalAmount.toFixed(2),
            allSelected
        });

        app.updateCartBadge();
    },

    toggleSelect(e) {
        const index = e.currentTarget.dataset.index;
        const key = `cartItems[${index}].selected`;
        this.setData({ [key]: !this.data.cartItems[index].selected });
        this.saveCart();
        this.updateSummary();
    },

    toggleSelectAll() {
        const newSelected = !this.data.allSelected;
        const cartItems = this.data.cartItems.map(item => ({ ...item, selected: newSelected }));
        this.setData({ cartItems, allSelected: newSelected });
        this.saveCart();
        this.updateSummary();
    },

    increaseQty(e) {
        const index = e.currentTarget.dataset.index;
        const key = `cartItems[${index}].quantity`;
        this.setData({ [key]: this.data.cartItems[index].quantity + 1 });
        this.saveCart();
        this.updateSummary();
    },

    decreaseQty(e) {
        const index = e.currentTarget.dataset.index;
        if (this.data.cartItems[index].quantity > 1) {
            const key = `cartItems[${index}].quantity`;
            this.setData({ [key]: this.data.cartItems[index].quantity - 1 });
            this.saveCart();
            this.updateSummary();
        }
    },

    removeItem(e) {
        const index = e.currentTarget.dataset.index;
        wx.showModal({
            title: '提示',
            content: '确定要删除该商品吗？',
            success: (res) => {
                if (res.confirm) {
                    const cartItems = this.data.cartItems.filter((_, i) => i !== index);
                    this.setData({ cartItems });
                    this.saveCart();
                    this.updateSummary();
                    wx.showToast({ title: '已删除', icon: 'success' });
                }
            }
        });
    },

    saveCart() {
        wx.setStorageSync('cart', this.data.cartItems);
    },

    goToProduct(e) {
        const id = e.currentTarget.dataset.id;
        wx.navigateTo({ url: `/pages/product/product?id=${id}` });
    },

    goShopping() {
        wx.switchTab({ url: '/pages/index/index' });
    },

    checkout() {
        if (this.data.selectedCount === 0) return;

        // 检查登录状态
        const token = wx.getStorageSync('token');
        if (!token) {
            wx.showToast({ title: '请先登录', icon: 'none' });
            setTimeout(() => {
                wx.navigateTo({ url: '/pages/login/login' });
            }, 1500);
            return;
        }

        wx.navigateTo({ url: '/pages/order/order' });
    },

    loadGuessProducts() {
        const guessProducts = [
            { id: 7, name: '特仑苏有机纯牛奶', specification: '250ml×10瓶', price: '78', cover_image: '/assets/products/organic_milk.jpg', fresh_days: 6 },
            { id: 8, name: '德国进口有机奶', specification: '200ml×12包', price: '55', cover_image: '/assets/products/fresh_milk.jpg', fresh_days: 10 },
            { id: 9, name: '有机甄选限定上市', specification: '250ml×12盒', price: '66', cover_image: '/assets/products/organic_milk.jpg', fresh_days: 8 },
            { id: 10, name: '有机营养家庭周货', specification: '250ml×24盒', price: '187', cover_image: '/assets/products/children_milk.jpg', fresh_days: 17 }
        ];
        this.setData({ guessProducts });
    },

    goToProducts(e) {
        const filter = e.currentTarget.dataset.filter;
        if (filter === 'recommend') {
            this.refreshGuessProducts();
            wx.showToast({ title: '已更新推荐', icon: 'none' });
            return;
        }
        wx.switchTab({ url: '/pages/index/index' });
    },

    refreshGuessProducts() {
        const allProducts = [
            { id: 7, name: '特仑苏有机纯牛奶', specification: '250ml×10瓶', price: '78', cover_image: '/assets/products/organic_milk.jpg', fresh_days: 6 },
            { id: 8, name: '德国进口有机奶', specification: '200ml×12包', price: '55', cover_image: '/assets/products/fresh_milk.jpg', fresh_days: 10 },
            { id: 9, name: '有机甄选限定上市', specification: '250ml×12盒', price: '66', cover_image: '/assets/products/organic_milk.jpg', fresh_days: 8 },
            { id: 10, name: '有机营养家庭周货', specification: '250ml×24盒', price: '187', cover_image: '/assets/products/children_milk.jpg', fresh_days: 17 },
            { id: 11, name: '低脂鲜牛奶', specification: '500ml×8瓶', price: '56.80', cover_image: '/assets/products/fresh_milk.jpg', fresh_days: 7 },
            { id: 12, name: '儿童成长奶', specification: '200ml×12瓶', price: '68', cover_image: '/assets/products/children_milk.jpg', fresh_days: 15 }
        ];
        const shuffled = allProducts.sort(() => Math.random() - 0.5).slice(0, 4);
        this.setData({ guessProducts: shuffled });
    },

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
        this.loadCart();
        wx.showToast({ title: '已加入购物车', icon: 'success' });
    }
});
