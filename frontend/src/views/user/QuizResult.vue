<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import UserNavbar from '@/components/user/UserNavbar.vue'
import UserSidebar from '@/components/user/UserSidebar.vue'
import { useApi } from '@/composables/useApi'
import { format } from 'date-fns'

const api = useApi()
const route = useRoute()
const attemptId = parseInt(route.params.id)

const loading = ref(true)
const result = ref({})
const quiz = ref({})
const chapter = ref({})
const subject = ref({})
const filter = ref('all')
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

// Fixed computed properties using backend data
const correctAnswers = computed(() => {
  return result.value.correct_answers || 0
})

const incorrectAnswers = computed(() => {
  return result.value.incorrect_answers || 0
})

const unattemptedQuestions = computed(() => {
  return result.value.unattempted || 0
})

const totalQuestions = computed(() => {
  return result.value.total_questions || 0
})

const scoreColor = computed(() => {
  if (!result.value.score_percentage) return ''
  if (result.value.score_percentage >= (result.value.passing_score || 60)) {
    return 'text-success'
  } else {
    return 'text-danger'
  }
})

const scoreColorClass = computed(() => {
  if (!result.value.score_percentage) return ''
  if (result.value.score_percentage >= 90) {
    return 'bg-success-subtle border-success'
  } else if (result.value.score_percentage >= (result.value.passing_score || 60)) {
    return 'bg-primary-subtle border-primary'
  } else {
    return 'bg-danger-subtle border-danger'
  }
})

const scoreMessage = computed(() => {
  if (!result.value.score_percentage) return ''
  if (result.value.score_percentage >= 90) {
    return 'Excellent! Outstanding performance!'
  } else if (result.value.score_percentage >= 75) {
    return 'Great job! Well done!'
  } else if (result.value.score_percentage >= (result.value.passing_score || 60)) {
    return 'Good work! You passed the quiz.'
  } else {
    return 'Try again. You can do better next time!'
  }
})

const filteredQuestions = computed(() => {
  if (!result.value.responses) return []
  
  switch (filter.value) {
    case 'correct':
      return result.value.responses.filter(q => q.is_correct)
    case 'incorrect':
      return result.value.responses.filter(q => q.selected_option > 0 && !q.is_correct)
    case 'unattempted':
      return result.value.responses.filter(q => q.selected_option === 0)
    default:
      return result.value.responses
  }
})

