// pages/order-detail/order-detail.js - 订单详情逻辑
const { api } = require('../../utils/api');
const payment = require('../../utils/payment');

// 快递公司名称映射
const expressCompanyMap = {
    'SF': '顺丰速运',
    'YTO': '圆通速递',
    'ZTO': '中通快递',
    'YD': '韵达快递',
    'JTSD': '极兔速递'
};

Page({
    data: {
        orderNo: null,
        order: null,
        deliveryPerson: null,
        progressSteps: [],
        expressCompanyName: '',
        latestTrace: null,
        expressTraces: []
    },

    onLoad(options) {
        console.log('order-detail onLoad options:', options);
        // 支持 order_no 和 id 两种参数（兼容旧版本）
        const orderNo = options.order_no || options.id;
        if (orderNo) {
            this.setData({ orderNo: orderNo });
            this.loadOrderDetail();
        } else {
            wx.showToast({ title: '订单参数错误', icon: 'none' });
            setTimeout(() => wx.navigateBack(), 1500);
        }
    },

    onShow() {
        if (this.data.orderNo) {
            this.loadOrderDetail();
        }
    },

    async loadOrderDetail() {
        wx.showLoading({ title: '加载中...' });
        try {
            console.log('Loading order detail for:', this.data.orderNo);
            const res = await api.getOrder(this.data.orderNo);
            console.log('Order detail response:', res);
            const order = res;

            if (order) {
                // 格式化订单数据
                const fullOrder = {
                    id: order.id,
                    order_no: order.order_no,
                    status: order.status,
                    status_display: order.status_display || this.getStatusDisplay(order.status),
                    total_amount: order.total_amount,
                    delivery_fee: order.delivery_fee || '0.00',
                    discount_amount: order.discount_amount || '0.00',
                    pay_amount: order.pay_amount || order.total_amount,
                    receiver_name: order.receiver_name || order.address?.name,
                    receiver_phone: order.receiver_phone || order.address?.phone,
                    receiver_address: order.receiver_address || order.address?.full_address,
                    created_at: order.created_at,
                    paid_at: order.paid_at,
                    shipped_at: order.shipped_at,
                    delivered_at: order.delivered_at,
                    completed_at: order.completed_at,
                    expected_delivery: order.expected_delivery,
                    is_reviewed: order.is_reviewed,
                    // 快递信息
                    express_company: order.express_company,
                    express_no: order.express_no,
                    express_status: order.express_status,
                    items: (order.items || []).map(item => ({
                        id: item.id,
                        product_id: item.product_id || item.product?.id,
                        name: item.product_name || item.product?.name || item.name,
                        specification: item.specification || item.product?.specification,
                        price: item.price,
                        quantity: item.quantity,
                        total_price: (parseFloat(item.price) * item.quantity).toFixed(2),
                        cover_image: item.cover_image || item.product?.cover_image || '/assets/products/fresh_milk.jpg'
                    }))
                };

                // 配送员信息（如果有）
                const deliveryPerson = order.delivery_person ? {
                    id: order.delivery_person.id,
                    name: order.delivery_person.name,
                    phone: order.delivery_person.phone,
                    avatar: order.delivery_person.avatar || '/assets/default_avatar.png',
                    rating: order.delivery_person.rating,
                    total_deliveries: order.delivery_person.total_deliveries
                } : null;

                const progressSteps = this.generateProgressSteps(fullOrder);

                // 快递公司名称
                const expressCompanyName = expressCompanyMap[order.express_company] || order.express_company || '';

                this.setData({
                    order: fullOrder,
                    deliveryPerson,
                    progressSteps,
                    expressCompanyName
                });

                // 如果有快递单号，加载物流轨迹
                if (order.express_no) {
                    this.loadExpressTrace();
                }
            } else {
                wx.showToast({ title: '未找到订单', icon: 'error' });
                setTimeout(() => wx.navigateBack(), 1500);
            }
            wx.hideLoading();
        } catch (err) {
            wx.hideLoading();
            console.error('加载订单详情失败:', err);
            wx.showToast({ title: '加载失败', icon: 'none' });
        }
    },

    // 加载物流轨迹
    async loadExpressTrace() {
        try {
            const res = await api.getExpressTrace(this.data.orderNo);
            if (res && res.traces && res.traces.length > 0) {
                this.setData({
                    expressTraces: res.traces,
                    latestTrace: res.traces[0]
                });
            }
        } catch (err) {
            console.error('加载物流轨迹失败:', err);
        }
    },

    getStatusDisplay(status) {
        const statusMap = {
            'pending': '待付款',
            'paid': '待发货',
            'shipped': '配送中',
            'delivered': '待收货',
            'completed': '已完成',
            'cancelled': '已取消'
        };
        return statusMap[status] || status;
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

    // 复制快递单号
    copyExpressNo() {
        const expressNo = this.data.order?.express_no;
        if (expressNo) {
            wx.setClipboardData({
                data: expressNo,
                success: () => {
                    wx.showToast({ title: '已复制', icon: 'success' });
                }
            });
        }
    },

    // 查看物流轨迹
    viewExpressTrace() {
        wx.navigateTo({
            url: `/pages/express-trace/express-trace?order_no=${this.data.orderNo}`
        });
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
                        await api.cancelOrder(this.data.orderNo);
                        wx.hideLoading();
                        wx.showToast({ title: '已取消', icon: 'success' });
                        setTimeout(() => wx.navigateBack(), 1500);
                    } catch (err) {
                        wx.hideLoading();
                        wx.showToast({ title: err.message || '取消失败', icon: 'none' });
                    }
                }
            }
        });
    },

    // 支付订单
    payOrder() {
        const order = this.data.order;
        if (!order) return;

        wx.showModal({
            title: '确认支付',
            content: `支付金额：¥${order.pay_amount}`,
            confirmText: '确认支付',
            cancelText: '取消',
            success: async (res) => {
                if (res.confirm) {
                    wx.showLoading({ title: '支付中...' });
                    try {
                        // 调用后端支付接口更新订单状态
                        await api.payOrder(this.data.orderNo);
                        wx.hideLoading();

                        // 跳转到支付成功页面
                        wx.redirectTo({
                            url: `/pages/order-result/order-result?order_no=${order.order_no}&amount=${order.pay_amount}&success=true`
                        });
                    } catch (err) {
                        wx.hideLoading();
                        console.error('支付失败:', err);
                        wx.showToast({ title: err.message || '支付失败', icon: 'none' });
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
                        const result = await api.confirmOrder(this.data.orderNo);
                        wx.hideLoading();
                        // 显示获得的积分
                        const points = result.points_earned || 0;
                        if (points > 0) {
                            wx.showToast({ title: `收货成功，+${points}积分`, icon: 'success', duration: 2000 });
                        } else {
                            wx.showToast({ title: '已确认收货', icon: 'success' });
                        }
                        this.loadOrderDetail();
                    } catch (err) {
                        wx.hideLoading();
                        wx.showToast({ title: err.message || '操作失败', icon: 'none' });
                    }
                }
            }
        });
    },

    // 申请售后
    applyAfterSale() {
        wx.navigateTo({
            url: `/pages/aftersale/aftersale?order_no=${this.data.orderNo}`
        });
    },

    // 去评价
    goToReview() {
        wx.navigateTo({
            url: `/pages/review/review?order_no=${this.data.orderNo}`
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
