// pages/review/review.js - 订单评价逻辑
const { api } = require('../../utils/api');

Page({
    data: {
        orderId: null,      // 订单号（用于API查询）
        orderDbId: null,    // 订单数据库ID（用于提交评论）
        order: null,
        reviews: [], // 每个商品的评价数据
        submitting: false
    },

    onLoad(options) {
        // 支持 order_id 和 order_no 两种参数
        const orderId = options.order_id || options.order_no;
        if (orderId) {
            this.setData({ orderId: orderId });
            this.loadOrderDetail();
        }
    },

    async loadOrderDetail() {
        wx.showLoading({ title: '加载中...' });
        try {
            const res = await api.getOrder(this.data.orderId);
            console.log('Order detail response:', JSON.stringify(res));

            const order = {
                id: res.id,
                order_no: res.order_no,
                items: (res.items || []).map(item => ({
                    id: item.id,
                    product_id: item.product,  // 这是产品的数据库ID
                    name: item.product_name || item.name,
                    specification: item.specification,
                    cover_image: item.cover_image || item.product_image || '/assets/products/fresh_milk.jpg',
                    quantity: item.quantity
                }))
            };

            // 初始化每个商品的评价数据
            const reviews = order.items.map(item => ({
                product_id: item.product_id,
                product_name: item.name,
                rating: 5,
                content: '',
                images: [],         // 本地临时路径
                uploadedImages: [], // 上传后的URL
                is_anonymous: false
            }));

            this.setData({
                order,
                orderDbId: res.id,  // 保存订单的数据库ID
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
                sourceType: ['album', 'camera'],
                sizeType: ['compressed']
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
        // 同时删除已上传的URL（如果有）
        if (reviews[index].uploadedImages && reviews[index].uploadedImages[imgIndex]) {
            reviews[index].uploadedImages.splice(imgIndex, 1);
        }
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

    // 上传单张图片
    async uploadSingleImage(filePath) {
        try {
            const res = await api.uploadImage(filePath, 'comment');
            return res.url;
        } catch (err) {
            console.error('上传图片失败:', err);
            throw err;
        }
    },

    // 提交评价
    async submitReview() {
        const { reviews, orderDbId } = this.data;

        // 验证
        if (!orderDbId) {
            wx.showToast({ title: '订单信息错误', icon: 'none' });
            return;
        }

        // 验证评价内容
        for (let i = 0; i < reviews.length; i++) {
            if (!reviews[i].content.trim()) {
                wx.showToast({ title: `请填写第${i + 1}个商品的评价`, icon: 'none' });
                return;
            }
            if (!reviews[i].product_id) {
                wx.showToast({ title: `商品信息错误`, icon: 'none' });
                return;
            }
        }

        this.setData({ submitting: true });
        wx.showLoading({ title: '提交中...' });

        try {
            // 先上传所有图片
            for (let i = 0; i < reviews.length; i++) {
                const review = reviews[i];
                if (review.images && review.images.length > 0) {
                    wx.showLoading({ title: `上传图片 ${i + 1}/${reviews.length}...` });
                    const uploadedUrls = [];
                    for (const imgPath of review.images) {
                        try {
                            const url = await this.uploadSingleImage(imgPath);
                            uploadedUrls.push(url);
                        } catch (err) {
                            console.error('图片上传失败:', err);
                            // 继续上传其他图片
                        }
                    }
                    review.uploadedImages = uploadedUrls;
                }
            }

            wx.showLoading({ title: '提交评价...' });

            // 为每个商品创建评论
            for (let i = 0; i < reviews.length; i++) {
                const review = reviews[i];
                const commentData = {
                    order: orderDbId,
                    product: review.product_id,
                    rating: review.rating,
                    content: review.content,
                    images: review.uploadedImages || [],
                    is_anonymous: review.is_anonymous || false
                };
                console.log('Submitting comment:', JSON.stringify(commentData));
                await api.createComment(commentData);
            }

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
