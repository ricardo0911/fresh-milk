const { api } = require('../../utils/api.js')

Page({
    data: {
        favorites: [],
        loading: true,
        isEmpty: false
    },

    onShow() {
        this.loadFavorites()
    },

    onPullDownRefresh() {
        this.loadFavorites().then(() => {
            wx.stopPullDownRefresh()
        })
    },

    async loadFavorites() {
        try {
            this.setData({ loading: true })
            const res = await api.getFavorites()
            // 后端返回的是分页结果或列表，根据 Serializer 应该是列表列表
            // ModelViewSet 默认 list 返回 pagination，除非配置了不分页
            // 假设 result 结构是 verify from previous views request.js usually returns response.data

            const list = res.results || res || []
            this.setData({
                favorites: list,
                isEmpty: list.length === 0,
                loading: false
            })
        } catch (error) {
            console.error('加载收藏失败', error)
            this.setData({ loading: false })
            wx.showToast({
                title: '加载失败',
                icon: 'none'
            })
        }
    },

    goToProduct(e) {
        const id = e.currentTarget.dataset.id
        wx.navigateTo({
            url: `/pages/product/product?id=${id}`
        })
    },

    async removeFavorite(e) {
        const id = e.currentTarget.dataset.id // Product ID
        const index = e.currentTarget.dataset.index

        wx.showModal({
            title: '提示',
            content: '确定要取消收藏吗？',
            success: async (res) => {
                if (res.confirm) {
                    try {
                        await api.toggleFavorite({ product_id: id })

                        const newList = this.data.favorites.filter((item, idx) => idx !== index)
                        this.setData({
                            favorites: newList,
                            isEmpty: newList.length === 0
                        })

                        wx.showToast({
                            title: '已取消',
                            icon: 'none'
                        })
                    } catch (error) {
                        console.error('取消收藏失败', error)
                        wx.showToast({
                            title: '操作失败',
                            icon: 'none'
                        })
                    }
                }
            }
        })
    }
})
