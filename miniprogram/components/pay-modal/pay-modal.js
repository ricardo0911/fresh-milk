/**
 * 仿微信支付弹窗组件
 */
Component({
    properties: {
        // 是否显示
        visible: {
            type: Boolean,
            value: false
        },
        // 支付金额
        amount: {
            type: String,
            value: '0.00'
        },
        // 标题
        title: {
            type: String,
            value: '确认支付'
        },
        // 订单ID
        orderId: {
            type: String,
            value: ''
        },
        // 账户余额
        balance: {
            type: String,
            value: '0.00'
        },
        // 是否显示自定义键盘
        showKeyboard: {
            type: Boolean,
            value: false
        }
    },

    data: {
        selectedMethod: 'wechat',
        showPassword: false,
        password: '',
        paying: false,
        payResult: null,
        errorMessage: ''
    },

    methods: {
        // 阻止滚动穿透
        preventMove() { },

        // 阻止冒泡
        stopPropagation() { },

        // 点击遮罩
        onMaskTap() {
            if (!this.data.paying) {
                this.onClose();
            }
        },

        // 关闭弹窗
        onClose() {
            if (this.data.paying) return;

            this.setData({
                showPassword: false,
                password: '',
                paying: false,
                payResult: null,
                errorMessage: ''
            });
            this.triggerEvent('close');
        },

        // 选择支付方式
        selectMethod(e) {
            const method = e.currentTarget.dataset.method;
            this.setData({ selectedMethod: method });
        },

        // 点击支付按钮
        onPayClick() {
            // 显示密码输入界面
            this.setData({ showPassword: true, password: '' });
        },

        // 键盘按键
        onKeyTap(e) {
            const key = e.currentTarget.dataset.key;
            if (this.data.password.length < 6) {
                const password = this.data.password + key;
                this.setData({ password });

                if (password.length === 6) {
                    this.verifyAndPay(password);
                }
            }
        },

        // 删除键
        onDeleteTap() {
            if (this.data.password.length > 0) {
                this.setData({
                    password: this.data.password.slice(0, -1)
                });
            }
        },

        // 验证密码并支付
        verifyAndPay(password) {
            // 模拟密码验证 (测试密码: 123456)
            const correctPassword = '123456';

            this.setData({
                paying: true,
                showPassword: false
            });

            // 模拟支付过程
            setTimeout(() => {
                if (password === correctPassword) {
                    // 支付成功
                    this.setData({
                        paying: false,
                        payResult: 'success'
                    });

                    // 延迟触发成功事件
                    setTimeout(() => {
                        this.triggerEvent('success', {
                            orderId: this.properties.orderId || 'ORDER_' + Date.now(),
                            amount: this.properties.amount,
                            method: this.data.selectedMethod
                        });
                    }, 1000);
                } else {
                    // 支付失败
                    this.setData({
                        paying: false,
                        payResult: 'fail',
                        errorMessage: '支付密码错误，请重试'
                    });

                    // 延迟重置状态
                    setTimeout(() => {
                        this.setData({
                            payResult: null,
                            errorMessage: '',
                            showPassword: true,
                            password: ''
                        });
                    }, 2000);
                }
            }, 2000);
        },

        // 重置组件状态
        reset() {
            this.setData({
                selectedMethod: 'wechat',
                showPassword: false,
                password: '',
                paying: false,
                payResult: null,
                errorMessage: ''
            });
        }
    },

    observers: {
        'visible': function (visible) {
            if (!visible) {
                // 关闭时重置状态
                this.reset();
            }
        }
    }
});
