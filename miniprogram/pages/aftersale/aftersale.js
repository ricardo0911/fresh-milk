// pages/aftersale/aftersale.js - 售后申请逻辑
const { api } = require('../../utils/api');

Page({
    data: {
        orderId: null,
        order: null,

        // 售后类型 (只保留退款相关)
        typeOptions: [
            { value: 'refund_only', label: '仅退款', icon: '💰', desc: '未收到货或不需要退货' },
            { value: 'return_refund', label: '退货退款', icon: '📦', desc: '已收到货，需要退回商品' }
        ],
        selectedType: '',

        // 退款原因 (与后端对应)
        reasonOptions: [
            { value: 'quality', label: '商品质量问题' },
            { value: 'not_on_time', label: '未按时送达' },
            { value: 'not_match', label: '商品与描述不符' },
            { value: 'no_need', label: '不想要了' },
            { value: 'other', label: '其他' }
        ],
        selectedReasonIndex: -1,

        // 详细说明
        description: '',



        // 退款金额
        refundAmount: '0.00',

        submitting: false
    },

    onLoad(options) {
        // 支持 order_no 和 order_id 两种参数
        const orderId = options.order_no || options.order_id;
        if (orderId) {
            this.setData({ orderId: orderId });
            this.loadOrderInfo();
        }
    },

    async loadOrderInfo() {
        wx.showLoading({ title: '加载中...' });
        try {
            const res = await api.getOrder(this.data.orderId);
            const order = {
                id: res.id,
                order_no: res.order_no,
                pay_amount: res.pay_amount || res.total_amount,
                items: (res.items || []).map(item => ({
                    id: item.id,
                    name: item.product_name || item.product?.name || item.name,
                    specification: item.specification || item.product?.specification,
                    price: item.price,
                    quantity: item.quantity,
                    cover_image: item.cover_image || item.product?.cover_image || '/assets/products/fresh_milk.jpg'
                }))
            };

            this.setData({
                order,
                refundAmount: order.pay_amount
            });
        } catch (err) {
            console.error('加载订单失败:', err);
            wx.showToast({ title: '加载订单失败', icon: 'none' });
        }
        wx.hideLoading();
    },

    // 选择售后类型
    selectType(e) {
        const type = e.currentTarget.dataset.type;
        this.setData({ selectedType: type });
    },

    // 选择原因
    selectReason(e) {
        this.setData({ selectedReasonIndex: e.detail.value });
    },

    // 输入描述
    inputDescription(e) {
        this.setData({ description: e.detail.value });
    },



    // 提交申请
    async submitApplication() {
        const { selectedType, selectedReasonIndex, description, order, refundAmount } = this.data;

        // 验证
        if (!selectedType) {
            wx.showToast({ title: '请选择售后类型', icon: 'none' });
            return;
        }
        if (selectedReasonIndex < 0) {
            wx.showToast({ title: '请选择退款原因', icon: 'none' });
            return;
        }

        this.setData({ submitting: true });
        wx.showLoading({ title: '提交中...' });

        try {
            // 调用退款API
            await api.createRefund({
                order_id: order.id,
                type: selectedType,
                reason: this.data.reasonOptions[selectedReasonIndex].value,
                description: description,
                amount: refundAmount
            });

            wx.hideLoading();
            wx.showModal({
                title: '提交成功',
                content: '您的退款申请已提交，我们将在1-3个工作日内处理',
                showCancel: false,
                success: () => {
                    wx.navigateBack();
                }
            });
        } catch (err) {
            wx.hideLoading();
            wx.showToast({ title: err.error || err.message || '提交失败', icon: 'none' });
        }
        this.setData({ submitting: false });
    }
});
