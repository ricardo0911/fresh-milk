// pages/address/address.js - 收货地址逻辑
const { api } = require('../../utils/api');

Page({
    data: {
        addresses: [],
        showForm: false,
        editingAddress: null,
        form: {
            name: '',
            phone: '',
            address: '',
            is_default: false
        },
        region: [],
        selectMode: false // 是否是选择地址模式
    },

    onLoad(options) {
        if (options.select === '1') {
            this.setData({ selectMode: true });
        }
        this.loadAddresses();
    },

    async loadAddresses() {
        wx.showLoading({ title: '加载中...' });
        try {
            const res = await api.getAddresses();
            // 后端返回的可能是 { results: [...] } 或直接是数组
            const addresses = res.results || res || [];
            this.setData({ addresses });
        } catch (err) {
            console.error('加载地址失败:', err);
            wx.showToast({ title: '加载地址失败', icon: 'none' });
        }
        wx.hideLoading();
    },

    selectAddress(e) {
        const address = e.currentTarget.dataset.address;
        const pages = getCurrentPages();
        const prevPage = pages[pages.length - 2];

        // 如果是选择模式，或者有上一页需要接收地址
        if (this.data.selectMode && prevPage) {
            prevPage.setData({ selectedAddress: address });
            wx.navigateBack();
        }
    },

    showAddForm() {
        this.setData({
            showForm: true,
            editingAddress: null,
            form: { name: '', phone: '', address: '', is_default: false },
            region: []
        });
    },

    editAddress(e) {
        const address = e.currentTarget.dataset.address;
        this.setData({
            showForm: true,
            editingAddress: address,
            form: {
                name: address.receiver_name,
                phone: address.receiver_phone,
                address: address.detail,
                is_default: address.is_default
            },
            region: [address.province, address.city, address.district]
        });
    },

    hideForm() {
        this.setData({ showForm: false });
    },

    onInput(e) {
        const field = e.currentTarget.dataset.field;
        this.setData({
            [`form.${field}`]: e.detail.value
        });
    },

    onRegionChange(e) {
        this.setData({ region: e.detail.value });
    },

    onDefaultChange(e) {
        this.setData({ 'form.is_default': e.detail.value });
    },

    async saveAddress() {
        const { form, region, editingAddress } = this.data;

        // 验证
        if (!form.name.trim()) {
            wx.showToast({ title: '请输入收货人', icon: 'none' });
            return;
        }
        if (!/^1\d{10}$/.test(form.phone)) {
            wx.showToast({ title: '请输入正确的手机号', icon: 'none' });
            return;
        }
        if (region.length < 3) {
            wx.showToast({ title: '请选择所在地区', icon: 'none' });
            return;
        }
        if (!form.address.trim()) {
            wx.showToast({ title: '请输入详细地址', icon: 'none' });
            return;
        }

        wx.showLoading({ title: '保存中...' });
        try {
            const data = {
                receiver_name: form.name,
                receiver_phone: form.phone,
                detail: form.address,
                is_default: form.is_default,
                province: region[0],
                city: region[1],
                district: region[2]
            };

            if (editingAddress) {
                await api.updateAddress(editingAddress.id, data);
            } else {
                await api.addAddress(data);
            }

            wx.hideLoading();
            wx.showToast({ title: '保存成功', icon: 'success' });
            this.setData({ showForm: false });
            this.loadAddresses();
        } catch (err) {
            wx.hideLoading();
            wx.showToast({ title: err.message || '保存失败', icon: 'none' });
        }
    },

    async setDefault(e) {
        const id = e.currentTarget.dataset.id;

        wx.showLoading({ title: '设置中...' });
        try {
            await api.setDefaultAddress(id);

            // 更新本地状态
            const addresses = this.data.addresses.map(a => ({
                ...a,
                is_default: a.id === id
            }));
            this.setData({ addresses });

            wx.hideLoading();
            wx.showToast({ title: '设置成功', icon: 'success' });
        } catch (err) {
            wx.hideLoading();
            wx.showToast({ title: '设置失败', icon: 'none' });
        }
    },

    deleteAddress(e) {
        const id = e.currentTarget.dataset.id;

        wx.showModal({
            title: '确认删除',
            content: '确定要删除这个地址吗？',
            success: async (res) => {
                if (res.confirm) {
                    wx.showLoading({ title: '删除中...' });
                    try {
                        await api.deleteAddress(id);

                        const addresses = this.data.addresses.filter(a => a.id !== id);
                        this.setData({ addresses });

                        wx.hideLoading();
                        wx.showToast({ title: '删除成功', icon: 'success' });
                    } catch (err) {
                        wx.hideLoading();
                        wx.showToast({ title: '删除失败', icon: 'none' });
                    }
                }
            }
        });
    }
});
