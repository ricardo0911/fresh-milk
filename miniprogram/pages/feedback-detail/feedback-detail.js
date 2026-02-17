// pages/feedback-detail/feedback-detail.js
const { api } = require('../../utils/api');

Page({
    data: {
        id: null,
        feedback: null,
        loading: true
    },

    onLoad(options) {
        if (options.id) {
            this.setData({ id: options.id });
            this.loadFeedback(options.id);
        }
    },

    onPullDownRefresh() {
        if (this.data.id) {
            this.loadFeedback(this.data.id).then(() => {
                wx.stopPullDownRefresh();
            });
        }
    },

    // 加载反馈详情
    loadFeedback(id) {
        this.setData({ loading: true });
        return api.getFeedbackDetail(id).then(res => {
            const feedback = {
                ...res,
                type_text: this.getTypeText(res.feedback_type),
                status_text: this.getStatusText(res.status),
                status_desc: this.getStatusDesc(res.status),
                created_date: this.formatDate(res.created_at),
                replied_date: res.replied_at ? this.formatDate(res.replied_at) : ''
            };
            this.setData({ feedback, loading: false });
        }).catch(err => {
            console.error('加载反馈详情失败:', err);
            this.setData({ loading: false });
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

    // 获取状态描述
    getStatusDesc(status) {
        const descMap = {
            'pending': '您的反馈已收到，我们会尽快处理',
            'processing': '客服正在处理您的反馈',
            'resolved': '客服已回复，请查看回复内容',
            'closed': '该反馈已关闭'
        };
        return descMap[status] || '';
    },

    // 格式化日期
    formatDate(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr.replace(/-/g, '/'));
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        const hour = date.getHours().toString().padStart(2, '0');
        const minute = date.getMinutes().toString().padStart(2, '0');
        return `${year}-${month}-${day} ${hour}:${minute}`;
    }
});
