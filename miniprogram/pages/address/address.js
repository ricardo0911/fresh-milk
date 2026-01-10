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
            // 模拟数据
            const mockAddresses = [
                { id: 1, name: '张三', phone: '13800138000', province: '北京市', city: '北京市', district: '朝阳区', address: '建国路88号SOHO现代城A座1208室', is_default: true },
                { id: 2, name: '李四', phone: '13900139000', province: '上海市', city: '上海市', district: '浦东新区', address: '世纪大道100号上海环球金融中心', is_default: false }
            ];
            this.setData({ addresses: mockAddresses });
        } catch (err) {
            console.error('加载地址失败:', err);
        }
        wx.hideLoading();
    },

    selectAddress(e) {
        if (!this.data.selectMode) return;

        const address = e.currentTarget.dataset.address;
        const pages = getCurrentPages();
        const prevPage = pages[pages.length - 2];

        if (prevPage) {
            prevPage.setData({ selectedAddress: address });
        }
        wx.navigateBack();
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
                name: address.name,
                phone: address.phone,
                address: address.address,
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
                ...form,
                province: region[0],
                city: region[1],
                district: region[2]
            };

            if (editingAddress) {
                // TODO: 调用更新API
                // await api.updateAddress(editingAddress.id, data);
            } else {
                // TODO: 调用添加API
                // await api.addAddress(data);
            }

            await new Promise(resolve => setTimeout(resolve, 500));

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
            // TODO: 调用API
            // await api.setDefaultAddress(id);
            await new Promise(resolve => setTimeout(resolve, 300));

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
                        // TODO: 调用API
                        // await api.deleteAddress(id);
                        await new Promise(resolve => setTimeout(resolve, 300));

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
