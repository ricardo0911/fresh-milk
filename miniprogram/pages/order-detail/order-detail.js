// pages/order-detail/order-detail.js - 订单详情逻辑
const { api } = require('../../utils/api');

Page({
    data: {
        orderId: null,
        order: null,
        deliveryPerson: null,
        progressSteps: []
    },

    onLoad(options) {
        if (options.id) {
            this.setData({ orderId: options.id });
            this.loadOrderDetail();
        }
    },

    onShow() {
        if (this.data.orderId) {
            this.loadOrderDetail();
        }
    },

    async loadOrderDetail() {
        wx.showLoading({ title: '加载中...' });
        try {
            // 模拟订单详情数据
            const mockOrder = {
                id: this.data.orderId,
                order_no: 'FM202401150001',
                status: 'shipped',
                status_display: '配送中',

                // 商品信息
                items: [
                    {
                        id: 1,
                        product_id: 1,
                        name: '每日鲜牛奶',
                        specification: '250ml×10瓶',
                        price: '39.90',
                        quantity: 2,
                        total_price: '79.80',
                        cover_image: 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&q=80'
                    },
                    {
                        id: 2,
                        product_id: 2,
                        name: '有机纯牛奶',
                        specification: '1L×6盒',
                        price: '49.90',
                        quantity: 1,
                        total_price: '49.90',
                        cover_image: 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80'
                    }
                ],

                // 价格信息
                total_amount: '129.70',
                delivery_fee: '0.00',
                discount_amount: '10.00',
                pay_amount: '119.70',

                // 收货信息
                receiver_name: '张三',
                receiver_phone: '138****8888',
                receiver_address: '浙江省杭州市西湖区文三路999号',

                // 周期购信息（如果是周期购订单）
                is_subscription: true,
                subscription_no: 'SUB202401001',
                subscription_frequency: '每周一次',
                subscription_periods: 12,
                current_period: 3,

                // 时间
                created_at: '2024-01-15 10:30:00',
                paid_at: '2024-01-15 10:32:15',
                shipped_at: '2024-01-15 14:00:00',
                expected_delivery: '2024-01-16 08:00-10:00',

                // 备注
                remark: '请放到门口，谢谢',

                // 是否已评价
                is_reviewed: false
            };

            // 配送员信息
            const mockDeliveryPerson = {
                id: 1,
                name: '张师傅',
                phone: '13800138000',
                avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&q=80',
                rating: 4.9,
                total_deliveries: 1256
            };

            // 生成进度步骤
            const progressSteps = this.generateProgressSteps(mockOrder);

            this.setData({
                order: mockOrder,
                deliveryPerson: mockDeliveryPerson,
                progressSteps
            });
        } catch (err) {
            console.error('加载订单详情失败:', err);
            wx.showToast({ title: '加载失败', icon: 'none' });
        }
        wx.hideLoading();
    },

    generateProgressSteps(order) {
        const steps = [
            {
                title: '订单提交',
                time: order.created_at,
                icon: '📝',
                completed: true
            }
        ];

        if (order.paid_at) {
            steps.push({
                title: '支付成功',
                time: order.paid_at,
                icon: '💳',
                completed: true
            });
        }

        if (order.shipped_at) {
            steps.push({
                title: '商家发货',
                time: order.shipped_at,
                icon: '📦',
                completed: true,
                current: order.status === 'shipped'
            });
        }

        if (order.status === 'shipped') {
            steps.push({
                title: '等待收货',
                time: `预计 ${order.expected_delivery}`,
                icon: '🚚',
                completed: false,
                pending: true
            });
        }

        if (order.delivered_at || order.status === 'delivered') {
            steps.push({
                title: '已送达',
                time: order.delivered_at || '',
                icon: '✅',
                completed: true,
                current: order.status === 'delivered'
            });
        }

        if (order.completed_at || order.status === 'completed') {
            steps.push({
                title: '订单完成',
                time: order.completed_at || '',
                icon: '🎉',
                completed: true
            });
        }

        return steps;
    },

    // 拨打配送员电话
    callDelivery() {
        const phone = this.data.deliveryPerson?.phone;
        if (phone) {
            wx.makePhoneCall({ phoneNumber: phone });
        }
    },

    // 复制订单号
    copyOrderNo() {
        const orderNo = this.data.order?.order_no;
        if (orderNo) {
            wx.setClipboardData({
                data: orderNo,
                success: () => {
                    wx.showToast({ title: '已复制', icon: 'success' });
                }
            });
        }
    },

    // 取消订单
    cancelOrder() {
        wx.showModal({
            title: '取消订单',
            content: '确定要取消这个订单吗？',
            success: async (res) => {
                if (res.confirm) {
                    wx.showLoading({ title: '处理中...' });
                    try {
                        // TODO: 调用API取消订单
                        await new Promise(resolve => setTimeout(resolve, 500));
                        wx.hideLoading();
                        wx.showToast({ title: '已取消', icon: 'success' });
                        setTimeout(() => wx.navigateBack(), 1500);
                    } catch (err) {
                        wx.hideLoading();
                        wx.showToast({ title: '取消失败', icon: 'none' });
                    }
                }
            }
        });
    },

    // 确认收货
    confirmReceive() {
        wx.showModal({
            title: '确认收货',
            content: '确认已收到商品吗？',
            success: async (res) => {
                if (res.confirm) {
                    wx.showLoading({ title: '处理中...' });
                    try {
                        // TODO: 调用API确认收货
                        await new Promise(resolve => setTimeout(resolve, 500));
                        wx.hideLoading();
                        wx.showToast({ title: '已确认收货', icon: 'success' });
                        this.loadOrderDetail();
                    } catch (err) {
                        wx.hideLoading();
                        wx.showToast({ title: '操作失败', icon: 'none' });
                    }
                }
            }
        });
    },

    // 申请售后
    applyAfterSale() {
        wx.navigateTo({
            url: `/pages/aftersale/aftersale?order_id=${this.data.orderId}`
        });
    },

    // 去评价
    goToReview() {
        wx.navigateTo({
            url: `/pages/review/review?order_id=${this.data.orderId}`
        });
    },

    // 再次购买
    buyAgain() {
        const order = this.data.order;
        let cart = wx.getStorageSync('cart') || [];

        order.items.forEach(item => {
            const existingIndex = cart.findIndex(c => c.product?.id === item.product_id);
            if (existingIndex > -1) {
                cart[existingIndex].quantity += item.quantity;
            } else {
                cart.push({
                    product: {
                        id: item.product_id,
                        name: item.name,
                        specification: item.specification,
                        price: item.price,
                        cover_image: item.cover_image
                    },
                    quantity: item.quantity
                });
            }
        });

        wx.setStorageSync('cart', cart);
        wx.showToast({ title: '已加入购物车', icon: 'success' });
    },

    // 查看周期购详情
    viewSubscription() {
        const subNo = this.data.order?.subscription_no;
        if (subNo) {
            wx.navigateTo({
                url: `/pages/subscription-detail/subscription-detail?id=${subNo}`
            });
        }
    }
});
