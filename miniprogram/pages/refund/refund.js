// pages/refund/refund.js - 售后列表页
const { api, BASE_URL } = require('../../utils/api');

// 获取媒体文件完整URL
const getMediaUrl = (path) => {
    if (!path) return '/assets/products/fresh_milk.jpg';
    if (path.startsWith('http')) return path;
    if (path.startsWith('/assets')) return path;
    const serverUrl = BASE_URL.replace('/api/v1', '');
    return serverUrl + (path.startsWith('/') ? path : '/' + path);
};

Page({
    data: {
        refundList: [],
        loading: true
    },

    onLoad() {
        this.loadRefundList();
    },

    onShow() {
        // 返回时刷新列表
        this.loadRefundList();
    },

    async loadRefundList() {
        this.setData({ loading: true });
        try {
            const res = await api.getRefunds();
            const list = (res.results || res || []).map(item => ({
                id: item.id,
                refund_no: item.refund_no,
                order_no: item.order_no,
                type: item.type,
                type_label: item.type_display || (item.type === 'refund_only' ? '仅退款' : '退货退款'),
                status: item.status,
                status_label: item.status_display || this.getStatusLabel(item.status),
                reason: item.reason_display || item.reason,
                amount: item.amount,
                created_at: item.created_at,
                product: item.order_info?.items?.[0] ? {
                    name: item.order_info.items[0].product_name,
                    cover_image: getMediaUrl(item.order_info.items[0].product_image)
                } : {
                    name: '商品',
                    cover_image: '/assets/products/fresh_milk.jpg'
                }
            }));
            this.setData({ refundList: list, loading: false });
        } catch (err) {
            console.error('加载退款列表失败:', err);
            this.setData({ refundList: [], loading: false });
            wx.showToast({ title: '加载失败', icon: 'none' });
        }
    },

    getStatusLabel(status) {
        const map = {
            pending: '处理中',
            approved: '已同意',
            rejected: '已拒绝',
            completed: '已完成',
            cancelled: '已取消'
        };
        return map[status] || status;
    },

    viewDetail(e) {
        const id = e.currentTarget.dataset.id;
        const item = this.data.refundList.find(r => r.id === id);
        if (item) {
            let content = `退款单号：${item.refund_no}\n订单号：${item.order_no}\n原因：${item.reason}\n金额：¥${item.amount}\n时间：${item.created_at}`;

            // 如果是待处理状态，显示取消按钮
            if (item.status === 'pending') {
                wx.showModal({
                    title: item.type_label + ' - ' + item.status_label,
                    content: content,
                    cancelText: '取消申请',
                    confirmText: '关闭',
                    success: (res) => {
                        if (res.cancel) {
                            this.cancelRefund(id);
                        }
                    }
                });
            } else {
                wx.showModal({
                    title: item.type_label + ' - ' + item.status_label,
                    content: content,
                    showCancel: false
                });
            }
        }
    },

    async cancelRefund(id) {
        wx.showLoading({ title: '取消中...' });
        try {
            await api.cancelRefund(id);
            wx.hideLoading();
            wx.showToast({ title: '已取消', icon: 'success' });
            this.loadRefundList();
        } catch (err) {
            wx.hideLoading();
            wx.showToast({ title: err.message || '取消失败', icon: 'none' });
        }
    },

    applyNew() {
        // 提示选择订单
        wx.showToast({ title: '请从订单详情页申请售后', icon: 'none' });
    }
});
