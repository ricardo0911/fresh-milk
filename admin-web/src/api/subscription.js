import request from '@/utils/request'

// 获取订阅列表（管理员）
export function getSubscriptionList(params) {
  return request.get('/admin/subscriptions/', { params })
}

// 获取订阅详情
export function getSubscriptionDetail(id) {
  return request.get(`/admin/subscriptions/${id}/`)
}

// 确认配送（增加积分）
export function confirmDelivery(id) {
  return request.post(`/admin/subscriptions/${id}/confirm_delivery/`)
}

// 暂停订阅
export function pauseSubscription(id) {
  return request.post(`/admin/subscriptions/${id}/pause/`)
}

// 恢复订阅
export function resumeSubscription(id) {
  return request.post(`/admin/subscriptions/${id}/resume/`)
}

// 取消订阅
export function cancelSubscription(id) {
  return request.post(`/admin/subscriptions/${id}/cancel/`)
}
