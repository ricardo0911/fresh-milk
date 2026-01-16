// pages/aftersale/aftersale.js - 售后申请逻辑
const { api } = require('../../utils/api');

Page({
    data: {
        orderId: null,
        order: null,

        // 售后类型
        typeOptions: [
            { value: 'refund', label: '仅退款', icon: '💰', desc: '未收到货或不需要退货' },
            { value: 'return', label: '退货退款', icon: '📦', desc: '已收到货，需要退回商品' },
            { value: 'exchange', label: '换货', icon: '🔄', desc: '收到商品有问题，需要换货' },
            { value: 'repair', label: '补发', icon: '🚚', desc: '商品缺少或损坏，需补发' }
        ],
        selectedType: '',

        // 退款原因
        reasonOptions: [
            '商品质量问题',
            '商品与描述不符',
            '未按约定时间送达',
            '商品破损/变质',
            '发错商品',
            '其他原因'
        ],
        selectedReasonIndex: -1,

        // 详细说明
        description: '',

        // 上传凭证
        images: [],

        // 退款金额
        refundAmount: '0.00',

        submitting: false
    },

    onLoad(options) {
        if (options.order_id) {
            this.setData({ orderId: options.order_id });
            this.loadOrderInfo();
        }
    },

    async loadOrderInfo() {
        wx.showLoading({ title: '加载中...' });
        try {
            // 模拟订单数据
            const mockOrder = {
                id: this.data.orderId,
                order_no: 'FM202401150001',
                pay_amount: '119.70',
                items: [
                    {
                        id: 1,
                        name: '每日鲜牛奶',
                        specification: '250ml×10瓶',
                        price: '39.90',
                        quantity: 2,
                        cover_image: 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&q=80'
                    }
                ]
            };

            this.setData({
                order: mockOrder,
                refundAmount: mockOrder.pay_amount
            });
        } catch (err) {
            console.error('加载订单失败:', err);
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

    // 选择图片
    async chooseImage() {
        const currentImages = this.data.images;
        if (currentImages.length >= 9) {
            wx.showToast({ title: '最多上传9张图片', icon: 'none' });
            return;
        }

        try {
            const res = await wx.chooseMedia({
                count: 9 - currentImages.length,
                mediaType: ['image'],
                sourceType: ['album', 'camera']
            });

            const newImages = res.tempFiles.map(f => f.tempFilePath);
            this.setData({ images: [...currentImages, ...newImages] });
        } catch (err) {
            console.log('取消选择图片');
        }
    },

    // 删除图片
    deleteImage(e) {
        const index = e.currentTarget.dataset.index;
        const images = this.data.images;
        images.splice(index, 1);
        this.setData({ images });
    },

    // 预览图片
    previewImage(e) {
        const index = e.currentTarget.dataset.index;
        wx.previewImage({
            current: this.data.images[index],
            urls: this.data.images
        });
    },

    // 提交申请
    async submitApplication() {
        const { selectedType, selectedReasonIndex, description, images, orderId } = this.data;

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
            // TODO: 调用真实API
            // await api.createAfterSale({
            //     order_id: orderId,
            //     type: selectedType,
            //     reason: this.data.reasonOptions[selectedReasonIndex],
            //     description,
            //     images
            // });

            // 模拟提交
            await new Promise(resolve => setTimeout(resolve, 1000));

            wx.hideLoading();
            wx.showModal({
                title: '提交成功',
                content: '您的售后申请已提交，我们将在1-3个工作日内处理',
                showCancel: false,
                success: () => {
                    wx.navigateBack();
                }
            });
        } catch (err) {
            wx.hideLoading();
            wx.showToast({ title: err.message || '提交失败', icon: 'none' });
        }
        this.setData({ submitting: false });
    }
});