onMounted(async () => {
  try {
    checkScreenSize()
    window.addEventListener('resize', checkScreenSize)
    
    // Load result details
    const resultResponse = await api.get(`/attempts/${attemptId}/results`)
    result.value = resultResponse.data
    
    // Load quiz details
    const quizResponse = await api.get(`/quizzes/${result.value.quiz_id}`)
    quiz.value = quizResponse.data
    
    // Load chapter details
    const chapterResponse = await api.get(`/chapters/${quiz.value.chapter_id}`)
    chapter.value = chapterResponse.data
    
    // Load subject details
    const subjectResponse = await api.get(`/subjects/${chapter.value.subject_id}`)
    subject.value = subjectResponse.data
  } catch (error) {
    console.error('Error loading quiz results:', error)
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})

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
          <p class="mt-2">Loading quiz results...</p>
        </div>
        
        <div v-else>
          <nav aria-label="breadcrumb" class="mb-4">
            <ol class="breadcrumb">
              <li class="breadcrumb-item"><router-link to="/subjects">Subjects</router-link></li>
              <li class="breadcrumb-item">
                <router-link :to="`/subjects/${subject.id}`">{{ subject.name }}</router-link>
              </li>
              <li class="breadcrumb-item">
                <router-link :to="`/chapters/${chapter.id}/quizzes`">{{ chapter.name }}</router-link>
              </li>
              <li class="breadcrumb-item">
                <router-link :to="`/quizzes/${quiz.id}`">{{ quiz.title }}</router-link>
              </li>
              <li class="breadcrumb-item active" aria-current="page">Results</li>
            </ol>
          </nav>
          
          <div class="card mb-4 shadow">
            <div class="card-header bg-white py-3">
              <h4 class="mb-0">Quiz Result: {{ result.quiz_title }}</h4>
            </div>
            <div class="card-body p-3 p-md-4">
              <div class="row g-4">
                <div class="col-12 col-lg-6">
                  <div class="score-summary text-center mb-4 mb-lg-0">
                    <div class="score-circle mx-auto mb-3" :class="scoreColorClass">
                      <div class="score-value">{{ result.score_percentage || 0 }}%</div>
                    </div>
                    <h5>{{ scoreMessage }}</h5>
                    <p class="text-muted">
                      You scored {{ result.score || 0 }} out of {{ result.total_marks || 0 }} marks
                    </p>
                    <div class="result-stats mt-4 d-flex justify-content-center">
                      <div class="me-4 text-center">
                        <div class="stat-circle bg-success text-white mx-auto mb-2">
                          <i class="bi bi-check-lg"></i>
                        </div>
                        <div class="stat-number fw-bold">{{ correctAnswers }}</div>
                        <div class="stat-label text-muted small">Correct</div>
                      </div>
                      <div class="me-4 text-center">
                        <div class="stat-circle bg-danger text-white mx-auto mb-2">
                          <i class="bi bi-x-lg"></i>
                        </div>
                        <div class="stat-number fw-bold">{{ incorrectAnswers }}</div>
                        <div class="stat-label text-muted small">Incorrect</div>
                      </div>
                      <div class="text-center">
                        <div class="stat-circle bg-warning text-white mx-auto mb-2">
                          <i class="bi bi-dash-lg"></i>
                        </div>
                        <div class="stat-number fw-bold">{{ unattemptedQuestions }}</div>
                        <div class="stat-label text-muted small">Unattempted</div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="col-12 col-lg-6">
                  <div class="quiz-info p-3 p-md-4 bg-light rounded-3">
                    <div class="row mb-4">
                      <div class="col-6">
                        <div class="info-item">
                          <h6 class="text-muted mb-1">Time Taken</h6>
                          <div class="fw-medium">{{ formatDuration(result.time_taken) }}</div>
                        </div>
                      </div>
                      <div class="col-6">
                        <div class="info-item">
                          <h6 class="text-muted mb-1">Date</h6>
                          <div class="fw-medium">{{ formatDate(result.submitted_at) }}</div>
                        </div>
                      </div>
                    </div>
                    <div class="row mb-4">
                      <div class="col-6">
                        <div class="info-item">
                          <h6 class="text-muted mb-1">Subject</h6>
                          <div class="fw-medium">{{ subject.name }}</div>
                        </div>
                      </div>
                      <div class="col-6">
                        <div class="info-item">
                          <h6 class="text-muted mb-1">Chapter</h6>
                          <div class="fw-medium">{{ chapter.name }}</div>
                        </div>
                      </div>
                    </div>
                    <div class="row">
                      <div class="col-6">
                        <div class="info-item">
                          <h6 class="text-muted mb-1">Passing Score</h6>
                          <div class="fw-medium">{{ result.passing_score || 60 }}%</div>
                        </div>
                      </div>
                      <div class="col-6">
                        <div class="info-item">
                          <h6 class="text-muted mb-1">Status</h6>
                          <span 
                            :class="`badge ${result.is_passed ? 'bg-success' : 'bg-danger'}`"
                          >
                            {{ result.is_passed ? 'PASSED' : 'FAILED' }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h5 class="mb-0">Questions & Answers ({{ totalQuestions }} total)</h5>
            <div class="filter-controls">
              <div class="btn-group btn-group-sm">
                <button class="btn btn-outline-secondary" :class="{ 'active': filter === 'all' }" @click="filter = 'all'">
                  All
                </button>
                <button class="btn btn-outline-success" :class="{ 'active': filter === 'correct' }" @click="filter = 'correct'">
                  Correct ({{ correctAnswers }})
                </button>
                <button class="btn btn-outline-danger" :class="{ 'active': filter === 'incorrect' }" @click="filter = 'incorrect'">
                  Incorrect ({{ incorrectAnswers }})
                </button>
                <button class="btn btn-outline-warning" :class="{ 'active': filter === 'unattempted' }" @click="filter = 'unattempted'">
                  Unattempted ({{ unattemptedQuestions }})
                </button>
              </div>
            </div>
          </div>
          
          <div v-if="!result.responses || result.responses.length === 0" class="text-center my-5">
            <p class="text-muted">No questions available for review</p>
          </div>
          
          <div v-else class="mb-4">
            <div 
              v-for="(question, index) in filteredQuestions" 
              :key="question.id" 
              class="card mb-4 shadow-sm"
            >
              <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="mb-0">Question {{ result.responses.findIndex(q => q.id === question.id) + 1 }}</h6>
                </div>
                <div>
                  <span 
                    v-if="question.is_correct" 
                    class="badge bg-success"
                    title="Correct Answer"
                  >
                    <i class="bi bi-check-lg"></i> {{ question.score }}/{{ question.marks }}
                  </span>
                  <span 
                    v-else-if="question.selected_option > 0" 
                    class="badge bg-danger"
                    title="Incorrect Answer"
                  >
                    <i class="bi bi-x-lg"></i> 0/{{ question.marks }}
                  </span>
                  <span 
                    v-else 
                    class="badge bg-warning"
                    title="Not Attempted"
                  >
                    <i class="bi bi-dash-lg"></i> 0/{{ question.marks }}
                  </span>
                </div>
              </div>
              <div class="card-body p-3 p-md-4">
                <p class="card-text question-text mb-4">{{ question.question_text }}</p>
                
                <div class="options-list">
                  <div 
                    v-for="i in 4" 
                    :key="i" 
                    class="option-item mb-3"
                    :class="{
                      'selected': question.selected_option === i,
                      'correct': question.correct_option === i,
                      'incorrect': question.selected_option === i && question.selected_option !== question.correct_option
                    }"
                  >
                    <div class="d-flex align-items-center">
                      <div 
                        class="option-label me-3"
                        :class="{
                          'option-label-correct': question.correct_option === i,
                          'option-label-selected': question.selected_option === i && question.selected_option !== question.correct_option
                        }"
                      >
                        {{ String.fromCharCode(64 + i) }}
                      </div>
                      <div class="option-text">
                        {{ question[`option_${i}`] }}
                      </div>
                      <div class="ms-auto">
                        <i v-if="question.correct_option === i" class="bi bi-check-circle-fill text-success"></i>
                        <i v-else-if="question.selected_option === i" class="bi bi-x-circle-fill text-danger"></i>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="d-flex gap-2 justify-content-center mt-5">
            <router-link :to="`/quizzes/${quiz.id}`" class="btn btn-outline-primary">
              <i class="bi bi-arrow-repeat me-2"></i> Attempt Again
            </router-link>
            <router-link to="/subjects" class="btn btn-primary">
              <i class="bi bi-grid-fill me-2"></i> Browse More Subjects
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<!-- Keep the existing styles -->
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
  border-radius: 12px;
  border: none;
  overflow: hidden;
}

