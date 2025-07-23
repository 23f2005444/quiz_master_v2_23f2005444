<script setup>
import UserNavbar from '@/components/user/UserNavbar.vue'
import UserSidebar from '@/components/user/UserSidebar.vue'
import { ref, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'
import { useAuth } from '@/composables/useAuth'
import { format } from 'date-fns'

const api = useApi()
const auth = useAuth()
const user = ref({})
const loading = ref(true)

// Dashboard data
const stats = ref({
  totalAttempts: 0,
  averageScore: 0,
  completedQuizzes: 0,
  availableQuizzes: 0
})

// Recent data
const recentQuizzes = ref([])
const recentAttempts = ref([])
const availableSubjects = ref([])

onMounted(async () => {
  try {
    loading.value = true
    
    // Load user data
    const userId = auth.getUserId()
    const userResponse = await api.get(`/users/${userId}`)
    user.value = userResponse.data
    
    // Load dashboard stats
    const dashboardResponse = await api.get('/user/dashboard')
    stats.value = dashboardResponse.data
    
    // Load recent quiz attempts
    const attemptsResponse = await api.get('/user/attempts/recent')
    recentAttempts.value = attemptsResponse.data
    
    // Load available quizzes
    const quizzesResponse = await api.get('/user/quizzes/available')
    recentQuizzes.value = quizzesResponse.data
    
    // Load available subjects
    const subjectsResponse = await api.get('/subjects')
    availableSubjects.value = subjectsResponse.data
    
  } catch (error) {
    console.error('Error loading dashboard data:', error)
  } finally {
    loading.value = false
  }
})

const formatDate = (dateString) => {
  try {
    return format(new Date(dateString), 'MMM dd, yyyy')
  } catch (e) {
    return dateString
  }
}

const calculateTimePassed = (dateString) => {
  const now = new Date()
  const pastDate = new Date(dateString)
  const diffTime = Math.abs(now - pastDate)
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) {
    return 'Today'
  } else if (diffDays === 1) {
    return 'Yesterday'
  } else if (diffDays < 7) {
    return `${diffDays} days ago`
  } else if (diffDays < 30) {
    const diffWeeks = Math.floor(diffDays / 7)
    return `${diffWeeks} ${diffWeeks === 1 ? 'week' : 'weeks'} ago`
  } else {
    return formatDate(dateString)
  }
}
</script>

