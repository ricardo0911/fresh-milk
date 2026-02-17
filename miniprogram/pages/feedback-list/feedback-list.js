// pages/feedback-list/feedback-list.js
const { api } = require('../../utils/api');

Page({
    data: {
        feedbacks: [],
        loading: true,
        isEmpty: false
    },

    onLoad() {
        this.loadFeedbacks();
    },

    onShow() {
        this.loadFeedbacks();
    },

    onPullDownRefresh() {
        this.loadFeedbacks().then(() => {
            wx.stopPullDownRefresh();
        });
    },

    // 加载反馈列表
    loadFeedbacks() {
        this.setData({ loading: true });
        return api.getMyFeedbacks().then(res => {
            const feedbacks = res.results || res || [];
            // 格式化数据
            const formattedFeedbacks = feedbacks.map(item => ({
                ...item,
                type_text: this.getTypeText(item.feedback_type),
                status_text: this.getStatusText(item.status),
                status_class: item.status,
                created_date: this.formatDate(item.created_at),
                replied_date: item.replied_at ? this.formatDate(item.replied_at) : ''
            }));
            this.setData({
                feedbacks: formattedFeedbacks,
                loading: false,
                isEmpty: formattedFeedbacks.length === 0
            });
        }).catch(err => {
            console.error('加载反馈失败:', err);
            this.setData({ loading: false, isEmpty: true });
            wx.showToast({ title: '加载失败', icon: 'none' });
        });
    },

    // 获取类型文本
    getTypeText(type) {
        const typeMap = {
            'suggestion': '功能建议',
            'complaint': '投诉反馈',
            'quality': '商品问题',
            'delivery': '配送问题',
            'other': '其他'
        };
        return typeMap[type] || '其他';
    },

    // 获取状态文本
    getStatusText(status) {
        const statusMap = {
            'pending': '待处理',
            'processing': '处理中',
            'resolved': '已回复',
            'closed': '已关闭'
        };
        return statusMap[status] || '待处理';
    },

    // 格式化日期
    formatDate(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr.replace(/-/g, '/'));
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        const hour = date.getHours().toString().padStart(2, '0');
        const minute = date.getMinutes().toString().padStart(2, '0');
        return `${month}-${day} ${hour}:${minute}`;
    },

    // 查看详情
    viewDetail(e) {
        const id = e.currentTarget.dataset.id;
        const feedback = this.data.feedbacks.find(f => f.id === id);
        if (feedback) {
            wx.navigateTo({
                url: `/pages/feedback-detail/feedback-detail?id=${id}`
            });
        }
    },

    // 新建反馈
    goToFeedback() {
        wx.navigateTo({
            url: '/pages/feedback/feedback'
        });
    }
});
