// pages/order/order.js - 订单确认页
const app = getApp();
const { api } = require('../../utils/api');
const { createOrder, onPaymentSuccess } = require('../../utils/payment');

Page({
    data: {
        orderItems: [],
        address: null,
        selectedCoupon: null,
        couponsCount: 0,
        remark: '',
        goodsAmount: '0.00',
        shipping: 0,
        discountAmount: 0,
        totalAmount: '0.00',
        isSubmitting: false,
        // 支付弹窗相关
        showPayModal: false,
        currentOrderId: '',
        userBalance: '128.50'
    },

    onLoad() {
        this.loadOrderItems();
        this.loadAddress();
        this.loadUserBalance();
        this.loadCouponsCount();
    },

    onShow() {
        // 从优惠券选择页面返回时更新优惠券
        const selectedCoupon = wx.getStorageSync('selectedCoupon');
        if (selectedCoupon) {
            this.setData({ selectedCoupon });
            wx.removeStorageSync('selectedCoupon'); // 清除，避免下次进入时自动选中
            this.loadOrderItems(); // 重新计算价格
        }

        // 从地址选择页面返回时更新地址
        const selectedAddress = this.data.selectedAddress;
        if (selectedAddress) {
            this.setData({ address: selectedAddress, selectedAddress: null });
        }
    },

    loadOrderItems() {
        const cart = wx.getStorageSync('cart') || [];
        const orderItems = cart.filter(item => item.selected !== false);

        const goodsAmount = orderItems.reduce((sum, item) =>
            sum + parseFloat(item.product.price) * item.quantity, 0);
        const shipping = goodsAmount >= 88 ? 0 : 8;

        // 计算会员折扣（需要检查会员是否过期）
        const userInfo = app.globalData.userInfo;
        const rates = {
            'regular': 1.0,
            'silver': 0.95,
            'gold': 0.90,
            'platinum': 0.85,
        };

        // 检查会员是否有效
        let isMemberValid = false;
        if (userInfo && userInfo.member_level !== 'regular' && userInfo.member_expire_at) {
            const expireAt = new Date(userInfo.member_expire_at);
            isMemberValid = expireAt > new Date();
        }

        // 只有会员有效时才应用折扣
        const rate = (userInfo && isMemberValid) ? (rates[userInfo.member_level] || 1.0) : 1.0;
        const memberDiscount = goodsAmount * (1 - rate);

        const couponDiscount = this.data.selectedCoupon ? (parseFloat(this.data.selectedCoupon.amount) || 0) : 0;
        const discountAmount = memberDiscount + couponDiscount;
        const totalAmount = Math.max(0, goodsAmount + shipping - discountAmount);

        this.setData({
            orderItems,
            goodsAmount: goodsAmount.toFixed(2),
            shipping,
            memberDiscount: memberDiscount.toFixed(2),
            couponDiscount: couponDiscount.toFixed(2),
            discountAmount: discountAmount.toFixed(2),
            totalAmount: totalAmount.toFixed(2)
        });
    },

    loadAddress() {
        // 优先从storage获取默认地址
        const address = wx.getStorageSync('defaultAddress') || {
            receiver_name: '张三',
            receiver_phone: '138****8888',
            province: '北京市',
            city: '北京市',
            district: '朝阳区',
            detail: '三里屯路XX号'
        };
        this.setData({ address });
    },

    loadUserBalance() {
        // 模拟获取用户余额
        const userInfo = app.globalData.userInfo;
        if (userInfo && userInfo.balance) {
            this.setData({ userBalance: userInfo.balance });
        }
    },

    async loadCouponsCount() {
        try {
            const res = await api.getMyCoupons('unused');
            const data = res.data?.results || res.results || res.data || res || [];
            const count = Array.isArray(data) ? data.length : 0;
            this.setData({ couponsCount: count });
        } catch (err) {
            console.error('获取优惠券数量失败:', err);
        }
    },

    selectAddress() {
        wx.navigateTo({ url: '/pages/address/address?select=1' });
    },

    selectCoupon() {
        wx.navigateTo({ url: '/pages/coupon/coupon?select=1' });
    },

    onRemarkInput(e) {
        this.setData({ remark: e.detail.value });
    },

    async submitOrder() {
        // 防止重复提交
        if (this.data.isSubmitting) return;

        // 验证
        if (!this.data.address) {
            wx.showToast({ title: '请选择收货地址', icon: 'none' });
            return;
        }

        if (this.data.orderItems.length === 0) {
            wx.showToast({ title: '购物车为空', icon: 'none' });
            return;
        }

        // 过滤掉无效的商品（没有product.id的）
        const validItems = this.data.orderItems.filter(item => item.product && item.product.id);
        if (validItems.length === 0) {
            wx.showToast({ title: '购物车商品数据异常，请重新添加', icon: 'none' });
            return;
        }

        if (validItems.length !== this.data.orderItems.length) {
            wx.showToast({ title: '部分商品数据异常已过滤', icon: 'none' });
        }

        this.setData({ isSubmitting: true });

        try {
            // 构建订单数据
            const orderData = {
                items: validItems.map(item => ({
                    product_id: item.product.id,
                    quantity: item.quantity,
                    price: item.product.price,
                    name: item.product.name,
                    cover_image: item.product.cover_image,
                    specification: item.product.specification
                })),
                address: this.data.address,
                coupon_id: this.data.selectedCoupon?.id,
                remark: this.data.remark,
                goodsAmount: this.data.goodsAmount,
                shipping: this.data.shipping,
                discountAmount: this.data.discountAmount,
                totalAmount: this.data.totalAmount
            };

            // 创建订单
            const orderId = await createOrder(orderData);

            // 显示支付弹窗
            this.setData({
                currentOrderId: orderId,
                showPayModal: true,
                isSubmitting: false
            });

        } catch (error) {
            wx.showToast({ title: error.message || '创建订单失败', icon: 'none' });
            this.setData({ isSubmitting: false });
        }
    },

    // 支付成功回调
    async onPaySuccess(e) {
        const { orderId, amount } = e.detail;

        // 调用后端支付接口更新订单状态
        await onPaymentSuccess(orderId);

        // 关闭支付弹窗
        this.setData({ showPayModal: false });

        // 跳转到支付成功页
        wx.redirectTo({
            url: `/pages/order-result/order-result?orderId=${orderId}&status=success&amount=${amount}`
        });
    },

    // 支付弹窗关闭
    onPayClose() {
        this.setData({ showPayModal: false });
        wx.showToast({ title: '已取消支付', icon: 'none' });
    }
});
