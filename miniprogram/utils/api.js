/**
 * 鲜奶订购小程序 - API请求封装
 */

const BASE_URL = 'http://127.0.0.1:8000/api/v1';

// 请求封装
const request = (options) => {
    return new Promise((resolve, reject) => {
        const token = wx.getStorageSync('token');

        const headers = {
            'Content-Type': 'application/json',
            ...(options.header || {})
        };

        // 只有当 token 是有效的 JWT token 时才添加 Authorization header
        if (token && token.startsWith('eyJ')) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        console.log('API Request:', options.method || 'GET', BASE_URL + options.url);
        console.log('Request Data:', JSON.stringify(options.data));

        wx.request({
            url: BASE_URL + options.url,
            method: options.method || 'GET',
            data: options.data || {},
            header: headers,
            success: (res) => {
                console.log('API Response:', res.statusCode, JSON.stringify(res.data));
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
                console.error('API Error:', err);
                reject({ message: '网络错误，请稍后重试', error: err });
            }
        });
    });
};

// API接口
const api = {
    // ========== 用户模块 ==========
    // 登录
    login: (data) => request({ url: '/auth/login/', method: 'POST', data }),
    // 微信登录
    wxLogin: (data) => request({ url: '/auth/wx-login/', method: 'POST', data }),
    // 注册
    register: (data) => request({ url: '/auth/register/', method: 'POST', data }),
    // 获取用户信息
    getUserInfo: () => request({ url: '/users/me/' }),
    // 更新用户信息
    updateUserInfo: (data) => request({ url: '/users/me/', method: 'PATCH', data }),
    // 发送重置密码验证码
    sendResetCode: (data) => request({ url: '/auth/send-reset-code/', method: 'POST', data }),
    // 验证重置密码验证码
    verifyResetCode: (data) => request({ url: '/auth/verify-reset-code/', method: 'POST', data }),
    // 重置密码
    resetPassword: (data) => request({ url: '/auth/reset-password/', method: 'POST', data }),

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

    // ========== 收藏模块 ==========
    // 获取我的收藏
    getFavorites: () => request({ url: '/favorites/' }),
    // 切换收藏状态
    toggleFavorite: (data) => request({ url: '/favorites/toggle/', method: 'POST', data }),

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
    // 支付订单
    payOrder: (id) => request({ url: `/orders/${id}/pay/`, method: 'POST' }),
    // 确认收货
    confirmOrder: (id) => request({ url: `/orders/${id}/confirm_receive/`, method: 'POST' }),

    // ========== 物流模块 ==========
    // 查询物流轨迹（用户端）
    getExpressTrace: (orderId) => request({ url: `/express/orders/by-order/${orderId}/` }),

    // ========== 优惠券模块 ==========
    // 获取可领取优惠券
    getAvailableCoupons: () => request({ url: '/coupons/available/' }),
    // 获取可积分兑换的优惠券
    getExchangeableCoupons: () => request({ url: '/coupons/exchangeable/' }),
    // 获取我的优惠券
    getMyCoupons: (status) => request({ url: `/user-coupons/${status ? '?status=' + status : ''}` }),
    // 领取优惠券
    claimCoupon: (couponId) => request({ url: '/user-coupons/receive/', method: 'POST', data: { coupon_id: couponId } }),
    // 积分兑换优惠券
    exchangeCoupon: (couponId) => request({ url: '/user-coupons/exchange/', method: 'POST', data: { coupon_id: couponId } }),
    // 获取可用优惠券(下单时)
    getUsableCoupons: (amount) => request({ url: '/user-coupons/usable/', data: { amount } }),

    // ========== 积分模块 ==========
    // 获取用户统计数据（积分、优惠券数量）
    getUserStats: () => request({ url: '/users/stats/' }),
    // 获取积分记录
    getPointsRecords: () => request({ url: '/users/points_records/' }),

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
    // 获取订阅详情
    getSubscription: (id) => request({ url: `/subscriptions/${id}/` }),
    // 取消订阅
    cancelSubscription: (id) => request({ url: `/subscriptions/${id}/cancel/`, method: 'POST' }),
    // 暂停订阅
    pauseSubscription: (id) => request({ url: `/subscriptions/${id}/pause/`, method: 'POST' }),

    // ========== 社区模块 ==========
    // 获取话题列表
    getTopics: () => request({ url: '/topics/' }),
    // 获取帖子列表
    getPosts: (params = {}) => {
        const query = Object.entries(params).map(([k, v]) => `${k}=${v}`).join('&');
        return request({ url: `/posts/${query ? '?' + query : ''}` });
    },
    // 创建帖子
    createPost: (data) => request({ url: '/posts/', method: 'POST', data }),

    // ========== 评价模块 ==========
    // 创建评论
    createComment: (data) => request({ url: '/comments/', method: 'POST', data }),
    // 获取评论列表
    getComments: (params = {}) => {
        const query = Object.entries(params).map(([k, v]) => `${k}=${v}`).join('&');
        return request({ url: `/comments/${query ? '?' + query : ''}` });
    },
    // 获取产品评价
    getProductReviews: (productId) => request({ url: `/comments/?product=${productId}` }),
    // 获取我的评价
    getMyComments: () => request({ url: '/comments/my/' }),
    // 点赞评论
    likeComment: (id) => request({ url: `/comments/${id}/like/`, method: 'POST' }),

    // ========== 售后模块 ==========
    // 创建售后申请（旧接口，保留兼容）
    createAfterSale: (data) => request({ url: '/aftersales/', method: 'POST', data }),
    // 获取售后列表（旧接口）
    getAfterSales: () => request({ url: '/aftersales/' }),
    // 获取售后详情（旧接口）
    getAfterSale: (id) => request({ url: `/aftersales/${id}/` }),

    // ========== 退款模块 ==========
    // 获取退款申请列表
    getRefunds: () => request({ url: '/refunds/' }),
    // 获取退款申请详情
    getRefund: (id) => request({ url: `/refunds/${id}/` }),
    // 创建退款申请
    createRefund: (data) => request({ url: '/refunds/', method: 'POST', data }),
    // 取消退款申请
    cancelRefund: (id) => request({ url: `/refunds/${id}/cancel/`, method: 'POST' }),
    // 填写退货快递信息
    fillReturnExpress: (id, data) => request({ url: `/refunds/${id}/fill_return_express/`, method: 'POST', data }),

    // 提交反馈
    submitFeedback: (data) => request({ url: '/feedbacks/', method: 'POST', data }),
    // 获取我的反馈
    getMyFeedbacks: () => request({ url: '/feedbacks/' }),
    // 获取反馈详情
    getFeedbackDetail: (id) => request({ url: `/feedbacks/${id}/` }),

    // ========== 图片上传 ==========
    // 上传图片（返回Promise）
    uploadImage: (filePath, type = 'common') => {
        return new Promise((resolve, reject) => {
            const token = wx.getStorageSync('token');
            wx.uploadFile({
                url: BASE_URL + '/upload/image/',
                filePath: filePath,
                name: 'file',
                formData: { type: type },
                header: {
                    'Authorization': token ? `Bearer ${token}` : ''
                },
                success: (res) => {
                    if (res.statusCode >= 200 && res.statusCode < 300) {
                        try {
                            const data = JSON.parse(res.data);
                            resolve(data);
                        } catch (e) {
                            reject({ message: '解析响应失败' });
                        }
                    } else {
                        reject({ message: '上传失败' });
                    }
                },
                fail: (err) => {
                    reject({ message: '网络错误', error: err });
                }
            });
        });
    },

    // ========== 会员模块 ==========
    // 获取会员套餐列表
    getMembershipPlans: () => request({ url: '/membership/plans/' }),
    // 创建会员订单
    createMembershipOrder: (planId) => request({ url: '/membership/orders/', method: 'POST', data: { plan_id: planId } }),
    // 支付会员订单
    payMembershipOrder: (orderId) => request({ url: `/membership/orders/${orderId}/pay/`, method: 'POST' }),
    // 取消会员订单
    cancelMembershipOrder: (orderId) => request({ url: `/membership/orders/${orderId}/cancel/`, method: 'POST' }),
    // 获取会员订单列表
    getMembershipOrders: () => request({ url: '/membership/orders/' }),
};

module.exports = { api, request, BASE_URL };
