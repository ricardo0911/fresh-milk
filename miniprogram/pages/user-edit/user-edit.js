const app = getApp();

Page({
    data: {
        userInfo: {
            avatar: '',
            nickname: '',
            phone: '',
            gender: 0,
            birthday: '',
            genderDisplay: ''
        },
        originalUserInfo: null,
        genderOptions: ['保密', '男', '女'],
        genderIndex: -1
    },

    onLoad() {
        this.loadUserInfo();
    },

    loadUserInfo() {
        // 先显示当前全局数据
        const userInfo = app.globalData.userInfo || wx.getStorageSync('userInfo') || {};
        this.setLocalUserInfo(userInfo);

        // 刷新最新数据
        this.fetchUserProfile();
    },

    setLocalUserInfo(userInfo) {
        const gender = userInfo.gender || 0;
        const genderIndex = gender === 1 ? 1 : (gender === 2 ? 2 : 0);

        this.setData({
            userInfo: {
                avatar: userInfo.avatar || '',
                nickname: userInfo.nickname || userInfo.username || '',
                phone: userInfo.phone || '',
                gender: gender,
                birthday: userInfo.birthday || '',
                genderDisplay: this.data.genderOptions[genderIndex]
            },
            genderIndex: genderIndex,
            originalUserInfo: { ...userInfo }
        });
    },

    fetchUserProfile() {
        const token = wx.getStorageSync('token');
        if (!token) return;

        wx.request({
            url: `${app.globalData.baseUrl}/users/me/`,
            method: 'GET',
            header: {
                'Authorization': `Bearer ${token}`
            },
            success: (res) => {
                if (res.statusCode === 200) {
                    this.setLocalUserInfo(res.data);
                } else if (res.statusCode === 401) {
                    this.handleUnauthorized();
                }
            },
            fail: () => {
                // 网络错误等
            }
        });
    },

    onChooseAvatar(e) {
        const { avatarUrl } = e.detail;
        this.setData({
            'userInfo.avatar': avatarUrl
        });
    },

    onNicknameChange(e) {
        this.setData({
            'userInfo.nickname': e.detail.value
        });
    },

    onNicknameBlur(e) {
        this.setData({
            'userInfo.nickname': e.detail.value
        });
    },

    onGenderChange(e) {
        const index = e.detail.value;
        this.setData({
            genderIndex: index,
            'userInfo.gender': index // 假设后端使用 0/1/2
        });
    },

    onDateChange(e) {
        this.setData({
            'userInfo.birthday': e.detail.value
        });
    },

    saveProfile() {
        const { userInfo } = this.data;
        if (!userInfo.nickname.trim()) {
            wx.showToast({ title: '昵称不能为空', icon: 'none' });
            return;
        }

        wx.showLoading({ title: '保存中...' });

        const token = wx.getStorageSync('token');
        // 判断头像是否是本地临时文件（需要上传）
        // 微信临时文件可能是 wxfile:// 或 http://tmp/ 开头
        const avatar = userInfo.avatar || '';
        const isLocalFile = avatar && (
            avatar.startsWith('wxfile://') ||
            avatar.startsWith('http://tmp') ||
            avatar.startsWith('https://tmp') ||
            avatar.indexOf('/tmp/') !== -1
        );

        console.log('Avatar path:', avatar, 'isLocalFile:', isLocalFile);

        if (isLocalFile) {
            this.uploadAvatarAndProfile(token);
        } else {
            this.updateProfileOnly(token);
        }
    },

    uploadAvatarAndProfile(token) {
        const formData = {
            'username': this.data.userInfo.nickname,
            'nickname': this.data.userInfo.nickname,
            'gender': String(this.data.userInfo.gender)
        };
        // 只有当 birthday 有值时才发送
        if (this.data.userInfo.birthday) {
            formData.birthday = this.data.userInfo.birthday;
        }

        console.log('Uploading with formData:', formData);
        console.log('Avatar file path:', this.data.userInfo.avatar);

        wx.uploadFile({
            url: `${app.globalData.baseUrl}/users/me/`,
            filePath: this.data.userInfo.avatar,
            name: 'avatar',
            header: {
                'Authorization': `Bearer ${token}`
            },
            formData: formData,
            success: (res) => {
                console.log('Upload response:', res.statusCode, res.data);
                // uploadFile success returns data as String, need to parse
                let data = res.data;
                try {
                    data = JSON.parse(res.data);
                } catch (e) {
                    console.error('Parse error', e);
                }

                if (res.statusCode >= 200 && res.statusCode < 300) {
                    this.handleSuccess(data);
                } else {
                    this.handleFail(res.statusCode, data);
                }
            },
            fail: (err) => {
                console.error('Upload failed:', err);
                wx.hideLoading();
                wx.showToast({ title: '请求失败', icon: 'none' });
            }
        });
    },

    updateProfileOnly(token) {
        const data = {
            username: this.data.userInfo.nickname,
            nickname: this.data.userInfo.nickname,
            gender: this.data.userInfo.gender
        };
        // 只有当 birthday 有值时才发送
        if (this.data.userInfo.birthday) {
            data.birthday = this.data.userInfo.birthday;
        }

        console.log('Updating profile with data:', data);

        wx.request({
            url: `${app.globalData.baseUrl}/users/me/`,
            method: 'PATCH',
            header: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            data: data,
            success: (res) => {
                console.log('Update response:', res.statusCode, res.data);
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    this.handleSuccess(res.data);
                } else {
                    this.handleFail(res.statusCode, res.data);
                }
            },
            fail: (err) => {
                console.error('Update failed:', err);
                wx.hideLoading();
                wx.showToast({ title: '请求失败', icon: 'none' });
            }
        });
    },

    handleSuccess(data) {
        wx.hideLoading();
        wx.showToast({ title: '保存成功', icon: 'success' });

        app.globalData.userInfo = data;
        wx.setStorageSync('userInfo', data);

        const pages = getCurrentPages();
        const prevPage = pages[pages.length - 2];
        if (prevPage && prevPage.loadUserInfo) {
            prevPage.loadUserInfo();
        }

        setTimeout(() => {
            wx.navigateBack();
        }, 1500);
    },

    handleFail(statusCode, data) {
        wx.hideLoading();
        if (statusCode === 401) {
            this.handleUnauthorized();
            return;
        }

        console.error('Update failed', statusCode, data);
        let msg = '保存失败';
        if (data && data.username) {
            msg = data.username[0];
        } else if (data && data.detail) {
            msg = data.detail;
        }
        wx.showToast({ title: msg, icon: 'none' });
    },

    handleUnauthorized() {
        wx.removeStorageSync('token');
        app.globalData.token = null;
        wx.showToast({ title: '登录已过期，请重新登录', icon: 'none' });
        setTimeout(() => {
            wx.navigateTo({ url: '/pages/login/login' });
        }, 1500);
    },

    goChangePassword() {
        wx.navigateTo({
            url: '/pages/change-password/change-password'
        });
    }
});
