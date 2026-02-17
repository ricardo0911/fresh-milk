const { api } = require('../../utils/api');

Page({
    data: {
        content: '',
        topics: [],
        topicList: [],
        selectedTopic: '',
        selectedTopicId: null
    },

    onLoad(options) {
        this.loadTopics();
    },

    async loadTopics() {
        try {
            const res = await api.getTopics();
            const topicList = res.results || res || [];
            this.setData({
                topicList,
                topics: topicList.map(t => t.name)
            });
        } catch (err) {
            console.error('加载话题失败:', err);
            // 使用默认话题
            this.setData({
                topics: ['日常', '新品', '活动', '建议']
            });
        }
    },

    onInput(e) {
        this.setData({
            content: e.detail.value
        });
    },



    selectTopic(e) {
        const topic = e.currentTarget.dataset.topic;
        const topicObj = this.data.topicList.find(t => t.name === topic);
        this.setData({
            selectedTopic: this.data.selectedTopic === topic ? '' : topic,
            selectedTopicId: this.data.selectedTopic === topic ? null : (topicObj ? topicObj.id : null)
        });
    },

    async submitPost() {
        if (!this.data.content.trim()) {
            wx.showToast({
                title: '请输入内容',
                icon: 'none'
            });
            return;
        }

        if (!this.data.selectedTopic) {
            wx.showToast({
                title: '请选择一个话题',
                icon: 'none'
            });
            return;
        }

        // 检查登录状态
        const token = wx.getStorageSync('token');
        if (!token) {
            wx.showToast({
                title: '请先登录',
                icon: 'none'
            });
            setTimeout(() => {
                wx.navigateTo({ url: '/pages/login/login' });
            }, 1500);
            return;
        }

        wx.showLoading({
            title: '发布中...',
        });

        try {
            const postData = {
                content: this.data.content,
                topic: this.data.selectedTopicId
            };

            await api.createPost(postData);

            wx.hideLoading();
            wx.showToast({
                title: '发布成功',
                icon: 'success'
            });

            // Navigate back after success
            setTimeout(() => {
                wx.navigateBack();
            }, 1500);
        } catch (err) {
            wx.hideLoading();
            console.error('发布失败:', err);
            wx.showToast({
                title: err.message || '发布失败',
                icon: 'none'
            });
        }
    }
});
