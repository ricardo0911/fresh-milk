// pages/my-reviews/my-reviews.js
const { api } = require('../../utils/api');

Page({
    data: {
        reviews: [],
        loading: true,
        isEmpty: false
    },

    onLoad() {
        this.loadReviews();
    },

    onShow() {
        this.loadReviews();
    },

    onPullDownRefresh() {
        this.loadReviews().then(() => {
            wx.stopPullDownRefresh();
        });
    },

    // 加载我的评价
    loadReviews() {
        this.setData({ loading: true });
        return api.getMyComments().then(res => {
            const reviews = res.results || res || [];
            // 格式化数据
            const formattedReviews = reviews.map(item => ({
                ...item,
                created_date: this.formatDate(item.created_at),
                replied_date: item.replied_at ? this.formatDate(item.replied_at) : '',
                rating_text: this.getRatingText(item.rating)
            }));
            this.setData({
                reviews: formattedReviews,
                loading: false,
                isEmpty: formattedReviews.length === 0
            });
        }).catch(err => {
            console.error('加载评价失败:', err);
            this.setData({ loading: false, isEmpty: true });
            wx.showToast({ title: '加载失败', icon: 'none' });
        });
    },

    // 获取评分文本
    getRatingText(rating) {
        const texts = ['', '非常不满意', '不满意', '一般', '满意', '非常满意'];
        return texts[rating] || '';
    },

    // 格式化日期
    formatDate(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr.replace(/-/g, '/'));
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        return `${year}-${month}-${day}`;
    },

    // 预览图片
    previewImage(e) {
        const { urls, current } = e.currentTarget.dataset;
        wx.previewImage({
            current: current,
            urls: urls
        });
    },

    // 跳转到商品详情
    goToProduct(e) {
        const id = e.currentTarget.dataset.id;
        wx.navigateTo({
            url: `/pages/product/product?id=${id}`
        });
    }
});
