import request from '@/utils/request'

// 获取仪表盘数据
export function getDashboard() {
  return request.get('/admin/dashboard/')
}

// 获取销售统计
export function getSalesStatistics(params) {
  return request.get('/admin/statistics/sales/', { params })
}

// 获取产品统计
export function getProductStatistics() {
  return request.get('/admin/statistics/products/')
}

// 获取用户统计
export function getUserStatistics(params) {
  return request.get('/admin/statistics/users/', { params })
}
