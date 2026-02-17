<template>
  <div class="comment-page">
    <div class="page-card">
      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card blue">
          <div class="stat-icon">💬</div>
          <div class="stat-content">
            <span class="stat-label">总评价数</span>
            <span class="stat-value">{{ stats.total }}</span>
          </div>
        </div>
        <div class="stat-card green">
          <div class="stat-icon">⭐</div>
          <div class="stat-content">
            <span class="stat-label">平均评分</span>
            <span class="stat-value">{{ stats.avgRating }}</span>
          </div>
        </div>
        <div class="stat-card orange">
          <div class="stat-icon">📝</div>
          <div class="stat-content">
            <span class="stat-label">待回复</span>
            <span class="stat-value">{{ stats.pendingReply }}</span>
          </div>
        </div>
        <div class="stat-card purple">
          <div class="stat-icon">👍</div>
          <div class="stat-content">
            <span class="stat-label">好评率</span>
            <span class="stat-value">{{ stats.goodRate }}%</span>
          </div>
        </div>
      </div>

      <!-- 筛选标签 -->
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="全部评价" name="all" />
        <el-tab-pane name="pending">
          <template #label>
            待回复 <el-badge :value="stats.pendingReply" v-if="stats.pendingReply > 0" class="tab-badge" />
          </template>
        </el-tab-pane>
        <el-tab-pane label="好评(5星)" name="good" />
        <el-tab-pane label="中评(3-4星)" name="medium" />
        <el-tab-pane label="差评(1-2星)" name="bad" />
      </el-tabs>



      <!-- 评价列表 -->
      <div class="reviews-list" v-loading="loading">
        <div v-for="item in commentList" :key="item.id" class="review-card" :class="{ pending: !item.reply }">
          <div class="review-header">
            <div class="review-user">
              <el-avatar :src="item.avatar" :size="40">
                {{ (item.username || '匿名')[0] }}
              </el-avatar>
              <div class="user-info">
                <span class="user-name">{{ item.is_anonymous ? '匿名用户' : (item.username || '用户') }}</span>
                <span class="review-time">{{ formatTime(item.created_at) }}</span>
              </div>
            </div>
            <div class="review-rating">
              <span class="stars">{{ '★'.repeat(item.rating) }}{{ '☆'.repeat(5 - item.rating) }}</span>
              <span class="rating-value">{{ item.rating }}.0</span>
            </div>
            <el-tag v-if="!item.reply" type="warning" size="small" class="pending-badge">待回复</el-tag>
          </div>

          <div class="review-product">
            <el-image :src="getProductImage(item)" fit="cover" style="width: 40px; height: 40px; border-radius: 4px;" />
            <span>{{ item.product_name }}</span>
          </div>

          <div class="review-content">
            <p>{{ item.content }}</p>
            <div class="review-images" v-if="item.images && item.images.length > 0">
              <el-image
                v-for="(img, index) in parseImages(item.images)"
                :key="index"
                :src="img"
                :preview-src-list="parseImages(item.images)"
                fit="cover"
                class="review-image"
              />
            </div>
          </div>

          <!-- 商家回复 -->
          <div class="review-reply" v-if="item.reply">
            <div class="reply-content">
              <span class="reply-label">商家回复：</span>
              {{ item.reply }}
            </div>
            <span class="reply-time">{{ formatTime(item.replied_at) }}</span>
          </div>

          <div class="review-actions">
            <el-button v-if="!item.reply" type="primary" size="small" @click="showReplyDialog(item)">
              回复评价
            </el-button>
            <el-button v-else type="info" size="small" plain @click="showReplyDialog(item)">
              修改回复
            </el-button>
            <el-button type="danger" size="small" plain @click="handleDelete(item)">
              删除
            </el-button>
          </div>
        </div>

        <!-- 空状态 -->
        <el-empty v-if="!loading && commentList.length === 0" description="暂无评价" />
      </div>

      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="pagination.total > 0">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </div>

    <!-- 回复弹窗 -->
    <el-dialog v-model="replyDialogVisible" :title="currentComment.reply ? '修改回复' : '回复评价'" width="500px">
      <div class="reply-preview">
        <div class="preview-user">
          <span class="stars">{{ '★'.repeat(currentComment.rating || 5) }}</span>
          <span>{{ currentComment.is_anonymous ? '匿名用户' : currentComment.username }}</span>
        </div>
        <p class="preview-content">{{ currentComment.content }}</p>
      </div>
      <el-form :model="replyForm">
        <el-form-item label="回复内容" required>
          <el-input
            v-model="replyForm.reply"
            type="textarea"
            :rows="4"
            placeholder="请输入回复内容..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="replyDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="replyLoading" @click="submitReply">
          {{ currentComment.reply ? '修改回复' : '发送回复' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getComments, replyComment, deleteComment } from '@/api/comment'

const loading = ref(false)
const commentList = ref([])
const activeTab = ref('all')
const replyDialogVisible = ref(false)
const replyLoading = ref(false)
const currentComment = ref({})

const stats = reactive({
  total: 0,
  avgRating: '0.0',
  pendingReply: 0,
  goodRate: 0
})



const replyForm = reactive({
  reply: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const formatTime = (time) => {
  if (!time) return ''
  return time.replace('T', ' ').substring(0, 16)
}

const getProductImage = (item) => {
  return item.product_image || '/placeholder.jpg'
}

const parseImages = (images) => {
  if (!images) return []
  let imgList = images
  if (!Array.isArray(images)) {
    try {
      imgList = JSON.parse(images)
    } catch {
      return []
    }
  }
  // 过滤掉无效的本地路径（如 wxfile://、http://tmp 等）
  return imgList.filter(img => {
    if (!img || typeof img !== 'string') return false
    // 只保留有效的 http/https URL
    return img.startsWith('http://') || img.startsWith('https://')
  })
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }

    // 根据标签筛选
    if (activeTab.value === 'pending') {
      params.has_reply = 'false'
    } else if (activeTab.value === 'good') {
      params.rating = '5'
    } else if (activeTab.value === 'medium') {
      params.rating_min = '3'
      params.rating_max = '4'
    } else if (activeTab.value === 'bad') {
      params.rating_max = '2'
    }



    const res = await getComments(params)
    commentList.value = res.results || []
    pagination.total = res.count || 0

    // 计算统计数据
    calculateStats(res)
  } catch (error) {
    console.error('Failed to load comments:', error)
    ElMessage.error('加载评价列表失败')
  } finally {
    loading.value = false
  }
}

const calculateStats = (res) => {
  stats.total = res.count || 0
  // 这些通常应该从后端获取，这里简单处理
  if (commentList.value.length > 0) {
    const ratings = commentList.value.map(c => c.rating)
    const avg = ratings.reduce((a, b) => a + b, 0) / ratings.length
    stats.avgRating = avg.toFixed(1)
    stats.pendingReply = commentList.value.filter(c => !c.reply).length
    stats.goodRate = Math.round((ratings.filter(r => r >= 4).length / ratings.length) * 100)
  }
}



const handleTabChange = () => {
  pagination.page = 1
  loadData()
}

const showReplyDialog = (item) => {
  currentComment.value = item
  replyForm.reply = item.reply || ''
  replyDialogVisible.value = true
}

const submitReply = async () => {
  if (!replyForm.reply.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }

  replyLoading.value = true
  try {
    await replyComment(currentComment.value.id, replyForm.reply)
    ElMessage.success(currentComment.value.reply ? '回复已修改' : '回复成功')
    replyDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('Reply failed:', error)
    ElMessage.error(error.response?.data?.error || '操作失败')
  } finally {
    replyLoading.value = false
  }
}

const handleDelete = async (item) => {
  try {
    await ElMessageBox.confirm('确定要删除这条评价吗？', '删除确认', { type: 'warning' })
    await deleteComment(item.id)
    ElMessage.success('已删除')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete failed:', error)
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.comment-page {
  .page-card {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 20px;
  }

  .stat-card {
    display: flex;
    align-items: center;
    padding: 20px;
    border-radius: 12px;
    background: linear-gradient(135deg, #f5f7fa 0%, #fff 100%);
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);

    &.blue { border-left: 4px solid #409eff; }
    &.green { border-left: 4px solid #67c23a; }
    &.orange { border-left: 4px solid #e6a23c; }
    &.purple { border-left: 4px solid #9b59b6; }

    .stat-icon {
      font-size: 32px;
      margin-right: 16px;
    }

    .stat-content {
      display: flex;
      flex-direction: column;
    }

    .stat-label {
      font-size: 12px;
      color: #909399;
    }

    .stat-value {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
    }
  }

  .search-form {
    margin-bottom: 16px;
  }

  .tab-badge {
    margin-left: 6px;
  }

  .reviews-list {
    min-height: 200px;
  }

  .review-card {
    border: 1px solid #ebeef5;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 16px;
    transition: all 0.3s;

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }

    &.pending {
      border-left: 3px solid #e6a23c;
    }
  }

  .review-header {
    display: flex;
    align-items: center;
    margin-bottom: 12px;

    .review-user {
      display: flex;
      align-items: center;
      flex: 1;

      .user-info {
        margin-left: 12px;
        display: flex;
        flex-direction: column;
      }

      .user-name {
        font-weight: 500;
        color: #303133;
      }

      .review-time {
        font-size: 12px;
        color: #909399;
      }
    }

    .review-rating {
      display: flex;
      align-items: center;
      margin-right: 12px;

      .stars {
        color: #ffc107;
        font-size: 16px;
      }

      .rating-value {
        margin-left: 8px;
        font-weight: 600;
        color: #303133;
      }
    }

    .pending-badge {
      margin-left: 8px;
    }
  }

  .review-product {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px;
    background: #f5f7fa;
    border-radius: 6px;
    margin-bottom: 12px;
    font-size: 14px;
    color: #606266;
  }

  .review-content {
    margin-bottom: 12px;

    p {
      color: #303133;
      line-height: 1.6;
      margin: 0 0 10px 0;
    }
  }

  .review-images {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .review-image {
    width: 80px;
    height: 80px;
    border-radius: 6px;
    cursor: pointer;
  }

  .review-reply {
    background: #f0f9eb;
    border-radius: 6px;
    padding: 12px;
    margin-bottom: 12px;

    .reply-label {
      color: #67c23a;
      font-weight: 500;
    }

    .reply-content {
      color: #606266;
      font-size: 14px;
    }

    .reply-time {
      display: block;
      font-size: 12px;
      color: #909399;
      margin-top: 6px;
    }
  }

  .review-actions {
    display: flex;
    gap: 8px;
  }

  .pagination-wrapper {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }

  .reply-preview {
    background: #f5f7fa;
    border-radius: 6px;
    padding: 12px;
    margin-bottom: 16px;

    .preview-user {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;

      .stars {
        color: #ffc107;
      }
    }

    .preview-content {
      color: #606266;
      margin: 0;
    }
  }
}
</style>
