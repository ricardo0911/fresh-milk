import request from '@/utils/request'

// 获取分类列表
export function getCategoryList(params) {
  return request.get('/categories/', { params })
}

// 创建分类
export function createCategory(data) {
  return request.post('/admin/categories/', data)
}

// 更新分类
export function updateCategory(id, data) {
  return request.patch(`/admin/categories/${id}/`, data)
}

// 删除分类
export function deleteCategory(id) {
  return request.delete(`/admin/categories/${id}/`)
}

// 获取产品列表（管理员）
export function getProductList(params) {
  return request.get('/admin/products/', { params })
}

// 获取产品详情（管理员）
export function getProductDetail(id) {
  return request.get(`/admin/products/${id}/`)
}

// 创建产品（管理员）
export function createProduct(data) {
  return request.post('/admin/products/', data)
}

// 更新产品（管理员）
export function updateProduct(id, data) {
  return request.patch(`/admin/products/${id}/`, data)
}

// 删除产品（管理员）
export function deleteProduct(id) {
  return request.delete(`/admin/products/${id}/`)
}
