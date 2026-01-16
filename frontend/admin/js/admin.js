// Fresh Milk 管理后台 JavaScript

// 初始化图表
document.addEventListener('DOMContentLoaded', function () {
    initCharts();
    initEventListeners();
});

// 初始化图表
function initCharts() {
    // 销售趋势图
    const salesChartEl = document.getElementById('salesChart');
    if (salesChartEl) {
        const salesChart = echarts.init(salesChartEl);
        const salesOption = {
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'cross' }
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
                data: ['1月10日', '1月11日', '1月12日', '1月13日', '1月14日', '1月15日', '1月16日'],
                axisLine: { lineStyle: { color: '#e5e7eb' } },
                axisLabel: { color: '#6b7280' }
            },
            yAxis: [
                {
                    type: 'value',
                    name: '销售额',
                    axisLine: { show: false },
                    axisTick: { show: false },
                    splitLine: { lineStyle: { color: '#f3f4f6' } },
                    axisLabel: { color: '#6b7280', formatter: '¥{value}' }
                },
                {
                    type: 'value',
                    name: '订单量',
                    axisLine: { show: false },
                    axisTick: { show: false },
                    splitLine: { show: false },
                    axisLabel: { color: '#6b7280' }
                }
            ],
            series: [
                {
                    name: '销售额',
                    type: 'line',
                    smooth: true,
                    lineStyle: { color: '#667eea', width: 3 },
                    areaStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
                            { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
                        ])
                    },
                    itemStyle: { color: '#667eea' },
                    data: [2100, 2350, 1980, 2680, 2450, 2890, 2680]
                },
                {
                    name: '订单量',
                    type: 'bar',
                    yAxisIndex: 1,
                    barWidth: 20,
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: '#10b981' },
                            { offset: 1, color: '#059669' }
                        ]),
                        borderRadius: [4, 4, 0, 0]
                    },
                    data: [22, 25, 21, 28, 26, 30, 28]
                }
            ]
        };
        salesChart.setOption(salesOption);
        window.addEventListener('resize', () => salesChart.resize());
    }

    // 分类销售图
    const categoryChartEl = document.getElementById('categoryChart');
    if (categoryChartEl) {
        const categoryChart = echarts.init(categoryChartEl);
        const categoryOption = {
            tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
            legend: {
                orient: 'vertical',
                right: '5%',
                top: 'center',
                textStyle: { color: '#6b7280' }
            },
            series: [{
                type: 'pie',
                radius: ['45%', '70%'],
                center: ['35%', '50%'],
                avoidLabelOverlap: false,
                itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
                label: { show: false },
                emphasis: {
                    label: { show: true, fontSize: 14, fontWeight: 'bold' }
                },
                data: [
                    { value: 42, name: '鲜牛奶', itemStyle: { color: '#667eea' } },
                    { value: 25, name: '酸奶', itemStyle: { color: '#10b981' } },
                    { value: 18, name: '儿童奶', itemStyle: { color: '#f59e0b' } },
                    { value: 10, name: '有机奶', itemStyle: { color: '#8b5cf6' } },
                    { value: 5, name: '低脂奶', itemStyle: { color: '#06b6d4' } }
                ]
            }]
        };
        categoryChart.setOption(categoryOption);
        window.addEventListener('resize', () => categoryChart.resize());
    }

    // 用户增长图
    const userGrowthEl = document.getElementById('userGrowthChart');
    if (userGrowthEl) {
        const userGrowthChart = echarts.init(userGrowthEl);
        const userGrowthOption = {
            tooltip: { trigger: 'axis' },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: ['10日', '11日', '12日', '13日', '14日', '15日', '16日'],
                axisLine: { lineStyle: { color: '#e5e7eb' } },
                axisLabel: { color: '#6b7280' }
            },
            yAxis: {
                type: 'value',
                axisLine: { show: false },
                axisTick: { show: false },
                splitLine: { lineStyle: { color: '#f3f4f6' } },
                axisLabel: { color: '#6b7280' }
            },
            series: [{
                type: 'line',
                smooth: true,
                symbol: 'circle',
                symbolSize: 8,
                lineStyle: { color: '#8b5cf6', width: 3 },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(139, 92, 246, 0.3)' },
                        { offset: 1, color: 'rgba(139, 92, 246, 0.05)' }
                    ])
                },
                itemStyle: { color: '#8b5cf6' },
                data: [12, 18, 15, 22, 16, 20, 15]
            }]
        };
        userGrowthChart.setOption(userGrowthOption);
        window.addEventListener('resize', () => userGrowthChart.resize());
    }
}

// 初始化事件监听
function initEventListeners() {
    // 日期筛选
    const dateButtons = document.querySelectorAll('.date-filter .filter-btn');
    dateButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            dateButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            loadDashboardData(this.dataset.range);
        });
    });
}

// 刷新数据
function refreshData() {
    location.reload();
}

// 加载仪表盘数据
function loadDashboardData(range) {
    console.log('加载数据范围:', range);
    // TODO: 调用API获取数据
}

// 退出登录
function logout() {
    if (confirm('确定要退出登录吗？')) {
        window.location.href = '../login.html';
    }
}

// 切换侧边栏
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('collapsed');
}

// 格式化金额
function formatMoney(amount) {
    return '¥' + parseFloat(amount).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// 格式化日期
function formatDate(date) {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// 显示提示
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// 确认对话框
function confirmDialog(message) {
    return new Promise((resolve) => {
        resolve(confirm(message));
    });
}
