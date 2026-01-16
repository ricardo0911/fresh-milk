// admin.js - 管理后台逻辑

// API基础配置
const API_BASE = 'http://127.0.0.1:8000/api';

// 页面初始化
document.addEventListener('DOMContentLoaded', function () {
    initNavigation();
    loadDashboardData();
    initCharts();
});

// 初始化导航
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault();
            navItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            // 可以在这里添加页面切换逻辑
        });
    });

    // 日期范围选择
    const dateBtns = document.querySelectorAll('.date-btn');
    dateBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            dateBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const days = this.dataset.days;
            loadSalesData(days);
        });
    });
}

// 加载仪表盘数据
async function loadDashboardData() {
    try {
        // 模拟数据（后端连接后可替换为真实API调用）
        const mockData = {
            overview: {
                total_users: 1256,
                total_products: 48,
                total_orders: 3892,
                total_revenue: 156780.50
            },
            today: {
                orders: 28,
                revenue: 2680.50,
                new_users: 15
            },
            pending: {
                orders: 5,
                feedbacks: 2,
                low_stock: 3
            }
        };

        // 更新统计卡片
        updateStatCards(mockData);

        // 加载表格数据
        loadHotProducts();
        loadLatestOrders();

    } catch (error) {
        console.error('加载数据失败:', error);
    }
}

// 更新统计卡片
function updateStatCards(data) {
    document.getElementById('todayOrders').textContent = data.today.orders;
    document.getElementById('todayRevenue').textContent = `¥${data.today.revenue.toFixed(2)}`;
    document.getElementById('newUsers').textContent = data.today.new_users;
    document.getElementById('activeSubscriptions').textContent = '156';

    document.getElementById('pendingOrders').textContent = data.pending.orders;
    document.getElementById('lowStock').textContent = data.pending.low_stock;
}

// 初始化图表
function initCharts() {
    initSalesTrendChart();
    initCategorySalesChart();
    initUserGrowthChart();
}

// 销售趋势图表
function initSalesTrendChart() {
    const chartDom = document.getElementById('salesTrendChart');
    const myChart = echarts.init(chartDom);

    const option = {
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderColor: '#e5e7eb',
            textStyle: { color: '#1f2937' }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: ['01-10', '01-11', '01-12', '01-13', '01-14', '01-15', '01-16'],
            axisLine: { lineStyle: { color: '#e5e7eb' } },
            axisLabel: { color: '#6b7280' }
        },
        yAxis: [
            {
                type: 'value',
                name: '销售额(元)',
                axisLine: { show: false },
                axisTick: { show: false },
                axisLabel: { color: '#6b7280' },
                splitLine: { lineStyle: { color: '#f3f4f6' } }
            },
            {
                type: 'value',
                name: '订单量',
                axisLine: { show: false },
                axisTick: { show: false },
                axisLabel: { color: '#6b7280' },
                splitLine: { show: false }
            }
        ],
        series: [
            {
                name: '销售额',
                type: 'line',
                smooth: true,
                data: [2100, 2350, 1890, 2680, 2450, 3120, 2680],
                lineStyle: { color: '#667eea', width: 3 },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
                        { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
                    ])
                },
                itemStyle: { color: '#667eea' }
            },
            {
                name: '订单量',
                type: 'bar',
                yAxisIndex: 1,
                data: [22, 25, 18, 28, 24, 32, 28],
                barWidth: 20,
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: '#10b981' },
                        { offset: 1, color: '#059669' }
                    ]),
                    borderRadius: [4, 4, 0, 0]
                }
            }
        ]
    };

    myChart.setOption(option);
    window.addEventListener('resize', () => myChart.resize());
}

// 商品分类销售占比
function initCategorySalesChart() {
    const chartDom = document.getElementById('categorySalesChart');
    const myChart = echarts.init(chartDom);

    const option = {
        tooltip: {
            trigger: 'item',
            formatter: '{b}: ¥{c} ({d}%)'
        },
        legend: {
            orient: 'vertical',
            right: '5%',
            top: 'center',
            textStyle: { color: '#6b7280' }
        },
        series: [
            {
                type: 'pie',
                radius: ['45%', '70%'],
                center: ['35%', '50%'],
                avoidLabelOverlap: false,
                itemStyle: {
                    borderRadius: 8,
                    borderColor: '#fff',
                    borderWidth: 2
                },
                label: { show: false },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: '14',
                        fontWeight: 'bold'
                    }
                },
                labelLine: { show: false },
                data: [
                    { value: 4580, name: '鲜牛奶', itemStyle: { color: '#667eea' } },
                    { value: 2890, name: '酸奶', itemStyle: { color: '#764ba2' } },
                    { value: 1960, name: '低脂奶', itemStyle: { color: '#10b981' } },
                    { value: 1450, name: '儿童奶', itemStyle: { color: '#f59e0b' } },
                    { value: 980, name: '其他', itemStyle: { color: '#6b7280' } }
                ]
            }
        ]
    };

    myChart.setOption(option);
    window.addEventListener('resize', () => myChart.resize());
}

