import { createRouter, createWebHistory } from 'vue-router'
import Register from '../main/register.vue'
import problem_api from '@/api/problem/details'
import competition_problem_api from '@/api/competition/problem'
import { useCompetitionStore } from '@/store/competition'
import { useStore } from '@/store/user'  // 修改为 useStore
import { ElMessage } from 'element-plus'

// 先定义路由守卫函数
const checkAuth = (to, from, next) => {
  const userStore = useStore()  
  // 检查是否已登录
  if (!userStore.user.isLoggedIn) {  
    ElMessage.warning('请先登录！')
    next({ path: '/' })
  } else {
    // 已登录，允许访问
    next()
  }
}

const frontendRoutes = [
  {
    path: '',
    name: 'home',
    component: () => import('@/main/home.vue'),
  },
  {
    path: '/learn',
    name: 'learn',
    component: () => import('@/main/learn.vue'),
  },
  {
    path: '/problems',
    name: 'problems',
    component: () => import('@/main/problem.vue'),
  },
  {
    path: '/competition',
    name: 'competition',
    component: () => import('@/main/competition.vue')
  },
  {
    path: '/ai',
    name: 'ai',
    component: () => import('@/main/ai.vue')
  },
  {
    path: '/match/:id',
    name: 'match',
    component: () => import('@/components/competition/home.vue'),
    props: true,
    children:[
      {
        path: 'overview',
        name: 'overview',
        component: ()=>import('@/components/competition/match.vue'),
        props: true
      },
      {
        path: 'problem',
        name: 'problem',
        component: ()=>import('@/components/competition/problems.vue'),
        props: true 
      },
      {
        path: 'rank',
        name: 'rank',
        component: ()=>import('@/components/competition/rankings.vue'),
        props: true
      },
      {
        path: 'submission',
        name: 'submission',
        component: ()=>import('@/components/competition/submissions.vue'),
        props: true
      },
      {
        path: 'announcement',
        name: 'announcement',
        component: ()=>import('@/components/competition/announcements.vue'),
        props: true
      },
      {
        path: '',
        redirect: 'overview'
      }
    ]
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('@/main/about.vue'),
    children:[
      {
        path:'judger',
        name:'judger',
        component:()=>import('@/main/judger.vue')
      },
      {
        path: 'faq',
        name: 'faq',
        component: () => import('@/main/faq.vue')
      }
    ]
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/main/login.vue')
  },
  {
    path: '/reset',
    name: 'Reset',
    component: () => import('@/main/reset.vue')
  },
  {
    path:'/user',
    name:'user',
    component:()=>import('@/main/user.vue'),
    beforeEnter: checkAuth,
    children:[
      {
        path:'user-home',
        name:'user-home',
        component:()=>import('@/components/user/user-home.vue')
      },
      {
        path:'personalCenter',
        name:'PersonalCenter',
        component:()=>import('@/components/user/PersonalCenter.vue')
      },
      {
        path:'account',
        name:'account',
        component:()=>import('@/components/user/account.vue')
      }
    ]
  },
  {
    path:'/user/submissions',
    name:'UserSubmissions',
    component:()=>import('@/components/user/submitions.vue'),
    beforeEnter: checkAuth
  }
]
const adminRoutes = [
  {
    path: '',  // 默认路由
    name: 'admin',
    component: () => import('@/main/admin.vue')
  },
]

const routes = [
  {
    path: '',
    component: () => import('@/rest/frontend.vue'),
    children: frontendRoutes
  },
  {
    path: '/admin',
    component: () => import('@/rest/adminroutes.vue'),
    children: adminRoutes
  },
  {
    path: '/problem/:id',
    name: 'ProblemDetails',
    component: () => import('@/components/problem/details.vue'),
    props: true,
    beforeEnter: async (to, from, next) => {
      try {
        // 预获取题目数据
        const response = await problem_api.getProblemDetails(to.params.id);
        // 将数据附加到路由上
        to.params.problemData = response.data.data || {};
        next();
      } catch (error) {
        console.error('获取题目数据失败:', error);
        // 仍然允许导航，但页面会显示错误状态
        to.params.problemError = true;
        next();
      }
    }
  },
  {
    path: '/competition/problemslist/:competition_id/problem/:problem_id',
    name: 'CompetitionProblemDetails',
    component: () => import('@/components/competition/datails.vue'),
    props: true,
    beforeEnter: async (to, from, next) => {
      try {
        // 预获取题目数据
        const response = await competition_problem_api.getProblemDetails(
          to.params.competition_id,
          to.params.problem_id
        );
        // 将数据附加到路由上
        to.params.problemData = response.data || {};
        next();
      } catch (error) {
        console.error('获取比赛题目数据失败:', error);
        // 仍然允许导航，但页面会显示错误状态
        to.params.problemError = true;
        next();
      }
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 比赛密码校验路由守卫
router.beforeEach((to, from, next) => {
  // 检查是否为比赛相关页面
  if (to.path.startsWith('/match/')) {
    const matchId = to.params.id
    if (matchId) {
      const store = useCompetitionStore()
      if (to.name !== 'overview' && !store.isAuthenticated(matchId)) {
        next({ 
          name: 'overview',
          params: { id: matchId },
          replace: true
        })
        return
      }
    }
  }
  next()
})

export default router
