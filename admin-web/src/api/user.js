import request from '@/utils/request'

// 登录
export function login(data) {
  return request.post('/auth/login/', data)
}

// 获取当前用户信息
export function getUserInfo() {
  return request.get('/users/me/')
}

// 获取用户列表（管理员）
export function getUserList(params) {
  return request.get('/admin/users/', { params })
}

// 获取用户详情
export function getUserDetail(id) {
  return request.get(`/admin/users/${id}/`)
}

// 更新用户
export function updateUser(id, data) {
  return request.patch(`/admin/users/${id}/`, data)
}

// 删除用户
export function deleteUser(id) {
  return request.delete(`/admin/users/${id}/`)
}

// 切换用户状态
export function toggleUserActive(id) {
  return request.post(`/admin/users/${id}/toggle_active/`)
}

// 调整用户积分
export function adjustUserPoints(id, data) {
  return request.post(`/admin/users/${id}/adjust_points/`, data)
}

// 获取用户积分记录
export function getUserPointsRecords(id) {
  return request.get(`/admin/users/${id}/points_records/`)
}

// 获取用户日志
export function getUserLogs(params) {
  return request.get('/admin/logs/', { params })
}
