// pages/member/member.js - 会员社区
const app = getApp();

Page({
    data: {
        currentTab: 0,
        tabs: ['推荐', '生日礼', '新鲜日期', '大家都在晒'],
        contentFilter: 'all',
        topics: [
            { id: 1, name: '冬季营养 暖心直达', image: '/assets/products/organic_milk.jpg' },
            { id: 2, name: '花样萌友 更好相聚', image: '/assets/products/fresh_milk.jpg' },
            { id: 3, name: '定格更好瞬间 共赴巅峰赛场', image: '/assets/products/children_milk.jpg' },
            { id: 4, name: '有机生活 健康每天', image: '/assets/products/strawberry_yogurt.jpg' }
        ],
        leftPosts: [],
        rightPosts: []
    },

    onLoad() {
        this.loadPosts();
    },

    loadPosts() {
        const { currentTab } = this.data;
        let allPosts = [];

        if (currentTab === 0) { // 推荐
            allPosts = [
                { id: 1, username: '兔兔草莓茶', avatar: 'https://i.pravatar.cc/100?img=1', image: '/assets/products/organic_milk.jpg', content: '推荐这款有机奶，味道很纯正！', likes: 60 },
                { id: 2, username: 'C.C.', avatar: 'https://i.pravatar.cc/100?img=2', image: '/assets/products/fresh_milk.jpg', content: '每天早餐必备，新鲜直达。', likes: 62 }
            ];
        } else if (currentTab === 1) { // 生日礼
            allPosts = [
                { id: 11, username: '生日小星', avatar: 'https://i.pravatar.cc/100?img=11', image: '/assets/products/strawberry_yogurt.jpg', content: '今天生日收到了鲜奶礼盒，太开心了！🎁', likes: 120 },
                { id: 12, username: '甜甜', avatar: 'https://i.pravatar.cc/100?img=12', image: '/assets/products/children_milk.jpg', content: '生日礼券换的牛奶，好喝！', likes: 88 }
            ];
        } else if (currentTab === 2) { // 新鲜日期
            allPosts = [
                { id: 21, username: '品质控', avatar: 'https://i.pravatar.cc/100?img=21', image: '/assets/products/fresh_milk.jpg', content: '日期真的非常新鲜，都是当天的。', likes: 45 },
                { id: 22, username: '王阿姨', avatar: 'https://i.pravatar.cc/100?img=22', image: '/assets/products/organic_milk.jpg', content: '看这日期，给孩子喝着放心。', likes: 56 }
            ];
        } else { // 大家都在晒
            allPosts = [
                { id: 31, username: '晒图达人', avatar: 'https://i.pravatar.cc/100?img=31', image: '/assets/products/children_milk.jpg', content: '打卡今日份的健康生活！📷', likes: 200 },
                { id: 32, username: '生活家', avatar: 'https://i.pravatar.cc/100?img=32', image: '/assets/products/strawberry_yogurt.jpg', content: '颜值很高的包装，忍不住晒一下。', likes: 150 }
            ];
        }

        // 分配到左右两列
        const leftPosts = allPosts.filter((_, i) => i % 2 === 0);
        const rightPosts = allPosts.filter((_, i) => i % 2 === 1);

        this.setData({ leftPosts, rightPosts });
    },

    switchTab(e) {
        const index = e.currentTarget.dataset.index;
        this.setData({ currentTab: index });
        // 模拟切换内容
        wx.showLoading({ title: '加载中' });
        setTimeout(() => {
            this.loadPosts();
            wx.hideLoading();
        }, 500);
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
        wx.showToast({ title: '发布功能开发中', icon: 'none' });
    }
});
