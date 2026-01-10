// pages/order/order.js - 订单确认页
const app = getApp();
const { createOrderAndPay, onPaymentSuccess, sandboxPay } = require('../../utils/payment');

Page({
    data: {
        orderItems: [],
        address: null,
        selectedCoupon: null,
        couponsCount: 2,
        remark: '',
        goodsAmount: '0.00',
        shipping: 0,
        discountAmount: 0,
        totalAmount: '0.00',
        isSubmitting: false
    },

    onLoad() {
        this.loadOrderItems();
        this.loadAddress();
    },

    onShow() {
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
        const discountAmount = this.data.selectedCoupon ? this.data.selectedCoupon.amount : 0;
        const totalAmount = Math.max(0, goodsAmount + shipping - discountAmount);

        this.setData({
            orderItems,
            goodsAmount: goodsAmount.toFixed(2),
            shipping,
            discountAmount,
            totalAmount: totalAmount.toFixed(2)
        });
    },

    loadAddress() {
        // 优先从storage获取默认地址
        const address = wx.getStorageSync('defaultAddress') || {
            name: '张三',
            phone: '138****8888',
            province: '北京市',
            city: '北京市',
            district: '朝阳区',
            address: '三里屯路XX号'
        };
        this.setData({ address });
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

        this.setData({ isSubmitting: true });

        try {
            // 构建订单数据
            const orderData = {
                items: this.data.orderItems.map(item => ({
                    product_id: item.product.id,
                    quantity: item.quantity,
                    price: item.product.price
                })),
                address: this.data.address,
                coupon_id: this.data.selectedCoupon?.id,
                remark: this.data.remark,
                goodsAmount: this.data.goodsAmount,
                shipping: this.data.shipping,
                discountAmount: this.data.discountAmount,
                totalAmount: this.data.totalAmount
            };

            // 发起支付
            const result = await createOrderAndPay(orderData);

            if (result.success) {
                // 支付成功处理
                onPaymentSuccess(result.orderId);

                wx.showToast({
                    title: '支付成功',
                    icon: 'success',
                    duration: 1500
                });

                // 跳转到支付成功页
                setTimeout(() => {
                    wx.redirectTo({
                        url: `/pages/order-result/order-result?orderId=${result.orderId}&status=success&amount=${this.data.totalAmount}`
                    });
                }, 1500);
            }
        } catch (error) {
            if (error.cancelled) {
                wx.showToast({ title: '已取消支付', icon: 'none' });
            } else {
                wx.showToast({ title: error.message || '支付失败', icon: 'none' });
            }
        } finally {
            this.setData({ isSubmitting: false });
        }
    },

    // 沙箱支付测试
    async testSandboxPay() {
        try {
            const result = await sandboxPay(this.data.totalAmount, true);
            if (result.success) {
                onPaymentSuccess(result.orderId);
                wx.showToast({ title: '沙箱支付成功', icon: 'success' });
                setTimeout(() => {
                    wx.redirectTo({
                        url: `/pages/order-result/order-result?orderId=${result.orderId}&status=success&amount=${this.data.totalAmount}`
                    });
                }, 1500);
            }
        } catch (error) {
            wx.showToast({ title: error.message, icon: 'none' });
        }
    }
});
