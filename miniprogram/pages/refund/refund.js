// pages/refund/refund.js - 售后列表页
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

    loadRefundList() {
        // 模拟数据
        const mockList = [
            {
                id: 1,
                order_no: 'FM20240115001',
                type: 'refund',
                type_label: '仅退款',
                status: 'processing',
                status_label: '处理中',
                reason: '商品质量问题',
                amount: '39.90',
                created_at: '2024-01-15 10:30',
                product: {
                    name: '每日鲜牛奶',
                    cover_image: '/assets/products/fresh_milk.jpg'
                }
            },
            {
                id: 2,
                order_no: 'FM20240110002',
                type: 'return',
                type_label: '退货退款',
                status: 'completed',
                status_label: '已完成',
                reason: '未按时送达',
                amount: '89.00',
                created_at: '2024-01-10 14:20',
                product: {
                    name: '有机纯牛奶',
                    cover_image: '/assets/products/organic_milk.jpg'
                }
            }
        ];

        setTimeout(() => {
            this.setData({
                refundList: mockList,
                loading: false
            });
        }, 500);
    },

    viewDetail(e) {
        const id = e.currentTarget.dataset.id;
        // 显示详情弹窗
        const item = this.data.refundList.find(r => r.id === id);
        if (item) {
            wx.showModal({
                title: item.type_label + ' - ' + item.status_label,
                content: `订单：${item.order_no}\n原因：${item.reason}\n金额：¥${item.amount}\n时间：${item.created_at}`,
                showCancel: false
            });
        }
    },

    applyNew() {
        // 提示选择订单
        wx.showToast({ title: '请从订单详情页申请售后', icon: 'none' });
    }
});
