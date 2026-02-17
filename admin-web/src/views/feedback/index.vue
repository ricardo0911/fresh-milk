<template>
  <div class="feedback-page">
    <div class="page-card">
      <!-- 搜索栏 -->
      <div class="search-form">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="反馈类型">
            <el-select v-model="searchForm.type" placeholder="请选择类型" clearable>
              <el-option
                v-for="item in typeOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="处理状态">
            <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
              <el-option
                v-for="item in statusOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleReset">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 状态标签页 -->
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="待处理" name="pending" />
        <el-tab-pane label="处理中" name="processing" />
        <el-tab-pane label="已解决" name="resolved" />
        <el-tab-pane label="已关闭" name="closed" />
      </el-tabs>

      <!-- 表格 -->
      <el-table :data="feedbackList" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="type_display" label="反馈类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.feedback_type)">
              {{ row.type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="150" show-overflow-tooltip />
        <el-table-column prop="content" label="内容" min-width="200" show-overflow-tooltip />
        <el-table-column prop="contact" label="联系方式" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" width="180" />
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button
              v-if="row.status === 'pending' || row.status === 'processing'"
              type="success"
              link
              @click="handleReply(row)"
            >
              <el-icon><ChatDotRound /></el-icon>
              回复
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </div>

    <!-- 反馈详情弹窗 -->
    <el-dialog v-model="dialogVisible" title="反馈详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="用户">{{ currentFeedback.username }}</el-descriptions-item>
        <el-descriptions-item label="反馈类型">
          <el-tag :type="getTypeTagType(currentFeedback.feedback_type)">
            {{ currentFeedback.type_display }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="联系方式">{{ currentFeedback.contact || '-' }}</el-descriptions-item>
        <el-descriptions-item label="处理状态">
          <el-tag :type="getStatusType(currentFeedback.status)">
            {{ currentFeedback.status_display }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="提交时间" :span="2">{{ currentFeedback.created_at }}</el-descriptions-item>
        <el-descriptions-item label="反馈标题" :span="2">{{ currentFeedback.title }}</el-descriptions-item>
        <el-descriptions-item label="反馈内容" :span="2">
          <div style="white-space: pre-wrap;">{{ currentFeedback.content }}</div>
        </el-descriptions-item>
        <el-descriptions-item v-if="currentFeedback.reply" label="回复内容" :span="2">
          <div style="white-space: pre-wrap; color: #67c23a;">{{ currentFeedback.reply }}</div>
        </el-descriptions-item>
        <el-descriptions-item v-if="currentFeedback.replied_at" label="回复时间" :span="2">
          {{ currentFeedback.replied_at }}
        </el-descriptions-item>
      </el-descriptions>

      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
        <el-button
          v-if="currentFeedback.status === 'pending' || currentFeedback.status === 'processing'"
          type="primary"
          @click="handleReply(currentFeedback); dialogVisible = false"
        >
          回复
        </el-button>
      </template>
    </el-dialog>

    <!-- 回复弹窗 -->
    <el-dialog v-model="replyDialogVisible" title="回复反馈" width="500px">
      <el-form :model="replyForm" label-width="80px">
        <el-form-item label="反馈内容">
          <div style="color: #666; white-space: pre-wrap;">{{ replyForm.content }}</div>
        </el-form-item>
        <el-form-item label="回复内容" required>
          <el-input
            v-model="replyForm.reply"
            type="textarea"
            :rows="4"
            placeholder="请输入回复内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="replyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReply" :loading="submitting">
          提交回复
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getFeedbackList, getFeedbackDetail, replyFeedback } from '@/api/feedback'

const loading = ref(false)
const submitting = ref(false)
const feedbackList = ref([])
const dialogVisible = ref(false)
const replyDialogVisible = ref(false)
const currentFeedback = ref({})
const activeTab = ref('all')

const searchForm = reactive({
  type: '',
  status: ''
})

const replyForm = reactive({
  id: null,
  content: '',
  reply: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const typeOptions = [
  { value: 'suggestion', label: '功能建议' },
  { value: 'complaint', label: '投诉反馈' },
  { value: 'quality', label: '产品质量' },
  { value: 'delivery', label: '配送问题' },
  { value: 'other', label: '其他' }
]

const statusOptions = [
  { value: 'pending', label: '待处理' },
  { value: 'processing', label: '处理中' },
  { value: 'resolved', label: '已解决' },
  { value: 'closed', label: '已关闭' }
]

const typeTagMap = {
  suggestion: '',
  complaint: 'danger',
  quality: 'warning',
  delivery: 'info',
  other: 'info'
}

const statusMap = {
  pending: { text: '待处理', type: 'danger' },
  processing: { text: '处理中', type: 'warning' },
  resolved: { text: '已解决', type: 'success' },
  closed: { text: '已关闭', type: 'info' }
}

const getTypeTagType = (type) => typeTagMap[type] || 'info'
const getStatusType = (status) => statusMap[status]?.type || 'info'

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm
    }
    if (activeTab.value !== 'all') {
      params.status = activeTab.value
    }
    // 清理空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null) {
        delete params[key]
      }
    })
    const res = await getFeedbackList(params)
    feedbackList.value = res.results || res || []
    pagination.total = res.count || feedbackList.value.length
  } catch (error) {
    console.error('Failed to load feedbacks:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.type = ''
  searchForm.status = ''
  activeTab.value = 'all'
  pagination.page = 1
  loadData()
}

const handleTabChange = () => {
  pagination.page = 1
  loadData()
}

const handleView = async (row) => {
  try {
    const res = await getFeedbackDetail(row.id)
    currentFeedback.value = res
    dialogVisible.value = true
  } catch (error) {
    console.error('Failed to load feedback detail:', error)
  }
}

const handleReply = (row) => {
  replyForm.id = row.id
  replyForm.content = row.content
  replyForm.reply = ''
  replyDialogVisible.value = true
}

const submitReply = async () => {
  if (!replyForm.reply.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }

  submitting.value = true
  try {
    await replyFeedback(replyForm.id, { reply: replyForm.reply })
    ElMessage.success('回复成功')
    replyDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('Reply failed:', error)
    ElMessage.error('回复失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.feedback-page {
  .page-card {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
  }

  .search-form {
    margin-bottom: 16px;
  }

  .pagination-wrapper {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
}
</style>
