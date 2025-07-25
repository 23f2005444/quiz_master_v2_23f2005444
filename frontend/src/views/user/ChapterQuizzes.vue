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
          <p class="mt-2">Loading chapter quizzes...</p>
        </div>
        
        <div v-else>
          <nav aria-label="breadcrumb" class="mb-4">
            <ol class="breadcrumb">
              <li class="breadcrumb-item"><router-link to="/subjects">Subjects</router-link></li>
              <li class="breadcrumb-item">
                <router-link :to="`/subjects/${subject.id}`">{{ subject.name }}</router-link>
              </li>
              <li class="breadcrumb-item active" aria-current="page">{{ chapter.name }}</li>
            </ol>
          </nav>
          
          <div class="card mb-4 shadow-sm">
            <div class="card-body p-3 p-md-4">
              <div class="d-flex flex-wrap justify-content-between align-items-start mb-3">
                <h2 class="card-title mb-2 me-2">{{ chapter.name }}</h2>
                <span class="badge bg-primary">{{ quizzes.length }} quizzes</span>
              </div>
              <p class="card-text">{{ chapter.description }}</p>
              
              <div class="mt-3 d-flex flex-wrap gap-2">
                <span class="badge bg-light text-dark">
                  <i class="bi bi-book me-1"></i> {{ subject.name }}
                </span>
                <span class="badge bg-light text-dark" v-if="chapter.learning_path">
                  <i class="bi bi-signpost me-1"></i> {{ chapter.learning_path }}
                </span>
              </div>
            </div>
          </div>
          
          <!-- Search and Filter -->
          <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center mb-4">
            <h4 class="mb-3 mb-sm-0">Available Quizzes</h4>
            
            <div class="d-flex flex-grow-1 flex-sm-grow-0 gap-2 align-items-center">
              <div class="input-group" style="max-width: 250px">
                <input
                  type="text"
                  class="form-control"
                  placeholder="Search quizzes..."
                  v-model="searchQuery"
                />
                <button class="btn btn-outline-secondary" type="button">
                  <i class="bi bi-search"></i>
                </button>
              </div>
              
              <div class="dropdown">
                <button class="btn btn-outline-secondary dropdown-toggle" type="button" id="sortDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                  <i class="bi bi-sort-alpha-down me-1"></i> Sort
                </button>
                <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="sortDropdown">
                  <li><a class="dropdown-item" href="#" @click.prevent="sortQuizzes('title')">By Title</a></li>
                  <li><a class="dropdown-item" href="#" @click.prevent="sortQuizzes('date')">By Date</a></li>
                  <li><a class="dropdown-item" href="#" @click.prevent="sortQuizzes('duration')">By Duration</a></li>
                </ul>
              </div>
            </div>
          </div>
          
          <div v-if="filteredQuizzes.length === 0" class="text-center my-5">
            <div class="empty-state">
              <i class="bi bi-clipboard-x empty-icon"></i>
              <h5>No quizzes available</h5>
              <p class="text-muted">This chapter doesn't have any quizzes yet.</p>
              <router-link to="/subjects" class="btn btn-primary mt-2">
                <i class="bi bi-arrow-left me-2"></i> Back to Subjects
              </router-link>
            </div>
          </div>
          
          <div v-else>
            <div class="row g-3 g-md-4">
              <div v-for="quiz in filteredQuizzes" :key="quiz.id" class="col-12 col-sm-6 col-lg-4">
                <div class="card h-100 quiz-card">
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                      <h5 class="card-title">{{ quiz.title }}</h5>
                      <span class="badge bg-primary">{{ quiz.total_marks }} marks</span>
                    </div>
                    
                    <p class="card-text text-muted mb-3">{{ quiz.description }}</p>
                    
                    <div class="quiz-stats mb-3">
                      <div class="row row-cols-2 g-2">
                        <div class="col">
                          <div class="stat-item">
                            <i class="bi bi-clock stat-icon"></i>
                            <div class="stat-info">
                              <div class="stat-label">Duration</div>
                              <div class="stat-value">{{ formatDuration(quiz.time_duration) }}</div>
                            </div>
                          </div>
                        </div>
                        <div class="col">
                          <div class="stat-item">
                            <i class="bi bi-question-circle stat-icon"></i>
                            <div class="stat-info">
                              <div class="stat-label">Questions</div>
                              <div class="stat-value">{{ quiz.question_count }}</div>
                            </div>
                          </div>
                        </div>
                        <div class="col">
                          <div class="stat-item">
                            <i class="bi bi-award stat-icon"></i>
                            <div class="stat-info">
                              <div class="stat-label">Passing</div>
                              <div class="stat-value">{{ quiz.passing_score }}%</div>
                            </div>
                          </div>
                        </div>
                        <div class="col">
                          <div class="stat-item">
                            <i class="bi bi-calendar-date stat-icon"></i>
                            <div class="stat-info">
                              <div class="stat-label">Date</div>
                              <div class="stat-value">{{ formatDate(quiz.date_of_quiz) }}</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div class="progress mb-3" style="height: 5px;" v-if="quiz.attempts_count > 0">
                      <div 
                        class="progress-bar" 
                        role="progressbar" 
                        :style="{width: `${quiz.best_score || 0}%`}"
                        :class="getScoreClass(quiz.best_score)"
                        aria-valuemin="0" 
                        aria-valuemax="100"
                      ></div>
                    </div>
                    
                    <p class="small text-muted mb-0" v-if="quiz.attempts_count > 0">
                      Best score: {{ quiz.best_score }}% ({{ quiz.attempts_count }} attempts)
                    </p>
                  </div>
                  <div class="card-footer bg-white border-top-0">
                    <router-link :to="`/quizzes/${quiz.id}`" class="btn btn-primary w-100">
                      <i class="bi bi-play-fill me-2"></i> View Quiz
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import UserNavbar from '@/components/user/UserNavbar.vue'
import UserSidebar from '@/components/user/UserSidebar.vue'
import { useApi } from '@/composables/useApi'
import { format } from 'date-fns'

