import request from '@/utils/request'

// 获取退款申请列表
export function getRefundList(params) {
  return request.get('/admin/refunds/', { params })
}

// 获取退款申请详情
export function getRefundDetail(id) {
  return request.get(`/admin/refunds/${id}/`)
}

// 同意退款
export function approveRefund(id, data) {
  return request.post(`/admin/refunds/${id}/approve/`, data)
}

// 拒绝退款
export function rejectRefund(id, data) {
  return request.post(`/admin/refunds/${id}/reject/`, data)
}

// 完成退款（确认收到退货）
export function completeRefund(id) {
  return request.post(`/admin/refunds/${id}/complete/`)
}
