/**
 * API 模块 - 处理所有后端API请求
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

// 获取JWT Token
function getToken() {
    return localStorage.getItem('access_token');
}

// 设置JWT Token
function setToken(accessToken, refreshToken) {
    localStorage.setItem('access_token', accessToken);
    if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken);
    }
}

// 清除Token
function clearToken() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}

// 通用请求函数
async function request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(url, {
            ...options,
            headers,
        });

        // 处理401错误 - Token过期
        if (response.status === 401) {
            clearToken();
            window.location.href = '/login.html';
            return null;
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || data.message || '请求失败');
        }

        return data;
    } catch (error) {
        console.error('API请求错误:', error);
        throw error;
    }
}

// API 方法
const api = {
    // ===== 用户相关 =====
    // 登录
    async login(username, password) {
        const data = await request('/users/login/', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
        if (data && data.access) {
            setToken(data.access, data.refresh);
        }
        return data;
    },

    // 注册
    async register(userData) {
        return request('/users/register/', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    },

    // 获取当前用户信息
    async getCurrentUser() {
        return request('/users/me/');
    },

    // 更新用户信息
    async updateUser(userData) {
        return request('/users/me/', {
            method: 'PATCH',
            body: JSON.stringify(userData),
        });
    },

    // ===== 产品相关 =====
    // 获取分类列表
    async getCategories() {
        return request('/categories/');
    },

    // 获取产品列表
    async getProducts(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return request(`/products/${queryString ? '?' + queryString : ''}`);
    },

    // 获取热门产品
    async getHotProducts() {
        return request('/products/?is_hot=true');
    },

    // 获取新品
    async getNewProducts() {
        return request('/products/?is_new=true');
    },

    // 获取产品详情
    async getProduct(id) {
        return request(`/products/${id}/`);
    },

    // ===== 购物车相关 =====
    // 获取购物车
    async getCart() {
        return request('/cart/');
    },

    // 添加到购物车
    async addToCart(productId, quantity = 1) {
        return request('/cart/', {
            method: 'POST',
            body: JSON.stringify({ product: productId, quantity }),
        });
    },

    // 更新购物车商品数量
    async updateCartItem(itemId, quantity) {
        return request(`/cart/${itemId}/`, {
            method: 'PATCH',
            body: JSON.stringify({ quantity }),
        });
    },

    // 删除购物车商品
    async removeFromCart(itemId) {
        return request(`/cart/${itemId}/`, {
            method: 'DELETE',
        });
    },

    // ===== 订单相关 =====
    // 创建订单
    async createOrder(orderData) {
        return request('/orders/', {
            method: 'POST',
            body: JSON.stringify(orderData),
        });
    },

    // 获取订单列表
    async getOrders(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return request(`/orders/${queryString ? '?' + queryString : ''}`);
    },

    // 获取订单详情
    async getOrder(id) {
        return request(`/orders/${id}/`);
    },

    // 取消订单
    async cancelOrder(id) {
        return request(`/orders/${id}/cancel/`, {
            method: 'POST',
        });
    },

    // ===== 地址相关 =====
    // 获取地址列表
    async getAddresses() {
        return request('/addresses/');
    },

    // 添加地址
    async addAddress(addressData) {
        return request('/addresses/', {
            method: 'POST',
            body: JSON.stringify(addressData),
        });
    },

    // 更新地址
    async updateAddress(id, addressData) {
        return request(`/addresses/${id}/`, {
            method: 'PATCH',
            body: JSON.stringify(addressData),
        });
    },

    // 删除地址
    async deleteAddress(id) {
        return request(`/addresses/${id}/`, {
            method: 'DELETE',
        });
    },

    // ===== 优惠券相关 =====
    // 获取可用优惠券
    async getAvailableCoupons() {
        return request('/coupons/available/');
    },

    // 获取我的优惠券
    async getMyCoupons() {
        return request('/user-coupons/');
    },

    // 领取优惠券
    async receiveCoupon(couponId) {
        return request('/user-coupons/receive/', {
            method: 'POST',
            body: JSON.stringify({ coupon_id: couponId }),
        });
    },

    // ===== 评论相关 =====
    // 获取产品评论
    async getProductComments(productId, page = 1) {
        return request(`/comments/?product=${productId}&page=${page}`);
    },

    // 添加评论
    async addComment(commentData) {
        return request('/comments/', {
            method: 'POST',
            body: JSON.stringify(commentData),
        });
    },

    // ===== 收藏相关 =====
    // 获取收藏列表
    async getFavorites() {
        return request('/favorites/');
    },

    // 添加收藏
    async addFavorite(productId) {
        return request('/favorites/', {
            method: 'POST',
            body: JSON.stringify({ product: productId }),
        });
    },

    // 移除收藏
    async removeFavorite(id) {
        return request(`/favorites/${id}/`, {
            method: 'DELETE',
        });
    },
};

// 导出
window.api = api;
