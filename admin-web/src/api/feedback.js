import request from '@/utils/request'

// 获取反馈列表（管理员）
export function getFeedbackList(params) {
  return request.get('/admin/feedbacks/', { params })
}

// 获取反馈详情
export function getFeedbackDetail(id) {
  return request.get(`/admin/feedbacks/${id}/`)
}

// 回复反馈
export function replyFeedback(id, data) {
  return request.post(`/admin/feedbacks/${id}/reply/`, data)
}

// 更新反馈状态
export function updateFeedbackStatus(id, data) {
  return request.post(`/admin/feedbacks/${id}/update_status/`, data)
}
