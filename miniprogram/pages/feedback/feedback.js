// pages/feedback/feedback.js
const app = getApp();
const { api } = require('../../utils/api');

Page({
    data: {
        feedbackType: '',
        content: '',
        contact: ''
    },

    onLoad() {
        // 预填手机号
        const userInfo = app.globalData.userInfo || wx.getStorageSync('userInfo');
        if (userInfo && userInfo.phone) {
            this.setData({ contact: userInfo.phone });
        }
    },

    // 选择反馈类型
    selectType(e) {
        const type = e.currentTarget.dataset.type;
        this.setData({ feedbackType: type });
    },

    // 输入反馈内容
    onContentInput(e) {
        this.setData({ content: e.detail.value });
    },

    // 输入联系方式
    onContactInput(e) {
        this.setData({ contact: e.detail.value });
    },

    // 提交反馈
    submitFeedback() {
        const { feedbackType, content, contact } = this.data;

        // 验证
        if (!feedbackType) {
            wx.showToast({ title: '请选择反馈类型', icon: 'none' });
            return;
        }

        if (!content.trim()) {
            wx.showToast({ title: '请输入反馈内容', icon: 'none' });
            return;
        }

        if (content.trim().length < 10) {
            wx.showToast({ title: '反馈内容至少10个字', icon: 'none' });
            return;
        }

        // 验证手机号格式（如果填写了）
        if (contact && !/^1[3-9]\d{9}$/.test(contact)) {
            wx.showToast({ title: '请输入正确的手机号', icon: 'none' });
            return;
        }

        // 映射反馈类型到后端格式
        const typeMap = {
            'product': 'quality',
            'delivery': 'delivery',
            'service': 'complaint',
            'suggestion': 'suggestion',
            'other': 'other'
        };

        wx.showLoading({ title: '提交中...' });

        api.submitFeedback({
            feedback_type: typeMap[feedbackType] || 'other',
            title: content.trim().substring(0, 20),
            content: content.trim(),
            contact: contact
        }).then(() => {
            wx.hideLoading();
            wx.showModal({
                title: '提交成功',
                content: '感谢您的反馈，我们会认真处理！',
                showCancel: false,
                success: () => {
                    // 返回反馈列表页
                    const pages = getCurrentPages();
                    if (pages.length > 1) {
                        wx.navigateBack();
                    } else {
                        wx.redirectTo({ url: '/pages/feedback-list/feedback-list' });
                    }
                }
            });
        }).catch(err => {
            wx.hideLoading();
            wx.showToast({ title: err.message || '提交失败', icon: 'none' });
        });
    }
});
