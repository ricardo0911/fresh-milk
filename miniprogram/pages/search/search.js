const { api, BASE_URL } = require('../../utils/api')

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
    keyword: '',
    searched: false,
    historyList: [],
    hotList: ['鲜牛奶', '酸奶', '低脂奶', '有机奶', '儿童奶'],
    productList: []
  },

  onLoad() {
    this.loadHistory()
  },

  loadHistory() {
    const history = wx.getStorageSync('searchHistory') || []
    this.setData({ historyList: history })
  },

  saveHistory(keyword) {
    let history = wx.getStorageSync('searchHistory') || []
    history = history.filter(item => item !== keyword)
    history.unshift(keyword)
    history = history.slice(0, 10)
    wx.setStorageSync('searchHistory', history)
    this.setData({ historyList: history })
  },

  onInput(e) {
    this.setData({
      keyword: e.detail.value,
      searched: false
    })
  },

  clearKeyword() {
    this.setData({
      keyword: '',
      searched: false,
      productList: []
    })
  },

  onSearch() {
    const { keyword } = this.data
    if (!keyword.trim()) return

    this.saveHistory(keyword.trim())
    this.searchProducts(keyword.trim())
  },

  searchByTag(e) {
    const keyword = e.currentTarget.dataset.keyword
    this.setData({ keyword })
    this.saveHistory(keyword)
    this.searchProducts(keyword)
  },

  async searchProducts(keyword) {
    wx.showLoading({ title: '搜索中...' })
    try {
      const res = await api.getProducts({ search: keyword })
      const products = (res.results || res || []).map(p => ({
        ...p,
        cover_image: getMediaUrl(p.cover_image)
      }));
      this.setData({
        productList: products,
        searched: true
      })
    } catch (err) {
      console.error('Search error:', err)
      this.setData({
        productList: [],
        searched: true
      })
    } finally {
      wx.hideLoading()
    }
  },

  clearHistory() {
    wx.showModal({
      title: '提示',
      content: '确定清空搜索历史吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('searchHistory')
          this.setData({ historyList: [] })
        }
      }
    })
  },

  goToProduct(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: '/pages/product/product?id=' + id
    })
  },

  goBack() {
    wx.navigateBack()
  }
})
