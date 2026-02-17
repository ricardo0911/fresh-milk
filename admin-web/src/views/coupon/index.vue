<template>
  <div class="coupon-page">
    <div class="page-card">
      <!-- 工具栏 -->
      <div class="table-toolbar">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增优惠券
        </el-button>
        <div class="search-bar">
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="loadData" style="width: 120px; margin-right: 10px">
            <el-option label="进行中" value="active" />
            <el-option label="已结束" value="expired" />
            <el-option label="已停用" value="inactive" />
          </el-select>
        </div>
      </div>

      <!-- 表格 -->
      <el-table :data="couponList" v-loading="loading" stripe>
        <el-table-column prop="name" label="优惠券名称" min-width="150" />
        <el-table-column prop="type_display" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'discount' ? 'warning' : 'success'">
              {{ row.type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="优惠内容" width="120">
          <template #default="{ row }">
            <span v-if="row.type === 'amount'">减 ¥{{ row.discount_amount }}</span>
            <span v-else>{{ row.discount_percent }}折</span>
          </template>
        </el-table-column>
        <el-table-column label="使用门槛" width="100">
          <template #default="{ row }">
            <span v-if="row.min_amount > 0">满 ¥{{ row.min_amount }}</span>
            <span v-else>无门槛</span>
          </template>
        </el-table-column>
        <el-table-column label="积分兑换" width="120">
          <template #default="{ row }">
            <template v-if="row.is_exchangeable">
              <span class="points-value">{{ row.points_required }}积分</span>
            </template>
            <span v-else class="text-muted">不可兑换</span>
          </template>
        </el-table-column>
        <el-table-column label="有效期" width="280">
          <template #default="{ row }">
            {{ formatTime(row.start_time) }} 至 {{ formatTime(row.end_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_count" label="发行量" width="80">
           <template #default="{ row }">
             <span v-if="row.total_count === 0">不限</span>
             <span v-else>{{ row.total_count }}</span>
           </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button type="success" link @click="handleGrant(row)">
              发放
            </el-button>
            <el-button type="primary" link @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              删除
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
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑优惠券' : '新增优惠券'"
      width="650px"
      @close="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入优惠券名称" />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-radio-group v-model="form.type">
            <el-radio value="amount">满减券</el-radio>
            <el-radio value="discount">折扣券</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="form.type === 'amount'" label="减免金额" prop="discount_amount">
          <el-input-number v-model="form.discount_amount" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item v-else label="折扣" prop="discount_percent">
          <el-input-number v-model="form.discount_percent" :min="1" :max="99" :precision="0" />
           <span style="margin-left: 10px; color: #999">% (如95表示95折)</span>
        </el-form-item>

        <el-form-item label="最低消费" prop="min_amount">
          <el-input-number v-model="form.min_amount" :min="0" :precision="2" />
        </el-form-item>

        <el-form-item label="发行总量" prop="total_count">
          <el-input-number v-model="form.total_count" :min="0" placeholder="0为不限" />
          <span style="margin-left: 10px; color: #999">0表示不限制</span>
        </el-form-item>

        <el-form-item label="每人限领" prop="per_user_limit">
          <el-input-number v-model="form.per_user_limit" :min="1" />
        </el-form-item>

        <el-divider content-position="left">积分兑换设置</el-divider>

        <el-form-item label="积分兑换">
          <el-switch v-model="form.is_exchangeable" active-text="开启" inactive-text="关闭" />
        </el-form-item>

        <template v-if="form.is_exchangeable">
          <el-form-item label="所需积分" prop="points_required">
            <el-input-number v-model="form.points_required" :min="1" :max="100000" />
            <span style="margin-left: 10px; color: #999">兑换此券需要的积分</span>
          </el-form-item>
          <el-form-item label="兑换限量" prop="exchange_limit">
            <el-input-number v-model="form.exchange_limit" :min="0" />
            <span style="margin-left: 10px; color: #999">0表示不限制</span>
          </el-form-item>
        </template>

        <el-divider />

        <el-form-item label="有效期" prop="dateRange">
          <el-date-picker
            v-model="form.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio value="active">进行中</el-radio>
            <el-radio value="inactive">已停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 发放优惠券弹窗 -->
    <el-dialog v-model="grantDialogVisible" title="发放优惠券" width="600px">
      <div class="grant-info">
        <p>优惠券: <strong>{{ currentCoupon?.name }}</strong></p>
        <p>每人限领: {{ currentCoupon?.per_user_limit }} 张</p>
      </div>
      <el-form label-width="80px">
        <el-form-item label="选择用户">
          <el-select
            v-model="selectedUserIds"
            multiple
            filterable
            remote
            reserve-keyword
            placeholder="搜索用户手机号或昵称"
            :remote-method="searchUsers"
            :loading="userLoading"
            style="width: 100%"
          >
            <el-option
              v-for="user in userList"
              :key="user.id"
              :label="`${user.nickname || user.username} (${user.phone})`"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="grantDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="granting" @click="submitGrant">确认发放</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCouponList, createCoupon, updateCoupon, deleteCoupon, grantCoupon } from '@/api/coupon'
import { getUserList } from '@/api/user'
import dayjs from 'dayjs'

const loading = ref(false)
const couponList = ref([])
const statusFilter = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)

// 发放相关
const grantDialogVisible = ref(false)
const currentCoupon = ref(null)
const selectedUserIds = ref([])
const userList = ref([])
const userLoading = ref(false)
const granting = ref(false)

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const form = reactive({
  id: null,
  name: '',
  type: 'amount',
  discount_amount: 0,
  discount_percent: 95,
  min_amount: 0,
  total_count: 0,
  per_user_limit: 1,
  dateRange: [],
  description: '',
  status: 'active',
  // 积分兑换
  is_exchangeable: false,
  points_required: 100,
  exchange_limit: 0
})

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  dateRange: [{ required: true, message: '请选择有效期', trigger: 'change' }]
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

const getStatusType = (status) => {
  const map = {
    active: 'success',
    inactive: 'info',
    expired: 'danger'
  }
  return map[status] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      status: statusFilter.value || undefined
    }
    const res = await getCouponList(params)
    couponList.value = res.results || []
    pagination.total = res.count || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, row)
  form.dateRange = [row.start_time, row.end_time]
  // 确保数字类型正确
  form.discount_amount = Number(row.discount_amount)
  form.discount_percent = Number(row.discount_percent)
  form.points_required = Number(row.points_required) || 100
  form.exchange_limit = Number(row.exchange_limit) || 0
  form.is_exchangeable = row.is_exchangeable || false
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除优惠券 "${row.name}" 吗？`, '提示', { type: 'warning' })
    await deleteCoupon(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const { id, dateRange, ...rest } = form
    const data = {
      ...rest,
      start_time: dateRange[0],
      end_time: dateRange[1]
    }

    // 如果不开启积分兑换，重置相关字段
    if (!data.is_exchangeable) {
      data.points_required = 0
      data.exchange_limit = 0
    }

    if (isEdit.value) {
      await updateCoupon(id, data)
      ElMessage.success('更新成功')
    } else {
      await createCoupon(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    console.error(error)
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  form.id = null
  form.name = ''
  form.type = 'amount'
  form.discount_amount = 0
  form.discount_percent = 95
  form.min_amount = 0
  form.total_count = 0
  form.per_user_limit = 1
  form.dateRange = []
  form.description = ''
  form.status = 'active'
  form.is_exchangeable = false
  form.points_required = 100
  form.exchange_limit = 0
  if (formRef.value) formRef.value.resetFields()
}

// 发放优惠券
const handleGrant = (row) => {
  currentCoupon.value = row
  selectedUserIds.value = []
  userList.value = []
  grantDialogVisible.value = true
}

const searchUsers = async (query) => {
  if (!query) {
    userList.value = []
    return
  }
  userLoading.value = true
  try {
    const res = await getUserList({ search: query, page_size: 20 })
    userList.value = res.results || []
  } catch (error) {
    console.error(error)
  } finally {
    userLoading.value = false
  }
}

const submitGrant = async () => {
  if (selectedUserIds.value.length === 0) {
    ElMessage.warning('请选择用户')
    return
  }

  granting.value = true
  try {
    const res = await grantCoupon(currentCoupon.value.id, selectedUserIds.value)
    ElMessage.success(res.message)
    grantDialogVisible.value = false
  } catch (error) {
    console.error(error)
  } finally {
    granting.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.coupon-page .page-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
}
.table-toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}
.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
.points-value {
  color: #e6a23c;
  font-weight: bold;
}
.text-muted {
  color: #999;
}
.grant-info {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}
.grant-info p {
  margin: 5px 0;
  color: #666;
}
.grant-info strong {
  color: #333;
}
</style>
