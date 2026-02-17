<template>
  <div class="refund-page">
    <div class="page-card">
      <!-- 搜索栏 -->
      <div class="search-form">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="退款单号">
            <el-input v-model="searchForm.refund_no" placeholder="请输入退款单号" clearable />
          </el-form-item>
          <el-form-item label="状态">
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
        <el-tab-pane label="已同意" name="approved" />
        <el-tab-pane label="已拒绝" name="rejected" />
        <el-tab-pane label="已完成" name="completed" />
      </el-tabs>

      <!-- 表格 -->
      <el-table :data="refundList" v-loading="loading" stripe>
        <el-table-column prop="refund_no" label="退款单号" width="200" />
        <el-table-column prop="order_no" label="订单号" width="200" />
        <el-table-column label="用户" width="120">
          <template #default="{ row }">
            {{ row.user_info?.nickname || row.user_info?.username || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="退款类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'refund_only' ? 'info' : 'warning'" size="small">
              {{ row.type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reason_display" label="退款原因" width="120" />
        <el-table-column label="退款金额" width="100">
          <template #default="{ row }">
            <span class="amount">¥{{ row.amount }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="180" />
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="success"
              link
              @click="handleApprove(row)"
            >
              <el-icon><Check /></el-icon>
              同意
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="danger"
              link
              @click="handleReject(row)"
            >
              <el-icon><Close /></el-icon>
              拒绝
            </el-button>
            <el-button
              v-if="row.status === 'approved' && row.type === 'return_refund'"
              type="warning"
              link
              @click="handleComplete(row)"
            >
              <el-icon><Finished /></el-icon>
              完成退款
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

    <!-- 退款详情弹窗 -->
    <el-dialog v-model="dialogVisible" title="退款详情" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="退款单号">{{ currentRefund.refund_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentRefund.status)">
            {{ currentRefund.status_display }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="退款类型">{{ currentRefund.type_display }}</el-descriptions-item>
        <el-descriptions-item label="退款金额">
          <span class="amount">¥{{ currentRefund.amount }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="退款原因">{{ currentRefund.reason_display }}</el-descriptions-item>
        <el-descriptions-item label="申请时间">{{ currentRefund.created_at }}</el-descriptions-item>
        <el-descriptions-item label="详细说明" :span="2">{{ currentRefund.description || '-' }}</el-descriptions-item>
      </el-descriptions>

      <!-- 凭证图片 -->
      <div v-if="currentRefund.images" class="images-section">
        <h4>凭证图片</h4>
        <div class="image-list">
          <el-image
            v-for="(img, index) in parseImages(currentRefund.images)"
            :key="index"
            :src="img"
            :preview-src-list="parseImages(currentRefund.images)"
            fit="cover"
            class="evidence-image"
          />
        </div>
      </div>

      <!-- 订单信息 -->
      <div class="order-section">
        <h4>订单信息</h4>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="订单号">{{ currentRefund.order_info?.order_no }}</el-descriptions-item>
          <el-descriptions-item label="实付金额">¥{{ currentRefund.order_info?.pay_amount }}</el-descriptions-item>
        </el-descriptions>
        <el-table :data="currentRefund.order_info?.items || []" border size="small" style="margin-top: 10px;">
          <el-table-column label="商品图片" width="80">
            <template #default="{ row }">
              <el-image :src="row.product_image" fit="cover" style="width: 50px; height: 50px;" />
            </template>
          </el-table-column>
          <el-table-column prop="product_name" label="商品名称" />
          <el-table-column prop="price" label="单价" width="100">
            <template #default="{ row }">¥{{ row.price }}</template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="80" />
        </el-table>
      </div>

      <!-- 用户信息 -->
      <div class="user-section">
        <h4>用户信息</h4>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="用户名">{{ currentRefund.user_info?.username }}</el-descriptions-item>
          <el-descriptions-item label="昵称">{{ currentRefund.user_info?.nickname || '-' }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ currentRefund.user_info?.phone || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 退货信息 -->
      <div v-if="currentRefund.type === 'return_refund' && currentRefund.status !== 'pending'" class="return-section">
        <h4>退货信息</h4>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="退货地址" :span="2">{{ currentRefund.return_address || '-' }}</el-descriptions-item>
          <el-descriptions-item label="退货快递">{{ currentRefund.return_express_company || '-' }}</el-descriptions-item>
          <el-descriptions-item label="快递单号">{{ currentRefund.return_express_no || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 处理信息 -->
      <div v-if="currentRefund.processed_at" class="process-section">
        <h4>处理信息</h4>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="处理时间">{{ currentRefund.processed_at }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ currentRefund.completed_at || '-' }}</el-descriptions-item>
          <el-descriptions-item v-if="currentRefund.admin_remark" label="处理备注" :span="2">{{ currentRefund.admin_remark }}</el-descriptions-item>
          <el-descriptions-item v-if="currentRefund.reject_reason" label="拒绝原因" :span="2">
            <span class="reject-reason">{{ currentRefund.reject_reason }}</span>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
        <el-button
          v-if="currentRefund.status === 'pending'"
          type="success"
          @click="handleApprove(currentRefund); dialogVisible = false"
        >
          同意退款
        </el-button>
        <el-button
          v-if="currentRefund.status === 'pending'"
          type="danger"
          @click="handleReject(currentRefund); dialogVisible = false"
        >
          拒绝退款
        </el-button>
        <el-button
          v-if="currentRefund.status === 'approved' && currentRefund.type === 'return_refund'"
          type="warning"
          @click="handleComplete(currentRefund); dialogVisible = false"
        >
          完成退款
        </el-button>
      </template>
    </el-dialog>

    <!-- 同意退款弹窗 -->
    <el-dialog v-model="approveDialogVisible" title="同意退款" width="500px">
      <el-form :model="approveForm" label-width="100px">
        <el-form-item label="退款单号">
          <span>{{ approveForm.refund_no }}</span>
        </el-form-item>
        <el-form-item label="退款金额">
          <span class="amount">¥{{ approveForm.amount }}</span>
        </el-form-item>
        <el-form-item v-if="approveForm.type === 'return_refund'" label="退货地址" required>
          <el-input v-model="approveForm.return_address" placeholder="请输入退货地址" />
        </el-form-item>
        <el-form-item label="处理备注">
          <el-input v-model="approveForm.admin_remark" type="textarea" placeholder="处理备注（选填）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="approveDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="approveLoading" @click="confirmApprove">
          确认同意
        </el-button>
      </template>
    </el-dialog>

    <!-- 拒绝退款弹窗 -->
    <el-dialog v-model="rejectDialogVisible" title="拒绝退款" width="500px">
      <el-form :model="rejectForm" label-width="100px">
        <el-form-item label="退款单号">
          <span>{{ rejectForm.refund_no }}</span>
        </el-form-item>
        <el-form-item label="拒绝原因" required>
          <el-input v-model="rejectForm.reject_reason" type="textarea" placeholder="请输入拒绝原因" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" :loading="rejectLoading" @click="confirmReject">
          确认拒绝
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRefundList, getRefundDetail, approveRefund, rejectRefund, completeRefund } from '@/api/refund'

const loading = ref(false)
const refundList = ref([])
const dialogVisible = ref(false)
const currentRefund = ref({})
const activeTab = ref('all')

// 同意退款相关
const approveDialogVisible = ref(false)
const approveLoading = ref(false)
const approveForm = reactive({
  id: '',
  refund_no: '',
  amount: '',
  type: '',
  return_address: '',
  admin_remark: ''
})

// 拒绝退款相关
const rejectDialogVisible = ref(false)
const rejectLoading = ref(false)
const rejectForm = reactive({
  id: '',
  refund_no: '',
  reject_reason: ''
})

const searchForm = reactive({
  refund_no: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const statusOptions = [
  { value: 'pending', label: '待处理' },
  { value: 'approved', label: '已同意' },
  { value: 'rejected', label: '已拒绝' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' }
]

const getStatusType = (status) => {
  const map = {
    pending: 'warning',
    approved: '',
    rejected: 'danger',
    completed: 'success',
    cancelled: 'info'
  }
  return map[status] || 'info'
}

const parseImages = (images) => {
  if (!images) return []
  try {
    return JSON.parse(images)
  } catch {
    return images.split(',').filter(Boolean)
  }
}

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
    const res = await getRefundList(params)
    refundList.value = res.results || []
    pagination.total = res.count || 0
  } catch (error) {
    console.error('Failed to load refunds:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  activeTab.value = 'all'  // 搜索时切换到全部标签，避免状态被覆盖
  loadData()
}

const handleReset = () => {
  searchForm.refund_no = ''
  searchForm.status = ''
  activeTab.value = 'all'
  pagination.page = 1
  loadData()
}

const handleTabChange = () => {
  searchForm.status = ''  // 切换标签时清空搜索表单的状态选择
  pagination.page = 1
  loadData()
}

const handleView = async (row) => {
  try {
    const res = await getRefundDetail(row.id)
    currentRefund.value = res
    dialogVisible.value = true
  } catch (error) {
    console.error('Failed to load refund detail:', error)
  }
}

const handleApprove = (row) => {
  approveForm.id = row.id
  approveForm.refund_no = row.refund_no
  approveForm.amount = row.amount
  approveForm.type = row.type
  approveForm.return_address = ''
  approveForm.admin_remark = ''
  approveDialogVisible.value = true
}

const confirmApprove = async () => {
  if (approveForm.type === 'return_refund' && !approveForm.return_address) {
    ElMessage.warning('请填写退货地址')
    return
  }

  approveLoading.value = true
  try {
    await approveRefund(approveForm.id, {
      return_address: approveForm.return_address,
      admin_remark: approveForm.admin_remark
    })
    ElMessage.success('已同意退款申请')
    approveDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('Approve failed:', error)
    ElMessage.error(error.response?.data?.error || '操作失败')
  } finally {
    approveLoading.value = false
  }
}

const handleReject = (row) => {
  rejectForm.id = row.id
  rejectForm.refund_no = row.refund_no
  rejectForm.reject_reason = ''
  rejectDialogVisible.value = true
}

const confirmReject = async () => {
  if (!rejectForm.reject_reason) {
    ElMessage.warning('请填写拒绝原因')
    return
  }

  rejectLoading.value = true
  try {
    await rejectRefund(rejectForm.id, {
      reject_reason: rejectForm.reject_reason
    })
    ElMessage.success('已拒绝退款申请')
    rejectDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('Reject failed:', error)
    ElMessage.error(error.response?.data?.error || '操作失败')
  } finally {
    rejectLoading.value = false
  }
}

const handleComplete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定已收到退货并完成退款吗？退款金额：¥${row.amount}`,
      '完成退款',
      { type: 'warning' }
    )
    await completeRefund(row.id)
    ElMessage.success('退款已完成')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Complete failed:', error)
      ElMessage.error(error.response?.data?.error || '操作失败')
    }
  }
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.refund-page {
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

  .amount {
    color: #f56c6c;
    font-weight: bold;
  }

  .images-section,
  .order-section,
  .user-section,
  .return-section,
  .process-section {
    margin-top: 20px;

    h4 {
      margin-bottom: 10px;
      color: #303133;
      font-size: 14px;
    }
  }

  .image-list {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }

  .evidence-image {
    width: 100px;
    height: 100px;
    border-radius: 4px;
    cursor: pointer;
  }

  .reject-reason {
    color: #f56c6c;
  }
}
</style>