.badge {
  font-weight: 500;
  padding: 0.5em 0.75em;
}

.score-circle {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  border: 8px solid #e9ecef;
  display: flex;
  align-items: center;
  justify-content: center;
}

.score-value {
  font-size: 2.5rem;
  font-weight: 700;
}

.stat-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
}

.question-text {
  font-size: 1.1rem;
  font-weight: 500;
}

.options-list {
  padding-left: 1rem;
}

.option-item {
  border-radius: 0.5rem;
  background-color: #f8f9fa;
  border: 1px solid #e5e7eb;
  padding: 1rem;
}

.option-item.correct {
  background-color: #d1fae5;
  border-color: #10b981;
}

.option-item.selected {
  background-color: #f8fafc;
  border-color: #3b82f6;
}

.option-item.incorrect {
  background-color: #fee2e2;
  border-color: #ef4444;
}

.option-label {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: #e5e7eb;
  font-weight: 600;
}

.option-label-correct {
  background-color: #10b981;
  color: white;
}

.option-label-selected {
  background-color: #ef4444;
  color: white;
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
  .score-circle {
    width: 120px;
    height: 120px;
    border-width: 6px;
  }
  
  .score-value {
    font-size: 2rem;
  }
  
  .stat-circle {
    width: 32px;
    height: 32px;
    font-size: 0.9rem;
  }
  
  .option-label {
    width: 28px;
    height: 28px;
  }
  
  .option-item {
    padding: 0.75rem;
  }
  
  .card-body {
    padding: 1rem;
  }
  
  .filter-controls {
    display: flex;
    overflow-x: auto;
    padding-bottom: 0.5rem;
    width: 100%;
  }
  
  .filter-controls .btn-group {
    flex-wrap: nowrap;
  }
}
</style>