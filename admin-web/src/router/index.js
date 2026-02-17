import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', public: true }
  },
  {
    path: '/',
    component: () => import('@/components/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '仪表盘', icon: 'Odometer' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/user/index.vue'),
        meta: { title: '用户管理', icon: 'User' }
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('@/views/category/index.vue'),
        meta: { title: '分类管理', icon: 'Menu' }
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/product/index.vue'),
        meta: { title: '产品管理', icon: 'Goods' }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/order/index.vue'),
        meta: { title: '订单管理', icon: 'List' }
      },
      {
        path: 'subscriptions',
        name: 'Subscriptions',
        component: () => import('@/views/subscription/index.vue'),
        meta: { title: '周期购管理', icon: 'Calendar' }
      },
      {
        path: 'coupons',
        name: 'Coupons',
        component: () => import('@/views/coupon/index.vue'),
        meta: { title: '优惠券管理', icon: 'Ticket' }
      },
      {
        path: 'feedbacks',
        name: 'Feedbacks',
        component: () => import('@/views/feedback/index.vue'),
        meta: { title: '反馈管理', icon: 'ChatDotRound' }
      },
      {
        path: 'refunds',
        name: 'Refunds',
        component: () => import('@/views/refund/index.vue'),
        meta: { title: '退款管理', icon: 'RefreshLeft' }
      },
      {
        path: 'reviews',
        name: 'Reviews',
        component: () => import('@/views/comment/index.vue'),
        meta: { title: '评价管理', icon: 'Star' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || '管理后台'} - 鲜牛奶订购管理系统`

  const userStore = useUserStore()

  if (to.meta.public) {
    next()
  } else if (!userStore.isLoggedIn) {
    next('/login')
  } else {
    next()
  }
})

export default router
