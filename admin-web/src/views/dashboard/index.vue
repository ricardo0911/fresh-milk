<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stat-cards">
      <div class="stat-card">
        <div class="stat-icon" style="background: #409EFF;">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-title">用户总数</div>
          <div class="stat-value">{{ overview.total_users }}</div>
          <div class="stat-footer">今日新增 +{{ today.new_users }}</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: #67C23A;">
          <el-icon><Goods /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-title">产品总数</div>
          <div class="stat-value">{{ overview.total_products }}</div>
          <div class="stat-footer">在售产品</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: #E6A23C;">
          <el-icon><List /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-title">订单总数</div>
          <div class="stat-value">{{ overview.total_orders }}</div>
          <div class="stat-footer">今日订单 +{{ today.orders }}</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: #F56C6C;">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-title">总收入</div>
          <div class="stat-value">¥{{ formatMoney(overview.total_revenue) }}</div>
          <div class="stat-footer">今日收入 ¥{{ formatMoney(today.revenue) }}</div>
        </div>
      </div>
    </div>

    <!-- 待处理事项 -->
    <div class="page-card">
      <h3 class="card-title">待处理事项</h3>
      <div class="pending-items">
        <div class="pending-item" @click="$router.push('/orders?status=paid')">
          <el-badge :value="pending.orders" :max="99" type="warning">
            <div class="pending-icon">
              <el-icon><Box /></el-icon>
            </div>
          </el-badge>
          <span>待发货订单</span>
        </div>
        <div class="pending-item">
          <el-badge :value="pending.feedbacks" :max="99" type="info">
            <div class="pending-icon">
              <el-icon><ChatDotRound /></el-icon>
            </div>
          </el-badge>
          <span>待处理反馈</span>
        </div>
        <div class="pending-item" @click="$router.push('/products?low_stock=1')">
          <el-badge :value="pending.low_stock" :max="99" type="danger">
            <div class="pending-icon">
              <el-icon><Warning /></el-icon>
            </div>
          </el-badge>
          <span>库存预警</span>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-row">
      <div class="page-card chart-card">
        <h3 class="card-title">近7天销售趋势</h3>
        <v-chart class="chart" :option="salesChartOption" autoresize />
      </div>

      <div class="page-card chart-card">
        <h3 class="card-title">分类销售占比</h3>
        <v-chart class="chart" :option="categoryChartOption" autoresize />
      </div>
    </div>

    <!-- 热门产品 -->
    <div class="page-card">
      <h3 class="card-title">热门产品 TOP 10</h3>
      <el-table :data="hotProducts" stripe>
        <el-table-column prop="name" label="产品名称" />
        <el-table-column prop="sales_count" label="销量" width="100" />
        <el-table-column prop="view_count" label="浏览量" width="100" />
        <el-table-column prop="stock" label="库存" width="100">
          <template #default="{ row }">
            <el-tag :type="row.stock < 10 ? 'danger' : 'success'">
              {{ row.stock }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { getDashboard, getSalesStatistics, getProductStatistics } from '@/api/statistics'

use([CanvasRenderer, LineChart, PieChart, GridComponent, TooltipComponent, LegendComponent])

const overview = reactive({
  total_users: 0,
  total_products: 0,
  total_orders: 0,
  total_revenue: 0
})

const today = reactive({
  orders: 0,
  revenue: 0,
  new_users: 0
})

const pending = reactive({
  orders: 0,
  feedbacks: 0,
  low_stock: 0
})

const salesData = ref([])
const categoryData = ref([])
const hotProducts = ref([])

const formatMoney = (value) => {
  return Number(value || 0).toFixed(2)
}

// 销售趋势图配置
const salesChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis'
  },
  xAxis: {
    type: 'category',
    data: salesData.value.map(item => item.date)
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: '销售额',
      type: 'line',
      smooth: true,
      data: salesData.value.map(item => item.revenue),
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ]
        }
      },
      lineStyle: { color: '#409EFF' },
      itemStyle: { color: '#409EFF' }
    }
  ]
}))

// 分类销售占比图配置
const categoryChartOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: ¥{c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold'
        }
      },
      data: categoryData.value.map(item => ({
        name: item.product__category__name || '未分类',
        value: item.total
      }))
    }
  ]
}))

// 加载数据
const loadData = async () => {
  // 加载仪表盘数据
  try {
    const dashboardRes = await getDashboard()
    console.log('Dashboard response:', dashboardRes)
    Object.assign(overview, dashboardRes.overview || {})
    Object.assign(today, dashboardRes.today || {})
    Object.assign(pending, dashboardRes.pending || {})
  } catch (error) {
    console.error('Failed to load dashboard:', error)
  }

  // 加载销售统计
  try {
    const salesRes = await getSalesStatistics({ days: 7 })
    console.log('Sales response:', salesRes)
    salesData.value = salesRes.daily_sales || []
    categoryData.value = salesRes.category_sales || []
    console.log('Sales data:', salesData.value)
  } catch (error) {
    console.error('Failed to load sales statistics:', error)
  }

  // 加载产品统计
  try {
    const productRes = await getProductStatistics()
    console.log('Product response:', productRes)
    hotProducts.value = productRes.hot_products || []
  } catch (error) {
    console.error('Failed to load product statistics:', error)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.dashboard {
  .stat-cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-bottom: 20px;
  }

  .stat-card {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 16px;

    .stat-icon {
      width: 60px;
      height: 60px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: 28px;
    }

    .stat-info {
      flex: 1;

      .stat-title {
        font-size: 14px;
        color: #909399;
        margin-bottom: 8px;
      }

      .stat-value {
        font-size: 28px;
        font-weight: bold;
        color: #303133;
      }

      .stat-footer {
        margin-top: 8px;
        font-size: 12px;
        color: #67C23A;
      }
    }
  }

  .page-card {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;

    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid #ebeef5;
    }
  }

  .pending-items {
    display: flex;
    gap: 40px;

    .pending-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      cursor: pointer;

      .pending-icon {
        width: 50px;
        height: 50px;
        background: #f5f7fa;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        color: #606266;
      }

      span {
        font-size: 14px;
        color: #606266;
      }

      &:hover {
        .pending-icon {
          background: #ecf5ff;
          color: #409EFF;
        }
      }
    }
  }

  .charts-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;

    .chart-card {
      .chart {
        height: 300px;
      }
    }
  }
}
</style>
