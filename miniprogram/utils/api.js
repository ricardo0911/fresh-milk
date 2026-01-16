/**
 * 鲜奶订购小程序 - API请求封装
 */

const BASE_URL = 'http://127.0.0.1:8000/api/v1';

// 请求封装
const request = (options) => {
    return new Promise((resolve, reject) => {
        const token = wx.getStorageSync('token');

        wx.request({
            url: BASE_URL + options.url,
            method: options.method || 'GET',
            data: options.data || {},
            header: {
                'Content-Type': 'application/json',
                ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
                ...(options.header || {})
            },
            success: (res) => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    resolve(res.data);
                } else if (res.statusCode === 401) {
                    // Token过期，清除登录状态
                    wx.removeStorageSync('token');
                    wx.removeStorageSync('userInfo');
                    reject({ message: '登录已过期，请重新登录', code: 401 });
                } else {
                    reject(res.data || { message: '请求失败' });
                }
            },
            fail: (err) => {
                reject({ message: '网络错误，请稍后重试', error: err });
            }
        });
    });
};

// API接口
const api = {
    // ========== 用户模块 ==========
    // 登录
    login: (data) => request({ url: '/users/login/', method: 'POST', data }),
    // 注册
    register: (data) => request({ url: '/users/register/', method: 'POST', data }),
    // 获取用户信息
    getUserInfo: () => request({ url: '/users/me/' }),
    // 更新用户信息
    updateUserInfo: (data) => request({ url: '/users/me/', method: 'PATCH', data }),

    // ========== 产品模块 ==========
    // 获取分类列表
    getCategories: () => request({ url: '/categories/' }),
    // 获取产品列表
    getProducts: (params = {}) => {
        const query = Object.entries(params).map(([k, v]) => `${k}=${v}`).join('&');
        return request({ url: `/products/${query ? '?' + query : ''}` });
    },
    // 获取产品详情
    getProduct: (id) => request({ url: `/products/${id}/` }),
    // 获取热门产品
    getHotProducts: () => request({ url: '/products/hot/' }),
    // 获取新品
    getNewProducts: () => request({ url: '/products/new_arrivals/' }),
    // 获取周期购产品
    getSubscriptionProducts: () => request({ url: '/products/subscription/' }),

    // ========== 订单模块 ==========
    // 创建订单
    createOrder: (data) => request({ url: '/orders/', method: 'POST', data }),
    // 获取订单列表
    getOrders: (status) => {
        const query = status ? `?status=${status}` : '';
        return request({ url: `/orders/${query}` });
    },
    // 获取订单详情
    getOrder: (id) => request({ url: `/orders/${id}/` }),
    // 取消订单
    cancelOrder: (id) => request({ url: `/orders/${id}/cancel/`, method: 'POST' }),
    // 确认收货
    confirmOrder: (id) => request({ url: `/orders/${id}/confirm/`, method: 'POST' }),

    // ========== 优惠券模块 ==========
    // 获取可领取优惠券
    getAvailableCoupons: () => request({ url: '/coupons/available/' }),
    // 获取我的优惠券
    getMyCoupons: () => request({ url: '/coupons/my/' }),
    // 领取优惠券
    claimCoupon: (id) => request({ url: `/coupons/${id}/claim/`, method: 'POST' }),

    // ========== 地址模块 ==========
    // 获取地址列表
    getAddresses: () => request({ url: '/addresses/' }),
    // 添加地址
    addAddress: (data) => request({ url: '/addresses/', method: 'POST', data }),
    // 更新地址
    updateAddress: (id, data) => request({ url: `/addresses/${id}/`, method: 'PUT', data }),
    // 删除地址
    deleteAddress: (id) => request({ url: `/addresses/${id}/`, method: 'DELETE' }),
    // 设为默认
    setDefaultAddress: (id) => request({ url: `/addresses/${id}/set_default/`, method: 'POST' }),

    // ========== 周期购模块 ==========
    // 创建周期购订阅
    createSubscription: (data) => request({ url: '/subscriptions/', method: 'POST', data }),
    // 获取我的订阅
    getSubscriptions: () => request({ url: '/subscriptions/' }),
    // 取消订阅
    cancelSubscription: (id) => request({ url: `/subscriptions/${id}/cancel/`, method: 'POST' }),
};

module.exports = { api, request, BASE_URL };
