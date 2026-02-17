<template>
  <div class="subscription-page">
    <div class="page-card">
      <!-- 顶部切换：周期购产品 / 订阅订单 -->
      <el-radio-group v-model="viewMode" style="margin-bottom: 20px;">
        <el-radio-button value="products">周期购产品</el-radio-button>
        <el-radio-button value="orders">订阅订单</el-radio-button>
      </el-radio-group>

      <!-- 周期购产品列表 -->
      <div v-if="viewMode === 'products'">
        <el-table :data="subscriptionProducts" v-loading="productsLoading" stripe>
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="name" label="产品名称" min-width="180" />
          <el-table-column prop="category" label="分类" width="100">
            <template #default="{ row }">
              {{ row.category?.name || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="price" label="价格" width="100">
            <template #default="{ row }">
              ¥{{ row.price }}
            </template>
          </el-table-column>
          <el-table-column prop="specification" label="规格" width="120" />
          <el-table-column prop="stock" label="库存" width="80">
            <template #default="{ row }">
              <el-tag :type="row.stock < 10 ? 'danger' : 'success'">{{ row.stock }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">
                {{ row.is_active ? '上架' : '下架' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button type="danger" link @click="handleRemoveSubscription(row)">
                移除周期购
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!productsLoading && subscriptionProducts.length === 0" description="暂无周期购产品，请在产品管理中开启" />
      </div>

      <!-- 订阅订单列表 -->
      <div v-else>
        <!-- 搜索栏 -->
        <div class="search-form">
          <el-form :inline="true" :model="searchForm">
            <el-form-item label="订阅号">
              <el-input v-model="searchForm.subscription_no" placeholder="请输入订阅号" clearable />
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
          <el-tab-pane label="配送中" name="active" />
          <el-tab-pane label="已暂停" name="paused" />
          <el-tab-pane label="已完成" name="completed" />
          <el-tab-pane label="已取消" name="cancelled" />
        </el-tabs>

        <!-- 表格 -->
        <el-table :data="subscriptionList" v-loading="loading" stripe>
          <el-table-column prop="subscription_no" label="订阅号" width="220" />
          <el-table-column prop="user" label="用户" width="120">
            <template #default="{ row }">
              {{ row.user?.username || row.user?.phone || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="product_name" label="产品" width="180" />
          <el-table-column prop="frequency" label="配送频率" width="100">
            <template #default="{ row }">
              {{ getFrequencyText(row.frequency) }}
            </template>
          </el-table-column>
          <el-table-column label="配送进度" width="120">
            <template #default="{ row }">
              <span :class="{ 'text-success': row.delivered_count === row.total_periods }">
                {{ row.delivered_count }}/{{ row.total_periods }}期
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="period_price" label="每期价格" width="100">
            <template #default="{ row }">
              ¥{{ row.period_price }}
            </template>
          </el-table-column>
          <el-table-column prop="next_delivery_date" label="下次配送" width="120">
            <template #default="{ row }">
              {{ row.next_delivery_date || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180" />
          <el-table-column label="操作" fixed="right" width="280">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleView(row)">
                <el-icon><View /></el-icon>
                详情
              </el-button>
              <el-button
                v-if="row.status === 'active' && row.delivered_count < row.total_periods"
                type="success"
                link
                @click="handleConfirmDelivery(row)"
              >
                <el-icon><Check /></el-icon>
                确认配送
              </el-button>
              <el-button
                v-if="row.status === 'active'"
                type="warning"
                link
                @click="handlePause(row)"
              >
                <el-icon><VideoPause /></el-icon>
                暂停
              </el-button>
              <el-button
                v-if="row.status === 'paused'"
                type="success"
                link
                @click="handleResume(row)"
              >
                <el-icon><VideoPlay /></el-icon>
                恢复
              </el-button>
              <el-button
                v-if="row.status === 'active' || row.status === 'paused'"
                type="danger"
                link
                @click="handleCancel(row)"
              >
                <el-icon><Close /></el-icon>
                取消
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
    </div>

    <!-- 订阅详情弹窗 -->
    <el-dialog v-model="dialogVisible" title="订阅详情" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订阅号">{{ currentSubscription.subscription_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentSubscription.status)">
            {{ getStatusText(currentSubscription.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="用户">{{ currentSubscription.user?.username || currentSubscription.user?.phone }}</el-descriptions-item>
        <el-descriptions-item label="产品">{{ currentSubscription.product_name }}</el-descriptions-item>
        <el-descriptions-item label="配送频率">{{ getFrequencyText(currentSubscription.frequency) }}</el-descriptions-item>
        <el-descriptions-item label="每次数量">{{ currentSubscription.quantity }}</el-descriptions-item>
        <el-descriptions-item label="配送进度">{{ currentSubscription.delivered_count }}/{{ currentSubscription.total_periods }}期</el-descriptions-item>
        <el-descriptions-item label="每期价格">¥{{ currentSubscription.period_price }}</el-descriptions-item>
        <el-descriptions-item label="总价">¥{{ currentSubscription.total_price }}</el-descriptions-item>
        <el-descriptions-item label="开始日期">{{ currentSubscription.start_date }}</el-descriptions-item>
        <el-descriptions-item label="下次配送">{{ currentSubscription.next_delivery_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ currentSubscription.created_at }}</el-descriptions-item>
        <el-descriptions-item label="收货人" :span="2">
          {{ currentSubscription.receiver_name }} {{ currentSubscription.receiver_phone }}
        </el-descriptions-item>
        <el-descriptions-item label="收货地址" :span="2">{{ currentSubscription.receiver_address }}</el-descriptions-item>
      </el-descriptions>

      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
        <el-button
          v-if="currentSubscription.status === 'active' && currentSubscription.delivered_count < currentSubscription.total_periods"
          type="primary"
          @click="handleConfirmDelivery(currentSubscription); dialogVisible = false"
        >
          确认配送
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getSubscriptionList,
  getSubscriptionDetail,
  confirmDelivery,
  pauseSubscription,
  resumeSubscription,
  cancelSubscription
} from '@/api/subscription'
import { getProductList, updateProduct } from '@/api/product'

const loading = ref(false)
const productsLoading = ref(false)
const subscriptionList = ref([])
const subscriptionProducts = ref([])
const dialogVisible = ref(false)
const currentSubscription = ref({})
const activeTab = ref('all')
const viewMode = ref('products')  // 'products' or 'orders'

const searchForm = reactive({
  subscription_no: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const statusOptions = [
  { value: 'active', label: '配送中' },
  { value: 'paused', label: '已暂停' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' }
]

const statusMap = {
  active: { text: '配送中', type: 'success' },
  paused: { text: '已暂停', type: 'warning' },
  completed: { text: '已完成', type: 'info' },
  cancelled: { text: '已取消', type: 'danger' }
}

const frequencyMap = {
  daily: '每天',
  weekly: '每周一次',
  biweekly: '每两周一次',
  monthly: '每月一次'
}

const getStatusText = (status) => statusMap[status]?.text || status
const getStatusType = (status) => statusMap[status]?.type || 'info'
const getFrequencyText = (frequency) => frequencyMap[frequency] || frequency

// 加载周期购产品
const loadSubscriptionProducts = async () => {
  productsLoading.value = true
  try {
    const res = await getProductList({ is_subscription: true, page_size: 100 })
    subscriptionProducts.value = res.results || []
  } catch (error) {
    console.error('Failed to load subscription products:', error)
  } finally {
    productsLoading.value = false
  }
}

// 移除周期购
const handleRemoveSubscription = async (row) => {
  try {
    await ElMessageBox.confirm(`确定将产品 "${row.name}" 从周期购中移除吗？`, '提示', {
      type: 'warning'
    })
    await updateProduct(row.id, { is_subscription: false })
    ElMessage.success('已移除')
    loadSubscriptionProducts()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Remove failed:', error)
    }
  }
}

// 监听视图模式切换
watch(viewMode, (newVal) => {
  if (newVal === 'products') {
    loadSubscriptionProducts()
  } else {
    loadData()
  }
})

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    // 订阅号搜索
    if (searchForm.subscription_no) {
      params.subscription_no = searchForm.subscription_no
    }
    // 状态筛选：优先使用搜索框的状态，其次使用标签页
    if (searchForm.status) {
      params.status = searchForm.status
    } else if (activeTab.value !== 'all') {
      params.status = activeTab.value
    }
    const res = await getSubscriptionList(params)
    subscriptionList.value = res.results || []
    pagination.total = res.count || 0
  } catch (error) {
    console.error('Failed to load subscriptions:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.subscription_no = ''
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
    const res = await getSubscriptionDetail(row.id)
    currentSubscription.value = res
    dialogVisible.value = true
  } catch (error) {
    console.error('Failed to load subscription detail:', error)
  }
}

const handleConfirmDelivery = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确认订阅 "${row.subscription_no}" 第${row.delivered_count + 1}期已配送完成？\n用户将获得 ${parseInt(row.period_price)} 积分奖励`,
      '确认配送',
      { type: 'info' }
    )
    const res = await confirmDelivery(row.id)
    ElMessage.success(`配送确认成功，用户获得 ${res.points_earned} 积分`)
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Confirm delivery failed:', error)
      ElMessage.error(error.response?.data?.error || '操作失败')
    }
  }
}

const handlePause = async (row) => {
  try {
    await ElMessageBox.confirm(`确定暂停订阅 "${row.subscription_no}" 吗？`, '暂停订阅', {
      type: 'warning'
    })
    await pauseSubscription(row.id)
    ElMessage.success('订阅已暂停')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Pause failed:', error)
      ElMessage.error(error.response?.data?.error || '操作失败')
    }
  }
}

const handleResume = async (row) => {
  try {
    await ElMessageBox.confirm(`确定恢复订阅 "${row.subscription_no}" 吗？`, '恢复订阅', {
      type: 'info'
    })
    await resumeSubscription(row.id)
    ElMessage.success('订阅已恢复')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Resume failed:', error)
      ElMessage.error(error.response?.data?.error || '操作失败')
    }
  }
}

const handleCancel = async (row) => {
  try {
    await ElMessageBox.confirm(`确定取消订阅 "${row.subscription_no}" 吗？此操作不可恢复`, '取消订阅', {
      type: 'warning'
    })
    await cancelSubscription(row.id)
    ElMessage.success('订阅已取消')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Cancel failed:', error)
      ElMessage.error(error.response?.data?.error || '操作失败')
    }
  }
}

onMounted(() => {
  // 默认加载周期购产品
  loadSubscriptionProducts()
})
</script>

<style lang="scss" scoped>
.subscription-page {
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

  .text-success {
    color: #67c23a;
    font-weight: bold;
  }
}
</style>
