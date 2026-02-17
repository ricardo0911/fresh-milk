import request from '@/utils/request'

// 获取优惠券列表
export function getCouponList(params) {
    return request.get('/coupons/', { params })
}

// 获取优惠券详情
export function getCouponDetail(id) {
    return request.get(`/coupons/${id}/`)
}

// 创建优惠券
export function createCoupon(data) {
    return request.post('/coupons/', data)
}

// 更新优惠券
export function updateCoupon(id, data) {
    return request.patch(`/coupons/${id}/`, data)
}

// 删除优惠券
export function deleteCoupon(id) {
    return request.delete(`/coupons/${id}/`)
}

// 发放优惠券给用户
export function grantCoupon(id, userIds) {
    return request.post(`/coupons/${id}/grant/`, { user_ids: userIds })
}
