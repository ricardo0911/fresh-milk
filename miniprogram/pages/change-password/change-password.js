const app = getApp();

Page({
    data: {
        oldPassword: '',
        newPassword: '',
        confirmPassword: '',
        showOldPassword: false,
        showNewPassword: false,
        showConfirmPassword: false
    },

    onOldPasswordInput(e) {
        this.setData({ oldPassword: e.detail.value });
    },

    onNewPasswordInput(e) {
        this.setData({ newPassword: e.detail.value });
    },

    onConfirmPasswordInput(e) {
        this.setData({ confirmPassword: e.detail.value });
    },

    toggleOldPassword() {
        this.setData({ showOldPassword: !this.data.showOldPassword });
    },

    toggleNewPassword() {
        this.setData({ showNewPassword: !this.data.showNewPassword });
    },

    toggleConfirmPassword() {
        this.setData({ showConfirmPassword: !this.data.showConfirmPassword });
    },

    submitChangePassword() {
        const { oldPassword, newPassword, confirmPassword } = this.data;

        if (!oldPassword) {
            wx.showToast({ title: '请输入原密码', icon: 'none' });
            return;
        }

        if (!newPassword) {
            wx.showToast({ title: '请输入新密码', icon: 'none' });
            return;
        }

        if (newPassword.length < 8) {
            wx.showToast({ title: '新密码长度至少8位', icon: 'none' });
            return;
        }

        if (newPassword !== confirmPassword) {
            wx.showToast({ title: '两次输入的密码不一致', icon: 'none' });
            return;
        }

        if (oldPassword === newPassword) {
            wx.showToast({ title: '新密码不能与原密码相同', icon: 'none' });
            return;
        }

        wx.showLoading({ title: '提交中...' });

        const token = wx.getStorageSync('token');
        wx.request({
            url: `${app.globalData.baseUrl}/users/change_password/`,
            method: 'POST',
            header: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            data: {
                old_password: oldPassword,
                new_password: newPassword
            },
            success: (res) => {
                wx.hideLoading();
                if (res.statusCode === 200) {
                    wx.showToast({ title: '密码修改成功', icon: 'success' });
                    setTimeout(() => {
                        wx.navigateBack();
                    }, 1500);
                } else if (res.statusCode === 400) {
                    const msg = res.data.old_password || res.data.new_password || res.data.detail || '修改失败';
                    wx.showToast({ title: Array.isArray(msg) ? msg[0] : msg, icon: 'none' });
                } else if (res.statusCode === 401) {
                    wx.removeStorageSync('token');
                    wx.showToast({ title: '登录已过期，请重新登录', icon: 'none' });
                    setTimeout(() => {
                        wx.navigateTo({ url: '/pages/login/login' });
                    }, 1500);
                } else {
                    wx.showToast({ title: '修改失败，请稍后重试', icon: 'none' });
                }
            },
            fail: () => {
                wx.hideLoading();
                wx.showToast({ title: '网络错误，请稍后重试', icon: 'none' });
            }
        });
    }
});
