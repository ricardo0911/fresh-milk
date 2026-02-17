<template>
  <div class="user-page">
    <div class="page-card">
      <!-- 搜索栏 -->
      <div class="search-form">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="用户名">
            <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable />
          </el-form-item>
          <el-form-item label="手机号">
            <el-input v-model="searchForm.phone" placeholder="请输入手机号" clearable />
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

      <!-- 表格 -->
      <el-table :data="userList" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="points" label="积分" width="100">
          <template #default="{ row }">
            <span class="points-value">{{ row.points || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="member_level" label="会员等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getMemberLevelType(row.member_level)">
              {{ getMemberLevelText(row.member_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date_joined" label="注册时间" width="180" />
        <el-table-column label="操作" fixed="right" width="280">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button type="success" link @click="handleAdjustPoints(row)">
              <el-icon><Coin /></el-icon>
              积分
            </el-button>
            <el-button type="warning" link @click="handleToggleActive(row)">
              <el-icon><Switch /></el-icon>
              {{ row.is_active ? '禁用' : '启用' }}
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

    <!-- 用户详情弹窗 -->
    <el-dialog v-model="dialogVisible" title="用户详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="用户ID">{{ currentUser.id }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ currentUser.username }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ currentUser.phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="当前积分">
          <span class="points-value">{{ currentUser.points || 0 }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="会员等级">
          <el-tag :type="getMemberLevelType(currentUser.member_level)">
            {{ getMemberLevelText(currentUser.member_level) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentUser.is_active ? 'success' : 'danger'">
            {{ currentUser.is_active ? '正常' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="注册时间" :span="2">{{ currentUser.date_joined }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 积分调整弹窗 -->
    <el-dialog v-model="pointsDialogVisible" title="调整积分" width="500px">
      <el-form :model="pointsForm" label-width="100px">
        <el-form-item label="当前用户">
          <span>{{ pointsForm.username }}</span>
        </el-form-item>
        <el-form-item label="当前积分">
          <span class="points-value">{{ pointsForm.currentPoints }}</span>
        </el-form-item>
        <el-form-item label="调整类型">
          <el-radio-group v-model="pointsForm.type">
            <el-radio value="add">增加</el-radio>
            <el-radio value="subtract">扣减</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="积分数量">
          <el-input-number v-model="pointsForm.points" :min="1" :max="100000" />
        </el-form-item>
        <el-form-item label="调整原因">
          <el-input v-model="pointsForm.remark" type="textarea" placeholder="请输入调整原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pointsDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPointsAdjust">确认调整</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Coin } from '@element-plus/icons-vue'
import { getUserList, toggleUserActive, adjustUserPoints } from '@/api/user'

const loading = ref(false)
const userList = ref([])
const dialogVisible = ref(false)
const pointsDialogVisible = ref(false)
const currentUser = ref({})

const searchForm = reactive({
  username: '',
  phone: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const pointsForm = reactive({
  userId: null,
  username: '',
  currentPoints: 0,
  type: 'add',
  points: 100,
  remark: ''
})

const memberLevelMap = {
  regular: { text: '普通会员', type: 'info' },
  silver: { text: '银卡会员', type: '' },
  gold: { text: '金卡会员', type: 'warning' },
  platinum: { text: '铂金会员', type: 'danger' }
}

const getMemberLevelText = (level) => memberLevelMap[level]?.text || '普通会员'
const getMemberLevelType = (level) => memberLevelMap[level]?.type || 'info'

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm
    }
    // 清理空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null) {
        delete params[key]
      }
    })
    const res = await getUserList(params)
    userList.value = res.results || []
    pagination.total = res.count || 0
  } catch (error) {
    console.error('Failed to load users:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.username = ''
  searchForm.phone = ''
  pagination.page = 1
  loadData()
}

const handleView = (row) => {
  currentUser.value = row
  dialogVisible.value = true
}

const handleAdjustPoints = (row) => {
  pointsForm.userId = row.id
  pointsForm.username = row.username
  pointsForm.currentPoints = row.points || 0
  pointsForm.type = 'add'
  pointsForm.points = 100
  pointsForm.remark = ''
  pointsDialogVisible.value = true
}

const submitPointsAdjust = async () => {
  if (!pointsForm.points || pointsForm.points <= 0) {
    ElMessage.warning('请输入有效的积分数量')
    return
  }

  try {
    const points = pointsForm.type === 'add' ? pointsForm.points : -pointsForm.points
    await adjustUserPoints(pointsForm.userId, {
      points,
      remark: pointsForm.remark || (pointsForm.type === 'add' ? '管理员增加积分' : '管理员扣减积分')
    })
    ElMessage.success('积分调整成功')
    pointsDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('Adjust points failed:', error)
    ElMessage.error('积分调整失败')
  }
}

const handleToggleActive = async (row) => {
  const action = row.is_active ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确定要${action}用户 "${row.username}" 吗？`, '提示', {
      type: 'warning'
    })
    await toggleUserActive(row.id)
    ElMessage.success(`${action}成功`)
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Toggle active failed:', error)
    }
  }
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.user-page {
  .page-card {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
  }

  .search-form {
    margin-bottom: 20px;
  }

  .pagination-wrapper {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }

  .points-value {
    color: #e6a23c;
    font-weight: bold;
  }
}
</style>
