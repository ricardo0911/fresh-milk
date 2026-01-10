/**
 * 工具函数模块
 */

// 格式化价格
function formatPrice(price) {
    return parseFloat(price).toFixed(2);
}

// 格式化日期
function formatDate(dateString, format = 'YYYY-MM-DD') {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return format
        .replace('YYYY', year)
        .replace('MM', month)
        .replace('DD', day)
        .replace('HH', hours)
        .replace('mm', minutes);
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 显示Toast消息
function showToast(message, type = 'info', duration = 3000) {
    // 移除已存在的toast
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${getToastIcon(type)}</span>
        <span class="toast-message">${message}</span>
    `;

    // 添加样式
    Object.assign(toast.style, {
        position: 'fixed',
        top: '100px',
        left: '50%',
        transform: 'translateX(-50%) translateY(-20px)',
        padding: '12px 24px',
        background: getToastBackground(type),
        color: 'white',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        fontSize: '14px',
        fontWeight: '500',
        zIndex: '9999',
        opacity: '0',
        transition: 'all 0.3s ease'
    });

    document.body.appendChild(toast);

    // 动画显示
    requestAnimationFrame(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(-50%) translateY(0)';
    });

    // 自动关闭
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(-50%) translateY(-20px)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

function getToastIcon(type) {
    const icons = {
        success: '✓',
        error: '✕',
        warning: '!',
        info: 'i'
    };
    return icons[type] || icons.info;
}

function getToastBackground(type) {
    const backgrounds = {
        success: 'linear-gradient(135deg, #10b981, #059669)',
        error: 'linear-gradient(135deg, #ef4444, #dc2626)',
        warning: 'linear-gradient(135deg, #f59e0b, #d97706)',
        info: 'linear-gradient(135deg, #3b82f6, #2563eb)'
    };
    return backgrounds[type] || backgrounds.info;
}

// 显示加载动画
function showLoading(container) {
    const loading = document.createElement('div');
    loading.className = 'loading-spinner';
    loading.innerHTML = `
        <div class="spinner"></div>
        <style>
            .loading-spinner {
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 40px;
            }
            .spinner {
                width: 40px;
                height: 40px;
                border: 3px solid #e5e7eb;
                border-top-color: #10b981;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        </style>
    `;
    container.innerHTML = '';
    container.appendChild(loading);
    return loading;
}

// 隐藏加载
function hideLoading(loading) {
    if (loading && loading.parentNode) {
        loading.remove();
    }
}

// 创建骨架屏
function createSkeleton(type, count = 1) {
    const skeletons = [];

    for (let i = 0; i < count; i++) {
        const skeleton = document.createElement('div');
        skeleton.className = 'skeleton-item';

        if (type === 'product-card') {
            skeleton.innerHTML = `
                <div class="skeleton" style="aspect-ratio: 4/3; margin-bottom: 12px;"></div>
                <div class="skeleton" style="height: 20px; width: 80%; margin-bottom: 8px;"></div>
                <div class="skeleton" style="height: 14px; width: 60%; margin-bottom: 12px;"></div>
                <div class="skeleton" style="height: 24px; width: 40%;"></div>
            `;
            skeleton.style.background = 'white';
            skeleton.style.borderRadius = '16px';
            skeleton.style.padding = '16px';
        } else if (type === 'category-card') {
            skeleton.innerHTML = `
                <div class="skeleton" style="width: 64px; height: 64px; border-radius: 16px; margin: 0 auto 16px;"></div>
                <div class="skeleton" style="height: 16px; width: 60%; margin: 0 auto;"></div>
            `;
            skeleton.style.background = 'white';
            skeleton.style.borderRadius = '16px';
            skeleton.style.padding = '32px 16px';
        }

        skeletons.push(skeleton);
    }

    return skeletons;
}

// 检查是否登录
function isLoggedIn() {
    return !!localStorage.getItem('access_token');
}

// 获取当前用户
function getCurrentUserFromStorage() {
    const user = localStorage.getItem('current_user');
    return user ? JSON.parse(user) : null;
}

// 设置当前用户
function setCurrentUser(user) {
    localStorage.setItem('current_user', JSON.stringify(user));
}

// 清除当前用户
function clearCurrentUser() {
    localStorage.removeItem('current_user');
}

// 获取购物车数量
function getCartCount() {
    const cart = localStorage.getItem('cart_items');
    if (cart) {
        const items = JSON.parse(cart);
        return items.reduce((sum, item) => sum + item.quantity, 0);
    }
    return 0;
}

// 更新购物车徽标
function updateCartBadge() {
    const badge = document.getElementById('cartBadge');
    if (badge) {
        const count = getCartCount();
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
}

// 本地购物车操作 (未登录时使用)
const localCart = {
    getItems() {
        const cart = localStorage.getItem('cart_items');
        return cart ? JSON.parse(cart) : [];
    },

    addItem(product, quantity = 1) {
        const items = this.getItems();
        const existingIndex = items.findIndex(item => item.product.id === product.id);

        if (existingIndex > -1) {
            items[existingIndex].quantity += quantity;
        } else {
            items.push({ product, quantity });
        }

        localStorage.setItem('cart_items', JSON.stringify(items));
        updateCartBadge();
        return items;
    },

    updateQuantity(productId, quantity) {
        const items = this.getItems();
        const index = items.findIndex(item => item.product.id === productId);

        if (index > -1) {
            if (quantity <= 0) {
                items.splice(index, 1);
            } else {
                items[index].quantity = quantity;
            }
            localStorage.setItem('cart_items', JSON.stringify(items));
            updateCartBadge();
        }

        return items;
    },

    removeItem(productId) {
        const items = this.getItems().filter(item => item.product.id !== productId);
        localStorage.setItem('cart_items', JSON.stringify(items));
        updateCartBadge();
        return items;
    },

    clear() {
        localStorage.removeItem('cart_items');
        updateCartBadge();
    },

    getTotal() {
        return this.getItems().reduce((total, item) => {
            return total + parseFloat(item.product.price) * item.quantity;
        }, 0);
    }
};

// 滚动到元素
function scrollToElement(element, offset = 80) {
    const y = element.getBoundingClientRect().top + window.pageYOffset - offset;
    window.scrollTo({ top: y, behavior: 'smooth' });
}

// URL参数解析
function getUrlParams() {
    const params = new URLSearchParams(window.location.search);
    const result = {};
    for (const [key, value] of params) {
        result[key] = value;
    }
    return result;
}

// 导出
window.utils = {
    formatPrice,
    formatDate,
    debounce,
    throttle,
    showToast,
    showLoading,
    hideLoading,
    createSkeleton,
    isLoggedIn,
    getCurrentUserFromStorage,
    setCurrentUser,
    clearCurrentUser,
    getCartCount,
    updateCartBadge,
    localCart,
    scrollToElement,
    getUrlParams
};
