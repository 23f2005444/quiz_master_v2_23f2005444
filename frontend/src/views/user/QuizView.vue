<template>
  <div class="page-layout">
    <!-- Overlay for mobile when sidebar is visible -->
    <div 
      v-if="isMobile && sidebarVisible" 
      class="sidebar-backdrop"
      @click="toggleSidebar"
    ></div>
    
    <!-- Sidebar -->
    <UserSidebar 
      :class="{ 'sidebar-visible': sidebarVisible }"
      @close="sidebarVisible = false"
    />
    
    <div class="main-content" :class="{ 'with-sidebar': sidebarVisible && !isMobile }">
      <UserNavbar @toggle-sidebar="toggleSidebar" />
      
      <div class="container-fluid p-3 p-md-4">
        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2">Loading quiz details...</p>
        </div>
        
        <div v-else>
          <nav aria-label="breadcrumb" class="mb-4">
            <ol class="breadcrumb">
              <li class="breadcrumb-item"><router-link to="/subjects">Subjects</router-link></li>
              <li class="breadcrumb-item">
                <router-link :to="`/subjects/${subject.id}`">{{ subject.name }}</router-link>
              </li>
              <li class="breadcrumb-item">
                {{ chapter.name }}
              </li>
              <li class="breadcrumb-item active" aria-current="page">{{ quiz.title }}</li>
            </ol>
          </nav>
          
          <div class="card mb-4 shadow">
            <div class="card-body p-3 p-md-4">
              <h2 class="card-title mb-3">{{ quiz.title }}</h2>
              <p class="card-text">{{ quiz.description }}</p>
              
              <div class="row row-cols-2 row-cols-md-4 mt-4 g-3">
                <div class="col">
                  <div class="info-card bg-light rounded-3 p-3">
                    <div class="d-flex align-items-center">
                      <div class="icon-wrapper bg-primary text-white rounded-circle p-2 me-3">
                        <i class="bi bi-clock"></i>
                      </div>
                      <div>
                        <h6 class="mb-1">Duration</h6>
                        <p class="mb-0 text-muted">{{ formatDuration(quiz.time_duration) }}</p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="col">
                  <div class="info-card bg-light rounded-3 p-3">
                    <div class="d-flex align-items-center">
                      <div class="icon-wrapper bg-info text-white rounded-circle p-2 me-3">
                        <i class="bi bi-question-circle"></i>
                      </div>
                      <div>
                        <h6 class="mb-1">Questions</h6>
                        <p class="mb-0 text-muted">{{ questionCount }}</p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="col">
                  <div class="info-card bg-light rounded-3 p-3">
                    <div class="d-flex align-items-center">
                      <div class="icon-wrapper bg-success text-white rounded-circle p-2 me-3">
                        <i class="bi bi-award"></i>
                      </div>
                      <div>
                        <h6 class="mb-1">Total Marks</h6>
                        <p class="mb-0 text-muted">{{ quiz.total_marks }}</p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="col">
                  <div class="info-card bg-light rounded-3 p-3">
                    <div class="d-flex align-items-center">
                      <div class="icon-wrapper bg-warning text-white rounded-circle p-2 me-3">
                        <i class="bi bi-check-circle"></i>
                      </div>
                      <div>
                        <h6 class="mb-1">Passing Score</h6>
                        <p class="mb-0 text-muted">{{ quiz.passing_score }}%</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="previousAttempts.length > 0" class="card mb-4 shadow">
            <div class="card-header bg-white py-3">
              <h5 class="mb-0">Previous Attempts</h5>
            </div>
            <div class="card-body p-0">
              <div class="table-responsive">
                <table class="table table-hover mb-0 table-responsive-card">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Score</th>
                      <th>Result</th>
                      <th>Time Taken</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="attempt in previousAttempts" :key="attempt.id">
                      <td data-label="Date">{{ formatDate(attempt.created_at) }}</td>
                      <td data-label="Score">{{ attempt.score }}/{{ quiz.total_marks }} ({{ attempt.score_percentage }}%)</td>
                      <td data-label="Result">
                        <span 
                          :class="`badge ${attempt.score_percentage >= quiz.passing_score ? 'bg-success' : 'bg-danger'}`"
                        >
                          {{ attempt.score_percentage >= quiz.passing_score ? 'Passed' : 'Failed' }}
                        </span>
                      </td>
                      <td data-label="Time Taken">{{ formatDuration(attempt.time_taken) }}</td>
                      <td data-label="Actions">
                        <router-link :to="`/attempts/${attempt.id}`" class="btn btn-sm btn-outline-primary">
                          <i class="bi bi-eye me-1"></i> Details
                        </router-link>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          
          <div class="d-flex justify-content-center">
            <div class="card text-center p-3 p-md-4 shadow" style="max-width: 600px">
              <div v-if="questionCount === 0" class="text-center my-4">
                <i class="bi bi-exclamation-triangle-fill text-warning fs-1 mb-3"></i>
                <h5>No questions available</h5>
                <p class="text-muted">This quiz doesn't have any questions yet</p>
              </div>
              <template v-else>
                <div class="d-flex justify-content-center mb-4">
                  <div class="quiz-start-icon bg-light rounded-circle d-flex align-items-center justify-content-center">
                    <i class="bi bi-lightbulb text-primary"></i>
                  </div>
                </div>
                <h3>Ready to start the quiz?</h3>
                <p class="text-muted mb-4">Make sure you have enough time to complete the quiz. Once started, the timer cannot be paused.</p>
                <button 
                  @click="startQuiz" 
                  class="btn btn-primary btn-lg"
                  :disabled="startingQuiz"
                >
                  <span v-if="startingQuiz" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  <i v-else class="bi bi-play-fill me-2"></i>
                  Start Quiz
                </button>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import UserNavbar from '@/components/user/UserNavbar.vue'
