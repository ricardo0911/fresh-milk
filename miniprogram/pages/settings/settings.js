// pages/settings/settings.js
const app = getApp();

Page({
    data: {
        userInfo: null,
        cacheSize: '0 KB'
    },

    onLoad() {
        this.loadUserInfo();
        this.calculateCacheSize();
    },

    onShow() {
        this.loadUserInfo();
    },

    loadUserInfo() {
        const userInfo = app.globalData.userInfo || wx.getStorageSync('userInfo');
        this.setData({ userInfo });
    },

    calculateCacheSize() {
        try {
            const res = wx.getStorageInfoSync();
            const sizeKB = res.currentSize;
            let sizeStr = '';
            if (sizeKB >= 1024) {
                sizeStr = (sizeKB / 1024).toFixed(2) + ' MB';
            } else {
                sizeStr = sizeKB + ' KB';
            }
            this.setData({ cacheSize: sizeStr });
        } catch (e) {
            console.error('获取缓存大小失败:', e);
        }
    },

    // 意见反馈
    goToFeedback() {
        wx.navigateTo({ url: '/pages/feedback/feedback' });
    },

    // 联系客服
    callService() {
        wx.makePhoneCall({ phoneNumber: '400-888-8888' });
    },

    // 清除缓存
    clearCache() {
        wx.showModal({
            title: '提示',
            content: '确定要清除缓存吗？',
            success: (res) => {
                if (res.confirm) {
                    // 保留登录信息
                    const token = wx.getStorageSync('token');
                    const userInfo = wx.getStorageSync('userInfo');

                    wx.clearStorageSync();

                    // 恢复登录信息
                    if (token) wx.setStorageSync('token', token);
                    if (userInfo) wx.setStorageSync('userInfo', userInfo);

                    this.calculateCacheSize();
                    wx.showToast({ title: '清除成功', icon: 'success' });
                }
            }
        });
    },

    // 关于我们
    goToAbout() {
        wx.showModal({
            title: '关于鲜奶直达',
            content: '版本：1.0.0\n\n鲜奶直达致力于为您提供新鲜、优质的乳制品配送服务。',
            showCancel: false,
            confirmText: '知道了'
        });
    }
});