const api = useApi()
const route = useRoute()
const chapterId = parseInt(route.params.id)

const loading = ref(true)
const chapter = ref({})
const subject = ref({})
const quizzes = ref([])
const searchQuery = ref('')
const sortBy = ref('title')
const sortDirection = ref('asc')
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

const filteredQuizzes = computed(() => {
  let result = [...quizzes.value]
  
  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(quiz => 
      quiz.title.toLowerCase().includes(query) ||
      quiz.description.toLowerCase().includes(query)
    )
  }
  
  // Apply sorting
  result.sort((a, b) => {
    let comparison = 0
    
    switch (sortBy.value) {
      case 'title':
        comparison = a.title.localeCompare(b.title)
        break
      case 'date':
        comparison = new Date(a.date_of_quiz) - new Date(b.date_of_quiz)
        break
      case 'duration':
        comparison = a.time_duration - b.time_duration
        break
      default:
        comparison = a.title.localeCompare(b.title)
    }
    
    return sortDirection.value === 'asc' ? comparison : -comparison
  })
  
  return result
})

const sortQuizzes = (field) => {
  if (sortBy.value === field) {
    // Toggle direction if same field
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    // Set new field and reset direction
    sortBy.value = field
    sortDirection.value = 'asc'
  }
}

const getScoreClass = (score) => {
  if (!score) return 'bg-secondary'
  if (score >= 90) return 'bg-success'
  if (score >= 60) return 'bg-primary'
  return 'bg-danger'
}

onMounted(async () => {
  try {
    // Check screen size initially
    checkScreenSize()
    
    // Add resize listener
    window.addEventListener('resize', checkScreenSize)
    
    // Load chapter details
    const chapterResponse = await api.get(`/chapters/${chapterId}`)
    chapter.value = chapterResponse.data
    
    // Load subject details
    const subjectResponse = await api.get(`/subjects/${chapter.value.subject_id}`)
    subject.value = subjectResponse.data
    
    // Load quizzes
    const quizzesResponse = await api.get(`/chapters/${chapterId}/quizzes`)
    quizzes.value = quizzesResponse.data.map(quiz => ({
      ...quiz,
      attempts_count: Math.floor(Math.random() * 4), // Simulate attempt count for UI display
      best_score: Math.random() > 0.5 ? Math.floor(Math.random() * 100) : 0 // Simulate best score for UI display
    }))
  } catch (error) {
    console.error('Error loading chapter quizzes:', error)
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})

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

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    return format(new Date(dateString), 'MMM dd, yyyy')
  } catch (e) {
    return dateString
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

.breadcrumb a {
  text-decoration: none;
}

.card {
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  border: none;
  overflow: hidden;
}

.quiz-card {
  transition: transform 0.2s;
}

.quiz-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.card-title {
  font-weight: 600;
}

.badge {
  font-weight: 500;
  padding: 0.5em 0.75em;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1.5rem;
  color: #dee2e6;
}

.stat-item {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
  border-radius: 8px;
  margin-right: 10px;
  flex-shrink: 0;
}

.stat-info {
  min-width: 0;
}

.stat-label {
  font-size: 0.75rem;
  color: #6c757d;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-weight: 600;
  font-size: 0.875rem;
  line-height: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
  h2 {
    font-size: 1.5rem;
  }
  
  h4 {
    font-size: 1.3rem;
  }
  
  .card-body {
    padding: 1rem;
  }
  
  .empty-icon {
    font-size: 2.5rem;
  }
  
  .stat-icon {
    width: 28px;
    height: 28px;
    font-size: 0.8rem;
  }
}
</style>