// 用户增长趋势
function initUserGrowthChart() {
    const chartDom = document.getElementById('userGrowthChart');
    const myChart = echarts.init(chartDom);

    const option = {
        tooltip: {
            trigger: 'axis'
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: ['01-10', '01-11', '01-12', '01-13', '01-14', '01-15', '01-16'],
            axisLine: { lineStyle: { color: '#e5e7eb' } },
            axisLabel: { color: '#6b7280' }
        },
        yAxis: {
            type: 'value',
            axisLine: { show: false },
            axisTick: { show: false },
            axisLabel: { color: '#6b7280' },
            splitLine: { lineStyle: { color: '#f3f4f6' } }
        },
        series: [
            {
                data: [12, 18, 15, 22, 19, 25, 15],
                type: 'line',
                smooth: true,
                lineStyle: { color: '#8b5cf6', width: 3 },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(139, 92, 246, 0.3)' },
                        { offset: 1, color: 'rgba(139, 92, 246, 0.05)' }
                    ])
                },
                itemStyle: { color: '#8b5cf6' }
            }
        ]
    };

    myChart.setOption(option);
    window.addEventListener('resize', () => myChart.resize());
}

// 加载热销商品
function loadHotProducts() {
    const mockProducts = [
        { rank: 1, name: '每日鲜牛奶 250ml×10', sales: 128, revenue: 5112.00 },
        { rank: 2, name: 'A2蛋白鲜牛奶 260ml×8', sales: 95, revenue: 6072.00 },
        { rank: 3, name: '有机纯牛奶 200ml×12', sales: 82, revenue: 5895.00 },
        { rank: 4, name: '低脂鲜牛奶 500ml×6', sales: 76, revenue: 4104.00 },
        { rank: 5, name: '儿童成长奶 200ml×12', sales: 68, revenue: 4624.00 }
    ];

    const tbody = document.getElementById('hotProductsTable');
    tbody.innerHTML = mockProducts.map(product => `
        <tr>
            <td>
                <span class="rank-badge ${product.rank === 1 ? 'gold' : product.rank === 2 ? 'silver' : product.rank === 3 ? 'bronze' : ''}">${product.rank}</span>
            </td>
            <td>${product.name}</td>
            <td>${product.sales}</td>
            <td>¥${product.revenue.toFixed(2)}</td>
        </tr>
    `).join('');
}

// 加载最新订单
function loadLatestOrders() {
    const mockOrders = [
        { no: 'FM2024011600028', user: '张三', amount: 89.80, status: 'paid' },
        { no: 'FM2024011600027', user: '李四', amount: 156.00, status: 'shipped' },
        { no: 'FM2024011600026', user: '王五', amount: 68.50, status: 'completed' },
        { no: 'FM2024011600025', user: '赵六', amount: 245.00, status: 'pending' },
        { no: 'FM2024011600024', user: '陈七', amount: 112.30, status: 'completed' }
    ];

    const statusMap = {
        pending: '待付款',
        paid: '待发货',
        shipped: '配送中',
        completed: '已完成'
    };

    const tbody = document.getElementById('latestOrdersTable');
    tbody.innerHTML = mockOrders.map(order => `
        <tr>
            <td>${order.no}</td>
            <td>${order.user}</td>
            <td>¥${order.amount.toFixed(2)}</td>
            <td><span class="status-badge ${order.status}">${statusMap[order.status]}</span></td>
        </tr>
    `).join('');
}

// 加载销售数据（按天数）
async function loadSalesData(days) {
    console.log(`加载最近 ${days} 天的数据`);
    // TODO: 调用真实API
    // const response = await fetch(`${API_BASE}/statistics/sales/?days=${days}`);
    // const data = await response.json();
    // 更新图表...
}

// 刷新数据
function refreshData() {
    loadDashboardData();
    // 重新初始化图表
    initSalesTrendChart();
    initCategorySalesChart();
    initUserGrowthChart();
}

// 导航到指定页面
function navigateTo(page) {
    console.log(`导航到: ${page}`);
    // TODO: 实现页面导航逻辑
}
