<template>
  <div class="order-page">
    <div class="page-card">
      <!-- 搜索栏 -->
      <div class="search-form">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="订单号">
            <el-input v-model="searchForm.order_no" placeholder="请输入订单号" clearable />
          </el-form-item>
          <el-form-item label="订单状态">
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
        <el-tab-pane label="待支付" name="pending" />
        <el-tab-pane label="待发货" name="paid" />
        <el-tab-pane label="已发货" name="shipped" />
        <el-tab-pane label="已送达" name="delivered" />
        <el-tab-pane label="已完成" name="completed" />
        <el-tab-pane label="已取消" name="cancelled" />
      </el-tabs>

      <!-- 表格 -->
      <el-table :data="orderList" v-loading="loading" stripe>
        <el-table-column prop="order_no" label="订单号" width="200" />
        <el-table-column prop="user" label="用户" width="120">
          <template #default="{ row }">
            {{ row.user?.nickname || row.user?.username || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="订单金额" width="100">
          <template #default="{ row }">
            ¥{{ row.total_amount }}
          </template>
        </el-table-column>
        <el-table-column prop="pay_amount" label="实付金额" width="100">
          <template #default="{ row }">
            ¥{{ row.pay_amount }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="express_company" label="快递" width="100">
          <template #default="{ row }">
            <span v-if="row.express_no">
              {{ getExpressName(row.express_company) }}
            </span>
            <span v-else class="text-gray">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="receiver_name" label="收货人" width="100" />
        <el-table-column prop="receiver_phone" label="联系电话" width="120" />
        <el-table-column prop="created_at" label="下单时间" width="180" />
        <el-table-column label="操作" fixed="right" width="320">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button
              v-if="row.status === 'paid'"
              type="success"
              link
              @click="handleShip(row)"
            >
              <el-icon><Van /></el-icon>
              发货
            </el-button>
            <el-button
              v-if="row.express_no"
              type="info"
              link
              @click="handleViewTrace(row)"
            >
              <el-icon><Location /></el-icon>
              物流
            </el-button>
            <el-dropdown v-if="row.express_no" trigger="click" @command="(cmd) => handleExpressAction(cmd, row)">
              <el-button type="warning" link>
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="print">打印面单</el-dropdown-item>
                  <el-dropdown-item command="pickup">预约取件</el-dropdown-item>
                  <el-dropdown-item command="cancel" divided>取消快递</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button
              v-if="row.status === 'shipped'"
              type="warning"
              link
              @click="handleDeliver(row)"
            >
              <el-icon><Check /></el-icon>
              送达
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

    <!-- 订单详情弹窗 -->
    <el-dialog v-model="dialogVisible" title="订单详情" width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">{{ currentOrder.order_no }}</el-descriptions-item>
        <el-descriptions-item label="订单状态">
          <el-tag :type="getStatusType(currentOrder.status)">
            {{ getStatusText(currentOrder.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="用户">{{ currentOrder.user?.username }}</el-descriptions-item>
        <el-descriptions-item label="下单时间">{{ currentOrder.created_at }}</el-descriptions-item>
        <el-descriptions-item label="订单金额">¥{{ currentOrder.total_amount }}</el-descriptions-item>
        <el-descriptions-item label="实付金额">¥{{ currentOrder.pay_amount }}</el-descriptions-item>
        <el-descriptions-item label="收货人">{{ currentOrder.receiver_name }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ currentOrder.receiver_phone }}</el-descriptions-item>
        <el-descriptions-item label="收货地址" :span="2">{{ currentOrder.receiver_address }}</el-descriptions-item>
        <el-descriptions-item label="订单备注" :span="2">{{ currentOrder.remark || '-' }}</el-descriptions-item>
      </el-descriptions>

      <!-- 物流信息 -->
      <div v-if="currentOrder.express_no" class="express-info">
        <h4>物流信息</h4>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="快递公司">{{ getExpressName(currentOrder.express_company) }}</el-descriptions-item>
          <el-descriptions-item label="快递单号">
            {{ currentOrder.express_no }}
            <el-button type="primary" link size="small" @click="handleViewTrace(currentOrder)">
              查看物流
            </el-button>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <h4 style="margin: 20px 0 10px;">订单商品</h4>
      <el-table :data="currentOrder.items || []" border>
        <el-table-column prop="product_name" label="商品名称" />
        <el-table-column prop="price" label="单价" width="100">
          <template #default="{ row }">
            ¥{{ row.price }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="total_price" label="小计" width="100">
          <template #default="{ row }">
            ¥{{ row.total_price }}
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
        <el-button
          v-if="currentOrder.status === 'paid'"
          type="primary"
          @click="handleShip(currentOrder); dialogVisible = false"
        >
          发货
        </el-button>
      </template>
    </el-dialog>

    <!-- 快递发货弹窗 -->
    <el-dialog v-model="shipDialogVisible" title="快递发货" width="500px">
      <el-form :model="shipForm" label-width="100px">
        <el-form-item label="订单号">
          <span>{{ shipForm.order_no }}</span>
        </el-form-item>
        <el-form-item label="收货人">
          <span>{{ shipForm.receiver_name }} {{ shipForm.receiver_phone }}</span>
        </el-form-item>
        <el-form-item label="收货地址">
          <span>{{ shipForm.receiver_address }}</span>
        </el-form-item>
        <el-form-item label="快递公司" required>
          <el-select v-model="shipForm.express_company_code" placeholder="请选择快递公司" style="width: 100%">
            <el-option
              v-for="item in expressCompanies"
              :key="item.code"
              :label="item.name"
              :value="item.code"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="shipForm.remark" type="textarea" placeholder="发货备注（选填）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="shipDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="shipLoading" @click="confirmShip">
          确认发货
        </el-button>
      </template>
    </el-dialog>

    <!-- 物流轨迹弹窗 -->
    <el-dialog v-model="traceDialogVisible" title="物流轨迹" width="600px">
      <div class="trace-header">
        <p><strong>快递公司：</strong>{{ getExpressName(traceInfo.express_company) }}</p>
        <p><strong>快递单号：</strong>{{ traceInfo.express_no }}</p>
        <p><strong>物流状态：</strong>
          <el-tag :type="getExpressStatusType(traceInfo.status)">
            {{ getExpressStatusText(traceInfo.status) }}
          </el-tag>
        </p>
      </div>
      <el-divider />
      <div v-if="traceInfo.traces && traceInfo.traces.length > 0" class="trace-timeline">
        <el-timeline>
          <el-timeline-item
            v-for="(trace, index) in traceInfo.traces"
            :key="index"
            :timestamp="trace.time"
            :type="index === 0 ? 'primary' : ''"
          >
            <p>{{ trace.description }}</p>
            <p v-if="trace.location" class="trace-location">{{ trace.location }}</p>
          </el-timeline-item>
        </el-timeline>
      </div>
      <el-empty v-else description="暂无物流信息" />
    </el-dialog>

    <!-- 打印面单弹窗 -->
    <el-dialog v-model="waybillDialogVisible" title="电子面单" width="500px">
      <div v-if="waybillLoading" class="waybill-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <p>正在获取面单...</p>
      </div>
      <div v-else-if="waybillImage" class="waybill-container">
        <img :src="'data:image/png;base64,' + waybillImage" alt="电子面单" class="waybill-image" />
        <div class="waybill-actions">
          <el-button type="primary" @click="printWaybill">
            <el-icon><Printer /></el-icon>
            打印面单
          </el-button>
          <el-button @click="downloadWaybill">
            <el-icon><Download /></el-icon>
            下载图片
          </el-button>
        </div>
      </div>
      <el-empty v-else description="获取面单失败" />
    </el-dialog>

    <!-- 预约取件弹窗 -->
    <el-dialog v-model="pickupDialogVisible" title="预约上门取件" width="500px">
      <el-form :model="pickupForm" label-width="100px">
        <el-form-item label="快递单号">
          <span>{{ pickupForm.express_no }}</span>
        </el-form-item>
        <el-form-item label="取件时间" required>
          <el-date-picker
            v-model="pickupForm.pickup_time"
            type="datetime"
            placeholder="选择取件时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            :disabled-date="disabledDate"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="pickupForm.remark" type="textarea" placeholder="取件备注（选填）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pickupDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="pickupLoading" @click="confirmPickup">
          确认预约
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getOrderList, getOrderDetail, deliverOrder } from '@/api/order'
import { getExpressCompanies, expressShip, getExpressTrace, getExpressWaybill, bookPickup, cancelExpress } from '@/api/express'

const route = useRoute()

const loading = ref(false)
const orderList = ref([])
const dialogVisible = ref(false)
const currentOrder = ref({})
const activeTab = ref('all')

// 快递发货相关
const shipDialogVisible = ref(false)
const shipLoading = ref(false)
const expressCompanies = ref([])
const shipForm = reactive({
  order_id: '',
  order_no: '',
  receiver_name: '',
  receiver_phone: '',
  receiver_address: '',
  express_company_code: '',
  remark: ''
})

// 物流轨迹相关
const traceDialogVisible = ref(false)
const traceInfo = ref({})

// 面单打印相关
const waybillDialogVisible = ref(false)
const waybillLoading = ref(false)
const waybillImage = ref('')
const currentWaybillOrder = ref(null)

// 预约取件相关
const pickupDialogVisible = ref(false)
const pickupLoading = ref(false)
const pickupForm = reactive({
  order_id: '',
  express_no: '',
  pickup_time: '',
  remark: ''
})

const searchForm = reactive({
  order_no: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const statusOptions = [
  { value: 'pending', label: '待支付' },
  { value: 'paid', label: '待发货' },
  { value: 'shipped', label: '已发货' },
  { value: 'delivered', label: '已送达' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' },
  { value: 'refunding', label: '退款中' },
  { value: 'refunded', label: '已退款' }
]

const statusMap = {
  pending: { text: '待支付', type: 'info' },
  paid: { text: '待发货', type: 'warning' },
  shipped: { text: '已发货', type: '' },
  delivered: { text: '已送达', type: 'success' },
  completed: { text: '已完成', type: 'success' },
  cancelled: { text: '已取消', type: 'danger' },
  refunding: { text: '退款中', type: 'warning' },
  refunded: { text: '已退款', type: 'info' }
}

const expressNameMap = {
  SF: '顺丰速运',
  YTO: '圆通速递',
  ZTO: '中通快递',
  YD: '韵达快递',
  JTSD: '极兔速递'
}

const expressStatusMap = {
  created: { text: '已下单', type: 'info' },
  collected: { text: '已揽收', type: '' },
  in_transit: { text: '运输中', type: '' },
  delivering: { text: '派送中', type: 'warning' },
  signed: { text: '已签收', type: 'success' },
  failed: { text: '签收失败', type: 'danger' },
  cancelled: { text: '已取消', type: 'info' }
}

const getStatusText = (status) => statusMap[status]?.text || status
const getStatusType = (status) => statusMap[status]?.type || 'info'
const getExpressName = (code) => expressNameMap[code] || code || '-'
const getExpressStatusText = (status) => expressStatusMap[status]?.text || status
const getExpressStatusType = (status) => expressStatusMap[status]?.type || 'info'

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
    const res = await getOrderList(params)
    orderList.value = res.results || []
    pagination.total = res.count || 0
  } catch (error) {
    console.error('Failed to load orders:', error)
  } finally {
    loading.value = false
  }
}

const loadExpressCompanies = async () => {
  try {
    const res = await getExpressCompanies()
    expressCompanies.value = res || []
  } catch (error) {
    console.error('Failed to load express companies:', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.order_no = ''
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
    const res = await getOrderDetail(row.id)
    currentOrder.value = res
    dialogVisible.value = true
  } catch (error) {
    console.error('Failed to load order detail:', error)
  }
}

const handleShip = async (row) => {
  // 加载快递公司列表
  if (expressCompanies.value.length === 0) {
    await loadExpressCompanies()
  }

  // 填充发货表单
  shipForm.order_id = row.id
  shipForm.order_no = row.order_no
  shipForm.receiver_name = row.receiver_name
  shipForm.receiver_phone = row.receiver_phone
  shipForm.receiver_address = row.receiver_address
  shipForm.express_company_code = expressCompanies.value[0]?.code || ''
  shipForm.remark = ''

  shipDialogVisible.value = true
}

const confirmShip = async () => {
  if (!shipForm.express_company_code) {
    ElMessage.warning('请选择快递公司')
    return
  }

  shipLoading.value = true
  try {
    await expressShip(shipForm.order_id, {
      express_company_code: shipForm.express_company_code,
      remark: shipForm.remark
    })
    ElMessage.success('发货成功')
    shipDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('Ship failed:', error)
    ElMessage.error(error.response?.data?.error || '发货失败')
  } finally {
    shipLoading.value = false
  }
}

const handleViewTrace = async (row) => {
  try {
    const res = await getExpressTrace(row.id)
    traceInfo.value = res
    traceDialogVisible.value = true
  } catch (error) {
    console.error('Failed to load trace:', error)
    ElMessage.error(error.response?.data?.error || '获取物流信息失败')
  }
}

const handleDeliver = async (row) => {
  try {
    await ElMessageBox.confirm(`确定订单 "${row.order_no}" 已送达吗？`, '提示', {
      type: 'warning'
    })
    await deliverOrder(row.id)
    ElMessage.success('已确认送达')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Deliver failed:', error)
    }
  }
}

// 快递操作下拉菜单
const handleExpressAction = (command, row) => {
  switch (command) {
    case 'print':
      handlePrintWaybill(row)
      break
    case 'pickup':
      handleBookPickup(row)
      break
    case 'cancel':
      handleCancelExpress(row)
      break
  }
}

// 打印面单
const handlePrintWaybill = async (row) => {
  waybillLoading.value = true
  waybillImage.value = ''
  currentWaybillOrder.value = row
  waybillDialogVisible.value = true

  try {
    const res = await getExpressWaybill(row.id)
    waybillImage.value = res.image_data
  } catch (error) {
    console.error('Failed to get waybill:', error)
    ElMessage.error(error.response?.data?.error || '获取面单失败')
  } finally {
    waybillLoading.value = false
  }
}

// 打印面单
const printWaybill = () => {
  const printWindow = window.open('', '_blank')
  const htmlContent = [
    '<html>',
    '<head>',
    '<title>快递面单 - ' + (currentWaybillOrder.value?.express_no || '') + '</title>',
    '<style>body { margin: 0; display: flex; justify-content: center; align-items: center; } img { max-width: 100%; height: auto; }</style>',
    '</head>',
    '<body>',
    '<img src="data:image/png;base64,' + waybillImage.value + '" />',
    '<scr' + 'ipt>window.onload = function() { window.print(); }<\/scr' + 'ipt>',
    '</body>',
    '</html>'
  ].join('')
  printWindow.document.write(htmlContent)
  printWindow.document.close()
}

// 下载面单
const downloadWaybill = () => {
  const link = document.createElement('a')
  link.href = 'data:image/png;base64,' + waybillImage.value
  link.download = `waybill_${currentWaybillOrder.value?.express_no}.png`
  link.click()
}

// 预约取件
const handleBookPickup = (row) => {
  pickupForm.order_id = row.id
  pickupForm.express_no = row.express_no
  pickupForm.pickup_time = ''
  pickupForm.remark = ''
  pickupDialogVisible.value = true
}

// 禁用过去的日期
const disabledDate = (time) => {
  return time.getTime() < Date.now() - 8.64e7
}

// 确认预约取件
const confirmPickup = async () => {
  if (!pickupForm.pickup_time) {
    ElMessage.warning('请选择取件时间')
    return
  }

  pickupLoading.value = true
  try {
    const res = await bookPickup(pickupForm.order_id, {
      pickup_time: pickupForm.pickup_time,
      remark: pickupForm.remark
    })
    ElMessage.success(res.message || '预约成功')
    pickupDialogVisible.value = false
  } catch (error) {
    console.error('Pickup failed:', error)
    ElMessage.error(error.response?.data?.error || '预约失败')
  } finally {
    pickupLoading.value = false
  }
}

// 取消快递
const handleCancelExpress = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要取消订单 "${row.order_no}" 的快递吗？`, '取消快递', {
      type: 'warning'
    })
    await cancelExpress(row.id)
    ElMessage.success('取消成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Cancel express failed:', error)
      ElMessage.error(error.response?.data?.error || '取消失败')
    }
  }
}

onMounted(() => {
  // 检查URL参数
  if (route.query.status) {
    activeTab.value = route.query.status
  }
  loadData()
  loadExpressCompanies()
})
</script>

<style lang="scss" scoped>
.order-page {
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

  .text-gray {
    color: #999;
  }

  .express-info {
    margin-top: 20px;

    h4 {
      margin-bottom: 10px;
    }
  }

  .trace-header {
    p {
      margin: 8px 0;
    }
  }

  .trace-timeline {
    max-height: 400px;
    overflow-y: auto;
  }

  .trace-location {
    color: #999;
    font-size: 12px;
    margin-top: 4px;
  }

  .waybill-loading {
    text-align: center;
    padding: 40px;

    .is-loading {
      font-size: 32px;
      color: #409eff;
      animation: rotating 2s linear infinite;
    }

    p {
      margin-top: 16px;
      color: #666;
    }
  }

  .waybill-container {
    text-align: center;

    .waybill-image {
      max-width: 100%;
      border: 1px solid #eee;
      border-radius: 4px;
    }

    .waybill-actions {
      margin-top: 20px;
      display: flex;
      justify-content: center;
      gap: 16px;
    }
  }
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
