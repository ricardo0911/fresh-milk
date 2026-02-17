// pages/express-trace/express-trace.js - 物流轨迹页面
const { api } = require('../../utils/api');

// 快递公司名称映射
const expressCompanyMap = {
    'SF': '顺丰速运',
    'YTO': '圆通速递',
    'ZTO': '中通快递',
    'YD': '韵达快递',
    'JTSD': '极兔速递'
};

// 物流状态映射
const expressStatusMap = {
    'created': '已下单',
    'collected': '已揽收',
    'in_transit': '运输中',
    'delivering': '派送中',
    'signed': '已签收',
    'failed': '签收失败',
    'cancelled': '已取消'
};

Page({
    data: {
        orderId: null,
        expressInfo: null,
        traces: [],
        loading: true
    },

    onLoad(options) {
        // 支持 order_id 和 order_no 两种参数
        const orderId = options.order_id || options.order_no;
        if (orderId) {
            this.setData({ orderId: orderId });
            this.loadExpressTrace();
        }
    },

    async loadExpressTrace() {
        this.setData({ loading: true });
        try {
            const res = await api.getExpressTrace(this.data.orderId);
            if (res) {
                this.setData({
                    expressInfo: {
                        company: expressCompanyMap[res.express_company] || res.express_company,
                        no: res.express_no,
                        status: expressStatusMap[res.status] || res.status
                    },
                    traces: res.traces || []
                });
            }
        } catch (err) {
            console.error('加载物流轨迹失败:', err);
            wx.showToast({ title: '加载失败', icon: 'none' });
        }
        this.setData({ loading: false });
    },

    // 复制快递单号
    copyExpressNo() {
        const expressNo = this.data.expressInfo?.no;
        if (expressNo) {
            wx.setClipboardData({
                data: expressNo,
                success: () => {
                    wx.showToast({ title: '已复制', icon: 'success' });
                }
            });
        }
    },

    // 刷新物流信息
    onRefresh() {
        this.loadExpressTrace();
    }
});
