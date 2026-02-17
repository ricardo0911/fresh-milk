// pages/member/member.js - 会员社区
const app = getApp();
const { api } = require('../../utils/api');

Page({
    data: {
        currentTab: 0,
        tabs: ['推荐', '生日礼', '新鲜日期', '大家都在晒'],
        contentFilter: 'all',
        topics: [],
        leftPosts: [],
        rightPosts: []
    },

    onLoad() {
        this.loadTopics();
        this.loadPosts();
    },

    async loadTopics() {
        try {
            const res = await api.getTopics();
            const topics = (res.results || res || []).map(t => ({
                id: t.id,
                name: t.name,
                image: t.image || '/assets/products/organic_milk.jpg'
            }));
            if (topics.length > 0) {
                this.setData({ topics });
            } else {
                // 默认话题
                this.setData({
                    topics: [
                        { id: 1, name: '冬季营养 暖心直达', image: '/assets/products/organic_milk.jpg' },
                        { id: 2, name: '花样萌友 更好相聚', image: '/assets/products/fresh_milk.jpg' },
                        { id: 3, name: '定格更好瞬间 共赴巅峰赛场', image: '/assets/products/children_milk.jpg' },
                        { id: 4, name: '有机生活 健康每天', image: '/assets/products/strawberry_yogurt.jpg' }
                    ]
                });
            }
        } catch (err) {
            console.error('加载话题失败:', err);
            this.setData({
                topics: [
                    { id: 1, name: '冬季营养 暖心直达', image: '/assets/products/organic_milk.jpg' },
                    { id: 2, name: '花样萌友 更好相聚', image: '/assets/products/fresh_milk.jpg' },
                    { id: 3, name: '定格更好瞬间 共赴巅峰赛场', image: '/assets/products/children_milk.jpg' },
                    { id: 4, name: '有机生活 健康每天', image: '/assets/products/strawberry_yogurt.jpg' }
                ]
            });
        }
    },

    async loadPosts() {
        const { currentTab, tabs } = this.data;
        const tabName = tabs[currentTab];

        wx.showLoading({ title: '加载中' });
        try {
            const res = await api.getPosts({ tab: tabName, page_size: 10 });
            let allPosts = (res.results || res || []).map(p => ({
                id: p.id,
                username: p.user?.nickname || p.username || '用户',
                avatar: p.user?.avatar || '/assets/default_avatar.png',
                image: p.image || '/assets/products/organic_milk.jpg',
                content: p.content,
                likes: p.likes || 0
            }));

            // 如果 API 没有返回数据，使用默认数据
            if (allPosts.length === 0) {
                allPosts = this.getDefaultPosts(currentTab);
            }

            // 分配到左右两列
            const leftPosts = allPosts.filter((_, i) => i % 2 === 0);
            const rightPosts = allPosts.filter((_, i) => i % 2 === 1);

            this.setData({ leftPosts, rightPosts });
        } catch (err) {
            console.error('加载帖子失败:', err);
            // 使用默认数据
            const allPosts = this.getDefaultPosts(currentTab);
            const leftPosts = allPosts.filter((_, i) => i % 2 === 0);
            const rightPosts = allPosts.filter((_, i) => i % 2 === 1);
            this.setData({ leftPosts, rightPosts });
        }
        wx.hideLoading();
    },

    getDefaultPosts(tabIndex) {
        const defaultData = {
            0: [ // 推荐
                { id: 1, username: '兔兔草莓茶', avatar: '/assets/default_avatar.png', image: '/assets/products/organic_milk.jpg', content: '推荐这款有机奶，味道很纯正！', likes: 60 },
                { id: 2, username: 'C.C.', avatar: '/assets/default_avatar.png', image: '/assets/products/fresh_milk.jpg', content: '每天早餐必备，新鲜直达。', likes: 62 }
            ],
            1: [ // 生日礼
                { id: 11, username: '生日小星', avatar: '/assets/default_avatar.png', image: '/assets/products/strawberry_yogurt.jpg', content: '今天生日收到了鲜奶礼盒，太开心了！', likes: 120 },
                { id: 12, username: '甜甜', avatar: '/assets/default_avatar.png', image: '/assets/products/children_milk.jpg', content: '生日礼券换的牛奶，好喝！', likes: 88 }
            ],
            2: [ // 新鲜日期
                { id: 21, username: '品质控', avatar: '/assets/default_avatar.png', image: '/assets/products/fresh_milk.jpg', content: '日期真的非常新鲜，都是当天的。', likes: 45 },
                { id: 22, username: '王阿姨', avatar: '/assets/default_avatar.png', image: '/assets/products/organic_milk.jpg', content: '看这日期，给孩子喝着放心。', likes: 56 }
            ],
            3: [ // 大家都在晒
                { id: 31, username: '晒图达人', avatar: '/assets/default_avatar.png', image: '/assets/products/children_milk.jpg', content: '打卡今日份的健康生活！', likes: 200 },
                { id: 32, username: '生活家', avatar: '/assets/default_avatar.png', image: '/assets/products/strawberry_yogurt.jpg', content: '颜值很高的包装，忍不住晒一下。', likes: 150 }
            ]
        };
        return defaultData[tabIndex] || defaultData[0];
    },

    switchTab(e) {
        const index = e.currentTarget.dataset.index;
        this.setData({ currentTab: index });
        this.loadPosts();
    },

    setFilter(e) {
        const filter = e.currentTarget.dataset.filter;
        this.setData({ contentFilter: filter });
        this.loadPosts();
    },

    viewPromoDetails() {
        wx.showModal({
            title: '活动提示',
            content: '会员日活动详情正在加载中，请稍后再试',
            showCancel: false
        });
    },

    viewAllTopics() {
        wx.showToast({ title: '全部话题', icon: 'none' });
    },

    viewTopic(e) {
        const id = e.currentTarget.dataset.id;
        wx.showToast({ title: '话题详情开发中', icon: 'none' });
    },

    viewPost(e) {
        const id = e.currentTarget.dataset.id;
        wx.showToast({ title: '内容详情开发中', icon: 'none' });
    },

    publishPost() {
        wx.navigateTo({
            url: '/pages/publish/publish'
        });
    }
});
