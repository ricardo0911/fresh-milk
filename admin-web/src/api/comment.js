/**
 * 评论管理 API
 */
import request from '@/utils/request'

// 获取评论列表
export function getComments(params) {
    return request({
        url: '/admin/comments/',
        method: 'get',
        params
    })
}

// 获取评论详情
export function getComment(id) {
    return request({
        url: `/admin/comments/${id}/`,
        method: 'get'
    })
}

// 回复评论
export function replyComment(id, reply) {
    return request({
        url: `/admin/comments/${id}/reply/`,
        method: 'post',
        data: { reply }
    })
}

// 审核通过
export function approveComment(id) {
    return request({
        url: `/admin/comments/${id}/approve/`,
        method: 'post'
    })
}

// 审核拒绝
export function rejectComment(id) {
    return request({
        url: `/admin/comments/${id}/reject/`,
        method: 'post'
    })
}

// 删除评论
export function deleteComment(id) {
    return request({
        url: `/admin/comments/${id}/`,
        method: 'delete'
    })
}

// 获取评论统计
export function getCommentStats() {
    return request({
        url: '/admin/comments/stats/',
        method: 'get'
    })
}
