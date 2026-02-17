import request from '@/utils/request'

// 获取订单列表（管理员）
export function getOrderList(params) {
  return request.get('/admin/orders/', { params })
}

// 获取订单详情
export function getOrderDetail(id) {
  return request.get(`/admin/orders/${id}/`)
}

// 更新订单状态
export function updateOrderStatus(id, data) {
  return request.patch(`/admin/orders/${id}/`, data)
}

// 发货
export function shipOrder(id) {
  return request.post(`/admin/orders/${id}/ship/`)
}

// 确认送达
export function deliverOrder(id) {
  return request.post(`/admin/orders/${id}/deliver/`)
}

// 获取支付记录
export function getPaymentList(params) {
  return request.get('/admin/payments/', { params })
}