import UserSidebar from '@/components/user/UserSidebar.vue'
import { useApi } from '@/composables/useApi'
import { format } from 'date-fns'

const api = useApi()
const route = useRoute()
const router = useRouter()
const quizId = parseInt(route.params.id)

const loading = ref(true)
const startingQuiz = ref(false)
const quiz = ref({})
const chapter = ref({})
const subject = ref({})
const previousAttempts = ref([])
const questionCount = ref(0)
const sidebarVisible = ref(false)
const isMobile = ref(false)

const toggleSidebar = () => {
  sidebarVisible.value = !sidebarVisible.value
}

const checkScreenSize = () => {
  isMobile.value = window.innerWidth < 992
  if (isMobile.value) {
    sidebarVisible.value = false
  } else {
    sidebarVisible.value = true
  }
}

onMounted(async () => {
  try {
    // Check screen size initially
    checkScreenSize()
    
    // Add resize listener
    window.addEventListener('resize', checkScreenSize)
    
    // Load quiz details
    const quizResponse = await api.get(`/quizzes/${quizId}`)
    quiz.value = quizResponse.data
    
    // Load chapter details
    const chapterResponse = await api.get(`/chapters/${quiz.value.chapter_id}`)
    chapter.value = chapterResponse.data
    
    // Load subject details
    const subjectResponse = await api.get(`/subjects/${chapter.value.subject_id}`)
    subject.value = subjectResponse.data
    
    // Load previous attempts
    const attemptsResponse = await api.get(`/user/attempts/by-quiz/${quizId}`)
    previousAttempts.value = attemptsResponse.data
    
    // Get question count
    const questionsResponse = await api.get(`/quizzes/${quizId}/questions/count`)
    questionCount.value = questionsResponse.data.count
  } catch (error) {
    console.error('Error loading quiz details:', error)
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})

const startQuiz = async () => {
  startingQuiz.value = true
  try {
    // Create a new attempt
    const response = await api.post(`/quizzes/${quizId}/attempts`)
    const attemptId = response.data.id
    
    // Redirect to quiz attempt page
    router.push(`/attempts/${attemptId}/take`)
  } catch (error) {
    console.error('Error starting quiz:', error)
    alert('Failed to start the quiz. Please try again.')
  } finally {
    startingQuiz.value = false
  }
}

const formatDate = (dateString) => {
  try {
    return format(new Date(dateString), 'MMM dd, yyyy, h:mm a')
  } catch (e) {
    return dateString
  }
}

const formatDuration = (minutes) => {
  if (!minutes) return '0 mins'
  
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  
  if (hours === 0) {
    return `${mins} min${mins !== 1 ? 's' : ''}`
  } else {
    return `${hours} hr${hours !== 1 ? 's' : ''} ${mins} min${mins !== 1 ? 's' : ''}`
  }
}
</script>

<style scoped>
.page-layout {
  min-height: 100vh;
  display: flex;
  width: 100%;
  position: relative;
}

.main-content {
  flex-grow: 1;
  transition: margin-left 0.3s;
  width: 100%;
  background-color: #f8f9fa;
}

.main-content.with-sidebar {
  margin-left: 250px;
}

.card {
  border-radius: 12px;
  border: none;
  overflow: hidden;
}

.breadcrumb a {
  text-decoration: none;
}

.badge {
  font-weight: 500;
  padding: 0.5em 0.75em;
}

.icon-wrapper {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.quiz-start-icon {
  width: 80px;
  height: 80px;
  font-size: 2rem;
}

/* Responsive table */
.table-responsive-card {
  width: 100%;
}

/* Sidebar backdrop overlay for mobile */
.sidebar-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1030;
}

/* Responsive styles */
@media (max-width: 991.98px) {
  .main-content {
    margin-left: 0 !important;
  }
  
  .sidebar-visible {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1040;
    height: 100vh;
    transform: translateX(0) !important;
  }
}

@media (max-width: 767.98px) {
  .table-responsive-card thead {
    display: none;
  }
  
  .table-responsive-card tbody tr {
    display: block;
    margin-bottom: 1rem;
    border: 1px solid #dee2e6;
    border-radius: 0.5rem;
  }
  
  .table-responsive-card tbody td {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #dee2e6;
    padding: 0.75rem;
  }
  
  .table-responsive-card tbody td:last-child {
    border-bottom: none;
  }
  
  .table-responsive-card tbody td:before {
    content: attr(data-label);
    font-weight: 600;
    margin-right: 1rem;
  }
  
  .icon-wrapper {
    width: 32px;
    height: 32px;
    font-size: 0.9rem;
  }
  
  h2 {
    font-size: 1.5rem;
  }
  
  h3 {
    font-size: 1.3rem;
  }
}
</style>