<template>
  <div class="d-flex">
    <!-- Sidebar -->
    <UserSidebar />

    <!-- Main Content -->
    <div class="flex-grow-1" style="margin-left: 250px;">
      <UserNavbar />

      <div class="container-fluid p-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h2 class="mb-1">Welcome, {{ user.full_name || 'User' }}</h2>
            <p class="text-muted">Here's an overview of your learning progress</p>
          </div>
          <router-link to="/subjects" class="btn btn-primary">
            <i class="bi bi-play-fill"></i> Start New Quiz
          </router-link>
        </div>

        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2">Loading your dashboard...</p>
        </div>

        <div v-else>
          <!-- Statistics Cards -->
          <div class="row g-4 mb-4">
            <div class="col-md-3">
              <div class="card bg-primary text-white h-100">
                <div class="card-body">
                  <h5 class="card-title">Quiz Attempts</h5>
                  <h2 class="card-text">{{ stats.totalAttempts }}</h2>
                  <i class="bi bi-journal-check position-absolute top-50 end-0 me-3 opacity-50" style="font-size: 2rem;"></i>
                </div>
              </div>
            </div>

            <div class="col-md-3">
              <div class="card bg-success text-white h-100">
                <div class="card-body">
                  <h5 class="card-title">Average Score</h5>
                  <h2 class="card-text">{{ stats.averageScore }}%</h2>
                  <i class="bi bi-graph-up position-absolute top-50 end-0 me-3 opacity-50" style="font-size: 2rem;"></i>
                </div>
              </div>
            </div>

            <div class="col-md-3">
              <div class="card bg-info text-white h-100">
                <div class="card-body">
                  <h5 class="card-title">Completed Quizzes</h5>
                  <h2 class="card-text">{{ stats.completedQuizzes }}</h2>
                  <i class="bi bi-check-circle position-absolute top-50 end-0 me-3 opacity-50" style="font-size: 2rem;"></i>
                </div>
              </div>
            </div>

            <div class="col-md-3">
              <div class="card bg-warning text-white h-100">
                <div class="card-body">
                  <h5 class="card-title">Available Quizzes</h5>
                  <h2 class="card-text">{{ stats.availableQuizzes }}</h2>
                  <i class="bi bi-lightning position-absolute top-50 end-0 me-3 opacity-50" style="font-size: 2rem;"></i>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Activity and Available Content -->
          <div class="row g-4">
            <!-- Recent Quiz Attempts -->
            <div class="col-md-6">
              <div class="card h-100">
                <div class="card-header bg-white py-3">
                  <div class="d-flex justify-content-between align-items-center">
                    <h5 class="card-title mb-0">Recent Quiz Attempts</h5>
                    <router-link to="/attempts" class="btn btn-sm btn-outline-primary">View All</router-link>
                  </div>
                </div>
                <div class="card-body p-0">
                  <div class="list-group list-group-flush">
                    <div v-if="recentAttempts.length === 0" class="text-center py-4 text-muted">
                      <i class="bi bi-clipboard-x fs-1 mb-2"></i>
                      <p>No quiz attempts yet</p>
                      <router-link to="/subjects" class="btn btn-sm btn-primary">
                        Start your first quiz
                      </router-link>
                    </div>
                    
                    <router-link 
                      v-for="attempt in recentAttempts" 
                      :key="attempt.id" 
                      :to="`/attempts/${attempt.id}`"
                      class="list-group-item list-group-item-action"
                    >
                      <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">{{ attempt.quiz_title }}</h6>
                        <small>{{ calculateTimePassed(attempt.created_at) }}</small>
                      </div>
                      <div class="d-flex justify-content-between align-items-center">
                        <p class="mb-1 text-muted">{{ attempt.chapter_name }} ({{ attempt.subject_name }})</p>
                        <span 
                          :class="`badge ${attempt.score_percentage >= 60 ? 'bg-success' : 'bg-danger'}`"
                        >
                          {{ attempt.score_percentage }}%
                        </span>
                      </div>
                    </router-link>
                  </div>
                </div>
              </div>
            </div>

            <!-- Available Quizzes -->
            <div class="col-md-6">
              <div class="card h-100">
                <div class="card-header bg-white py-3">
                  <div class="d-flex justify-content-between align-items-center">
                    <h5 class="card-title mb-0">Available Quizzes</h5>
                    <router-link to="/subjects" class="btn btn-sm btn-outline-primary">Browse All</router-link>
                  </div>
                </div>
                <div class="card-body p-0">
                  <div class="list-group list-group-flush">
                    <div v-if="recentQuizzes.length === 0" class="text-center py-4 text-muted">
                      <i class="bi bi-clipboard-data fs-1 mb-2"></i>
                      <p>No quizzes available at the moment</p>
                    </div>
                    
                    <router-link 
                      v-for="quiz in recentQuizzes" 
                      :key="quiz.id" 
                      :to="`/quizzes/${quiz.id}`"
                      class="list-group-item list-group-item-action"
                    >
                      <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">{{ quiz.title }}</h6>
                        <small>{{ formatDate(quiz.date_of_quiz) }}</small>
                      </div>
                      <div class="d-flex justify-content-between align-items-center">
                        <p class="mb-1 text-muted">{{ quiz.chapter_name }} ({{ quiz.subject_name }})</p>
                        <span class="badge bg-info">{{ quiz.time_duration }} min</span>
                      </div>
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Available Subjects -->
          <div class="mt-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h4>Available Subjects</h4>
              <router-link to="/subjects" class="btn btn-sm btn-outline-primary">View All</router-link>
            </div>
            
            <div class="row g-4">
              <div v-if="availableSubjects.length === 0" class="col-12 text-center py-5 text-muted">
                <i class="bi bi-journal-x fs-1 mb-3"></i>
                <h5>No subjects available</h5>
                <p>Check back later for new content</p>
              </div>
              
              <div 
                v-for="subject in availableSubjects.slice(0, 4)" 
                :key="subject.id" 
                class="col-md-3"
              >
                <router-link :to="`/subjects/${subject.id}`" class="text-decoration-none">
                  <div class="card h-100">
                    <div class="card-body">
                      <h5 class="card-title">{{ subject.name }}</h5>
                      <p class="card-text text-muted">{{ subject.description }}</p>
                      <div class="text-primary">
                        <i class="bi bi-arrow-right"></i> Explore chapters
                      </div>
                    </div>
                  </div>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  transition: transform 0.2s;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.card-title {
  font-weight: 600;
}

.list-group-item-action:hover {
  background-color: #f8f9fa;
}

.badge {
  font-weight: 500;
  padding: 0.5em 0.75em;
}

a {
  text-decoration: none;
}
</style>