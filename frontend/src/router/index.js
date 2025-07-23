import { createRouter, createWebHistory } from 'vue-router'
import { authService } from '@/services/auth'
import HomePage from '../views/HomePage.vue'
import LoginPage from '../views/LoginPage.vue'
import RegisterPage from '../views/RegisterPage.vue'
import UserDashboard from '../views/user/UserDashboard.vue'
import AdminDashboard from '../views/admin/AdminDashboard.vue'
import SubjectManager from '../views/admin/SubjectManager.vue'
import ChapterManager from '../views/admin/ChapterManager.vue'
import QuizManager from '../views/admin/QuizManager.vue'
import QuestionManager from '../views/admin/QuestionManager.vue'
import UserManager from '../views/admin/UserManager.vue'
import NotFound from '@/views/NotFound.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: { guest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterPage,
      meta: { guest: true }
    },
    // Admin Routes
    {
      path: '/admin',
      name: 'adminDashboard',
      component: AdminDashboard,
      meta: { 
        requiresAuth: true,
        role: 'admin'
      }
    },
    {
      path: '/admin/subjects',
      name: 'adminSubjects',
      component: SubjectManager,
      meta: { 
        requiresAuth: true,
        role: 'admin'
      }
    },
    {
      path: '/admin/users',
      name: 'adminUsers',
      component: UserManager,
      meta: { 
        requiresAuth: true,
        role: 'admin'
      }
    },
    {
      path: '/admin/subjects/:id/chapters',
      name: 'adminChapters',
      component: ChapterManager,
      meta: { 
        requiresAuth: true,
        role: 'admin'
      }
    },
    {
      path: '/admin/chapters/:id/quizzes',
      name: 'adminQuizzes',
      component: QuizManager,
      meta: { 
        requiresAuth: true,
        role: 'admin'
      }
    },
    {
      path: '/admin/quizzes/:id/questions',
      name: 'adminQuestions',
      component: QuestionManager,
      meta: { 
        requiresAuth: true,
        role: 'admin'
      }
    },
    // User Routes
    {
      path: '/dashboard/user',
      name: 'userDashboard',
      component: UserDashboard,
      meta: { 
        requiresAuth: true,
        role: 'user'
      }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'notFound',
      component: NotFound,
    }
  ]
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('token')
  const userRole = localStorage.getItem('userRole')

  // Route requires auth
  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      return next('/login')
    }

    // Role-specific route
    if (to.meta.role && to.meta.role !== userRole) {
      return next('/')
    }
  }

  // Route is for guests only
  if (to.meta.guest && isAuthenticated) {
    return next(userRole === 'admin' ? '/admin' : '/dashboard/user')
  }

  next()
})

export default router