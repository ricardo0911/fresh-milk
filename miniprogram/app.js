// app.js - 小程序入口
App({
    globalData: {
        userInfo: null,
        token: null,
        baseUrl: 'http://localhost:8000/api/v1',
        cartCount: 0
    },

    onLaunch() {
        // 检查登录状态
        const token = wx.getStorageSync('token');
        if (token) {
            this.globalData.token = token;
            this.getUserInfo();
        }

        // 更新购物车数量
        this.updateCartBadge();
    },

    // 获取用户信息
    getUserInfo() {
        const that = this;
        wx.request({
            url: `${this.globalData.baseUrl}/users/me/`,
            header: {
                'Authorization': `Bearer ${this.globalData.token}`
            },
            success(res) {
                if (res.statusCode === 200) {
                    that.globalData.userInfo = res.data;
                }
            }
        });
    },

    // 更新购物车徽标
    updateCartBadge() {
        const cart = wx.getStorageSync('cart') || [];
        const count = cart.reduce((sum, item) => sum + item.quantity, 0);
        this.globalData.cartCount = count;

        if (count > 0) {
            wx.setTabBarBadge({
                index: 2,
                text: count > 99 ? '99+' : String(count)
            });
        } else {
            wx.removeTabBarBadge({ index: 2 });
        }
    },

    // 请求封装
    request(options) {
        const that = this;
        return new Promise((resolve, reject) => {
            wx.request({
                url: `${this.globalData.baseUrl}${options.url}`,
                method: options.method || 'GET',
                data: options.data,
                header: {
                    'Content-Type': 'application/json',
                    'Authorization': this.globalData.token ? `Bearer ${this.globalData.token}` : '',
                    ...options.header
                },
                success(res) {
                    if (res.statusCode === 401) {
                        // Token过期
                        that.globalData.token = null;
                        wx.removeStorageSync('token');
                        wx.navigateTo({ url: '/pages/login/login' });
                        reject(new Error('请重新登录'));
                    } else if (res.statusCode >= 200 && res.statusCode < 300) {
                        resolve(res.data);
                    } else {
                        reject(new Error(res.data.detail || '请求失败'));
                    }
                },
                fail(err) {
                    reject(err);
                }
            });
        });
    }
});
