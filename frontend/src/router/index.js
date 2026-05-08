import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'UserLogin',
    component: () => import('@/views/user/Login.vue'),
    meta: { title: '登录 - 体重记录小助手' }
  },
  {
    path: '/',
    component: () => import('@/components/layout/UserLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/user/Dashboard.vue'),
        meta: { title: '首页 - 体重记录小助手' }
      },
      {
        path: 'records',
        name: 'WeightRecords',
        component: () => import('@/views/user/WeightRecords.vue'),
        meta: { title: '体重记录' }
      },
      {
        path: 'chart',
        name: 'ChartView',
        component: () => import('@/views/user/ChartView.vue'),
        meta: { title: '趋势图表' }
      },
      {
        path: 'goal',
        name: 'GoalSetting',
        component: () => import('@/views/user/GoalSetting.vue'),
        meta: { title: '目标设置' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/user/Profile.vue'),
        meta: { title: '个人中心' }
      }
    ]
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('@/views/admin/AdminLogin.vue'),
    meta: { title: '管理员登录' }
  },
  {
    path: '/admin',
    component: () => import('@/components/layout/AdminLayout.vue'),
    redirect: '/admin/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/AdminDashboard.vue'),
        meta: { title: '管理后台 - 仪表盘' }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('@/views/admin/UserManagement.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: 'reward-rules',
        name: 'RewardRules',
        component: () => import('@/views/admin/RewardRules.vue'),
        meta: { title: '奖励规则' }
      },
      {
        path: 'config',
        name: 'SystemConfig',
        component: () => import('@/views/admin/SystemConfig.vue'),
        meta: { title: '系统设置' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory('/weight/'),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '体重记录小助手'

  const userToken = localStorage.getItem('user_token')
  const adminToken = localStorage.getItem('admin_token')

  if (to.path.startsWith('/admin')) {
    if (to.path === '/admin/login') {
      next()
    } else if (!adminToken) {
      next('/admin/login')
    } else {
      next()
    }
  } else {
    if (to.path === '/login') {
      if (userToken) {
        next('/dashboard')
      } else {
        next()
      }
    } else if (!userToken) {
      next('/login')
    } else {
      next()
    }
  }
})

export default router
