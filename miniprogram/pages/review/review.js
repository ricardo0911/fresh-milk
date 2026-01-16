// pages/review/review.js - 订单评价逻辑
const { api } = require('../../utils/api');

Page({
    data: {
        orderId: null,
        order: null,
        reviews: [], // 每个商品的评价数据
        submitting: false
    },

    onLoad(options) {
        if (options.order_id) {
            this.setData({ orderId: options.order_id });
            this.loadOrderDetail();
        }
    },

    async loadOrderDetail() {
        wx.showLoading({ title: '加载中...' });
        try {
            // 模拟订单数据
            const mockOrder = {
                id: this.data.orderId,
                order_no: 'ORD202401100003',
                items: [
                    {
                        id: 1,
                        product_id: 4,
                        name: '每日鲜牛奶',
                        specification: '250ml×10瓶',
                        cover_image: 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&q=80',
                        quantity: 1
                    },
                    {
                        id: 2,
                        product_id: 5,
                        name: '草莓味酸奶',
                        specification: '100g×12杯',
                        cover_image: 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&q=80',
                        quantity: 1
                    }
                ]
            };

            // 初始化每个商品的评价数据
            const reviews = mockOrder.items.map(item => ({
                product_id: item.product_id,
                product_name: item.name,
                rating: 5,
                content: '',
                images: [],
                is_anonymous: false
            }));

            this.setData({
                order: mockOrder,
                reviews
            });
        } catch (err) {
            console.error('加载订单失败:', err);
            wx.showToast({ title: '加载失败', icon: 'none' });
        }
        wx.hideLoading();
    },

    // 设置评分
    setRating(e) {
        const { index, rating } = e.currentTarget.dataset;
        const reviews = this.data.reviews;
        reviews[index].rating = rating;
        this.setData({ reviews });
    },

    // 输入评价内容
    inputContent(e) {
        const index = e.currentTarget.dataset.index;
        const reviews = this.data.reviews;
        reviews[index].content = e.detail.value;
        this.setData({ reviews });
    },

    // 选择图片
    async chooseImage(e) {
        const index = e.currentTarget.dataset.index;
        const reviews = this.data.reviews;
        const currentImages = reviews[index].images || [];

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
            reviews[index].images = [...currentImages, ...newImages];
            this.setData({ reviews });
        } catch (err) {
            console.log('取消选择图片');
        }
    },

    // 删除图片
    deleteImage(e) {
        const { index, imgIndex } = e.currentTarget.dataset;
        const reviews = this.data.reviews;
        reviews[index].images.splice(imgIndex, 1);
        this.setData({ reviews });
    },

    // 预览图片
    previewImage(e) {
        const { index, imgIndex } = e.currentTarget.dataset;
        const images = this.data.reviews[index].images;
        wx.previewImage({
            current: images[imgIndex],
            urls: images
        });
    },

    // 切换匿名评价
    toggleAnonymous(e) {
        const index = e.currentTarget.dataset.index;
        const reviews = this.data.reviews;
        reviews[index].is_anonymous = !reviews[index].is_anonymous;
        this.setData({ reviews });
    },

    // 提交评价
    async submitReview() {
        const { reviews, orderId } = this.data;

        // 验证评价内容
        for (let i = 0; i < reviews.length; i++) {
            if (!reviews[i].content.trim()) {
                wx.showToast({ title: `请填写第${i + 1}个商品的评价`, icon: 'none' });
                return;
            }
        }

        this.setData({ submitting: true });
        wx.showLoading({ title: '提交中...' });

        try {
            // TODO: 调用真实API
            // await api.submitReview({ order_id: orderId, reviews });

            // 模拟提交
            await new Promise(resolve => setTimeout(resolve, 1000));

            wx.hideLoading();
            wx.showToast({ title: '评价成功', icon: 'success' });

            setTimeout(() => {
                wx.navigateBack();
            }, 1500);
        } catch (err) {
            wx.hideLoading();
            wx.showToast({ title: err.message || '提交失败', icon: 'none' });
        }
        this.setData({ submitting: false });
    },

    goBack() {
        wx.navigateBack();
    }
});
