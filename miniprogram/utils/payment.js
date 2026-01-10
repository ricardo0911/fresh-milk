/**
 * 微信支付工具模块
 * 包含支付流程处理和模拟支付
 */

const { api, BASE_URL } = require('./api');

/**
 * 创建订单并发起支付
 * @param {Object} orderData - 订单数据
 * @returns {Promise}
 */
const createOrderAndPay = async (orderData) => {
    try {
        // 1. 创建订单
        wx.showLoading({ title: '创建订单...' });

        // TODO: 真实环境调用后端API创建订单
        // const orderResult = await api.createOrder(orderData);
        // const orderId = orderResult.id;

        // 模拟创建订单
        const orderId = 'ORDER_' + Date.now();

        wx.hideLoading();

        // 2. 发起支付
        return await requestPayment(orderId, orderData.totalAmount);
    } catch (error) {
        wx.hideLoading();
        throw error;
    }
};

/**
 * 发起微信支付
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
 * @param {string} orderId - 订单ID
 */
const onPaymentSuccess = (orderId) => {
    // 清空购物车已选商品
    const cart = wx.getStorageSync('cart') || [];
    const newCart = cart.filter(item => item.selected === false);
    wx.setStorageSync('cart', newCart);

    // 更新购物车角标
    const app = getApp();
    if (app && app.updateCartBadge) {
        app.updateCartBadge();
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
    createOrderAndPay,
    requestPayment,
    simulatePayment,
    onPaymentSuccess,
    sandboxPay
};
