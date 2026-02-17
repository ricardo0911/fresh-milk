/**
 * 微信支付工具模块
 * 包含支付流程处理和模拟支付
 */

const { api, BASE_URL } = require('./api');

// 支付状态管理
let paymentResolve = null;
let paymentReject = null;
let currentOrderId = null;

/**
 * 创建订单（不发起支付）
 * @param {Object} orderData - 订单数据
 * @returns {Promise<string>} 订单号
 */
const createOrder = async (orderData) => {
    wx.showLoading({ title: '创建订单...' });

    try {
        // 调用后端API创建订单
        const res = await api.createOrder({
            receiver_name: orderData.address?.receiver_name || orderData.address?.name || '收货人',
            receiver_phone: orderData.address?.receiver_phone || orderData.address?.phone || '',
            receiver_address: `${orderData.address?.province || ''}${orderData.address?.city || ''}${orderData.address?.district || ''}${orderData.address?.detail || orderData.address?.address || ''}`,
            remark: orderData.remark || '',
            items: orderData.items.map(item => ({
                product_id: item.product_id || item.id,
                quantity: item.quantity
            }))
        });

        const order = res.data || res;
        const orderId = order.order_no || order.id;

        wx.hideLoading();
        return orderId;
    } catch (error) {
        wx.hideLoading();
        console.error('创建订单失败:', error);
        throw error;
    }
};

/**
 * 创建订单并发起支付（使用支付弹窗）
 * 此方法返回一个 Promise，需要配合 pay-modal 组件使用
 * @param {Object} orderData - 订单数据
 * @returns {Promise}
 */
const createOrderAndPay = async (orderData) => {
    try {
        // 1. 创建订单
        const orderId = await createOrder(orderData);
        currentOrderId = orderId;

        // 2. 返回订单信息，由页面显示支付弹窗
        return {
            orderId,
            amount: orderData.totalAmount,
            showPayModal: true
        };
    } catch (error) {
        throw error;
    }
};

/**
 * 初始化支付 Promise（由页面调用）
 * @returns {Promise}
 */
const initPaymentPromise = () => {
    return new Promise((resolve, reject) => {
        paymentResolve = resolve;
        paymentReject = reject;
    });
};

/**
 * 支付成功回调（由 pay-modal 组件触发）
 * @param {Object} result - 支付结果
 */
const resolvePayment = (result) => {
    if (paymentResolve) {
        paymentResolve({
            success: true,
            orderId: result.orderId || currentOrderId,
            amount: result.amount,
            method: result.method
        });
        paymentResolve = null;
        paymentReject = null;
    }
};

/**
 * 支付取消/失败回调（由 pay-modal 组件触发）
 * @param {Object} error - 错误信息
 */
const rejectPayment = (error) => {
    if (paymentReject) {
        paymentReject(error || { cancelled: true, message: '用户取消支付' });
        paymentResolve = null;
        paymentReject = null;
    }
};

/**
 * 发起微信支付（旧版兼容，使用 showModal）
 * @param {string} orderId - 订单ID
 * @param {number|string} amount - 支付金额
 * @returns {Promise}
 */
const requestPayment = async (orderId, amount) => {
    return new Promise((resolve, reject) => {
        wx.showModal({
            title: '确认支付',
            content: `支付金额：¥${amount}`,
            confirmText: '确认支付',
            cancelText: '取消',
            success: async (res) => {
                if (res.confirm) {
                    // 显示支付中
                    wx.showLoading({ title: '支付中...' });

                    try {
                        // TODO: 真实环境 - 调用后端获取支付参数
                        // const payParams = await api.getPayParams(orderId);
                        //
                        // 真实微信支付调用:
                        // wx.requestPayment({
                        //   timeStamp: payParams.timeStamp,
                        //   nonceStr: payParams.nonceStr,
                        //   package: payParams.package,
                        //   signType: payParams.signType,
                        //   paySign: payParams.paySign,
                        //   success: (payRes) => {
                        //     wx.hideLoading();
                        //     resolve({ success: true, orderId });
                        //   },
                        //   fail: (payErr) => {
                        //     wx.hideLoading();
                        //     if (payErr.errMsg.includes('cancel')) {
                        //       reject({ cancelled: true, message: '用户取消支付' });
                        //     } else {
                        //       reject({ message: '支付失败', error: payErr });
                        //     }
                        //   }
                        // });

                        // 模拟支付成功
                        await simulatePayment(1500);

                        wx.hideLoading();
                        resolve({ success: true, orderId });

                    } catch (error) {
                        wx.hideLoading();
                        reject(error);
                    }
                } else {
                    reject({ cancelled: true, message: '用户取消支付' });
                }
            }
        });
    });
};

/**
 * 模拟支付过程
 * @param {number} delay - 延迟毫秒数
 */
const simulatePayment = (delay = 1500) => {
    return new Promise((resolve) => {
        setTimeout(resolve, delay);
    });
};

/**
 * 支付成功后的处理
 * @param {string} orderId - 订单号
 */
const onPaymentSuccess = async (orderId) => {
    // 清空购物车已选商品
    const cart = wx.getStorageSync('cart') || [];
    const newCart = cart.filter(item => item.selected === false);
    wx.setStorageSync('cart', newCart);

    // 更新购物车角标
    const app = getApp();
    if (app && app.updateCartBadge) {
        app.updateCartBadge();
    }

    // 调用后端支付接口
    try {
        await api.payOrder(orderId);
    } catch (err) {
        console.error('更新订单支付状态失败:', err);
    }

    return orderId;
};

/**
 * 沙箱支付（用于测试）
 * 直接模拟成功或失败
 */
const sandboxPay = async (amount, shouldSucceed = true) => {
    return new Promise((resolve, reject) => {
        wx.showLoading({ title: '沙箱支付中...' });

        setTimeout(() => {
            wx.hideLoading();

            if (shouldSucceed) {
                resolve({
                    success: true,
                    orderId: 'SANDBOX_' + Date.now(),
                    message: '沙箱支付成功'
                });
            } else {
                reject({
                    success: false,
                    message: '沙箱支付失败（模拟）'
                });
            }
        }, 1000);
    });
};

module.exports = {
    createOrder,
    createOrderAndPay,
    initPaymentPromise,
    resolvePayment,
    rejectPayment,
    requestPayment,
    simulatePayment,
    onPaymentSuccess,
    sandboxPay
};
