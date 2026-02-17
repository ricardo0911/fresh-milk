import request from '@/utils/request'

// 获取可用的快递公司列表
export function getExpressCompanies() {
  return request({
    url: '/express/admin/companies/',
    method: 'get'
  })
}

// 快递发货
export function expressShip(orderId, data) {
  return request({
    url: `/express/admin/ship/${orderId}/`,
    method: 'post',
    data
  })
}

// 查询物流轨迹
export function getExpressTrace(orderId) {
  return request({
    url: `/express/admin/trace/${orderId}/`,
    method: 'get'
  })
}

// 获取电子面单图片
export function getExpressWaybill(orderId) {
  return request({
    url: `/express/admin/waybill/${orderId}/`,
    method: 'get'
  })
}

// 预约上门取件
export function bookPickup(orderId, data) {
  return request({
    url: `/express/admin/pickup/${orderId}/`,
    method: 'post',
    data
  })
}

// 取消预约取件
export function cancelPickup(orderId) {
  return request({
    url: `/express/admin/cancel-pickup/${orderId}/`,
    method: 'post'
  })
}

// 查询可预约取件时间段
export function getPickupTimes(company = 'SF') {
  return request({
    url: '/express/admin/pickup-times/',
    method: 'get',
    params: { company }
  })
}

// 取消快递订单
export function cancelExpress(orderId) {
  return request({
    url: `/express/admin/cancel/${orderId}/`,
    method: 'post'
  })
}

// 获取快递订单列表
export function getExpressOrders(params) {
  return request({
    url: '/express/orders/',
    method: 'get',
    params
  })
}

// 获取快递订单详情
export function getExpressOrderDetail(id) {
  return request({
    url: `/express/orders/${id}/`,
    method: 'get'
  })
}
