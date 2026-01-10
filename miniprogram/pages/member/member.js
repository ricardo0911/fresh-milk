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
        // 模拟社区帖子数据
        const allPosts = [
            {
                id: 1,
                username: '兔兔草莓茶',
                avatar: 'https://i.pravatar.cc/100?img=1',
                image: '/assets/products/organic_milk.jpg',
                content: '在超市一眼就锁定了特仑苏牛奶，回家拆开发现后面还有以前学过的课文...',
                likes: 60
            },
            {
                id: 2,
                username: 'C.C.',
                avatar: 'https://i.pravatar.cc/100?img=2',
                image: '/assets/products/fresh_milk.jpg',
                content: '喝一瓶特仑苏有机纯牛奶「诗歌限定装」，开启元气满满的工作吧！',
                likes: 62
            },
            {
                id: 3,
                username: '芙蓉',
                avatar: 'https://i.pravatar.cc/100?img=3',
                image: '/assets/products/children_milk.jpg',
                content: '哇😍好漂亮的春日限定包装🥹好喜欢❤️爱了爱了🐱🌷',
                likes: 31
            },
            {
                id: 4,
                username: '路宝儿',
                avatar: 'https://i.pravatar.cc/100?img=4',
                image: '/assets/products/strawberry_yogurt.jpg',
                content: '新年新启，喜乐如常，福运满满！！！',
                likes: 43
            },
            {
                id: 5,
                username: '小明同学',
                avatar: 'https://i.pravatar.cc/100?img=5',
                image: '/assets/products/organic_milk.jpg',
                content: '每天一杯有机奶，健康生活从早开始～',
                likes: 28
            },
            {
                id: 6,
                username: '美食家',
                avatar: 'https://i.pravatar.cc/100?img=6',
                image: '/assets/products/fresh_milk.jpg',
                content: '用特仑苏做的拿铁，口感丝滑，太赞了！',
                likes: 55
            }
        ];

        // 分配到左右两列
        const leftPosts = allPosts.filter((_, i) => i % 2 === 0);
        const rightPosts = allPosts.filter((_, i) => i % 2 === 1);

        this.setData({ leftPosts, rightPosts });
    },

    switchTab(e) {
        const index = e.currentTarget.dataset.index;
        this.setData({ currentTab: index });
    },

    setFilter(e) {
        const filter = e.currentTarget.dataset.filter;
        this.setData({ contentFilter: filter });
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
        wx.showToast({ title: '帖子详情开发中', icon: 'none' });
    },

    publishPost() {
        wx.showToast({ title: '发布功能开发中', icon: 'none' });
    }
});
