<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '@/composables/useApi'
import * as bootstrap from 'bootstrap'

const api = useApi()
const route = useRoute()
const router = useRouter()
const attemptId = parseInt(route.params.id)

const loading = ref(true)
const quiz = ref({})
const chapter = ref({})
const subject = ref({})
const questions = ref([])
const userAnswers = ref([])
const currentQuestionIndex = ref(0)
const timeLeft = ref(0)
const submitting = ref(false)
const confirmSubmit = ref(false)
const timeUp = ref(false)
const startTime = ref(new Date())
let timer = null

// Modal refs
const submitModalRef = ref(null)
const timeUpModalRef = ref(null)
let submitModal = null
let timeUpModal = null

// Computed properties
const currentQuestion = computed(() => {
  return questions.value[currentQuestionIndex.value] || {}
})

const answeredCount = computed(() => {
  return userAnswers.value.filter(answer => answer !== null && answer !== undefined).length
})

const unansweredCount = computed(() => {
  return questions.value.length - answeredCount.value
})

const answeredPercentage = computed(() => {
  if (questions.value.length === 0) return 0
  return (answeredCount.value / questions.value.length) * 100
})

const progress = computed(() => {
  if (questions.value.length === 0) return 0
  return ((currentQuestionIndex.value + 1) / questions.value.length) * 100
})

const progressColorClass = computed(() => {
  if (progress.value < 33) return 'bg-danger'
  if (progress.value < 66) return 'bg-warning'
  return 'bg-success'
})

// Watch for confirmSubmit changes
watch(confirmSubmit, (newVal) => {
  if (newVal && submitModal) {
    submitModal.show()
  } else if (!newVal && submitModal) {
    submitModal.hide()
  }
})

// Watch for timeUp changes
watch(timeUp, (newVal) => {
  if (newVal && timeUpModal) {
    timeUpModal.show()
    submitQuiz()
  }
})

// Methods
const selectOption = (optionNumber) => {
  // Create a new array to ensure reactivity
  const newAnswers = [...userAnswers.value]
  newAnswers[currentQuestionIndex.value] = optionNumber
  userAnswers.value = newAnswers
}

const previousQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
  }
}

const nextQuestion = () => {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++
  }
}

const goToQuestion = (index) => {
  currentQuestionIndex.value = index
}

const submitQuiz = async () => {
  if (submitting.value) return
  submitting.value = true
  
  try {
    // Calculate time taken
    const endTime = new Date()
    const timeTakenMs = endTime - startTime.value
    const timeTakenMinutes = Math.ceil(timeTakenMs / (1000 * 60))
    
    // Prepare answers in the format expected by the API
    const answers = userAnswers.value.map((answer, index) => {
      return {
        question_id: questions.value[index].id,
        selected_option: answer || 0 // Use 0 for unanswered questions
      }
    })
    
    // Submit the quiz
    await api.put(`/attempts/${attemptId}/submit`, {
      answers,
      time_taken: timeTakenMinutes
    })
    
    // Clear the timer
    clearInterval(timer)
    
    // Hide all modals before redirecting
    hideAllModals()
    
    // Add a small delay to ensure modals are properly hidden
    setTimeout(() => {
      // Redirect to the result page
      router.push(`/attempts/${attemptId}`)
    }, 100)
    
  } catch (error) {
    console.error('Error submitting quiz:', error)
    // Hide modals on error too
    hideAllModals()
    
    // Show more detailed error information
    if (error.response) {
      console.error('Response data:', error.response.data)
      alert(`Failed to submit quiz: ${error.response.data.error || 'Unknown error'}`)
    } else {
      alert('Failed to submit quiz. Please try again.')
    }
    submitting.value = false
    confirmSubmit.value = false
  }
}

const hideAllModals = () => {
  try {
    // Hide submit modal
    if (submitModal) {
      submitModal.hide()
    }
    
    // Hide time up modal
    if (timeUpModal) {
      timeUpModal.hide()
    }
    
    // Force remove all modal backdrops
    const backdrops = document.querySelectorAll('.modal-backdrop')
    backdrops.forEach(backdrop => {
      if (backdrop.parentNode) {
        backdrop.parentNode.removeChild(backdrop)
      }
    })
    
    // Remove modal-open class from body
    document.body.classList.remove('modal-open')
    
    // Reset body styles
    document.body.style.overflow = ''
    document.body.style.paddingRight = ''
    
  } catch (error) {
    console.error('Error hiding modals:', error)
  }
}

const startTimer = () => {
  timer = setInterval(() => {
    if (timeLeft.value <= 0) {
      clearInterval(timer)
      timeUp.value = true
    } else {
      timeLeft.value -= 1
    }
  }, 1000)
}

const formatTime = (seconds) => {
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// Lifecycle hooks
onMounted(async () => {
  try {
    // Initialize modals with proper event handlers
    if (submitModalRef.value) {
      submitModal = new bootstrap.Modal(submitModalRef.value, {
        backdrop: 'static',
        keyboard: false
      })
      
      // Add event listener for modal hidden event
      submitModalRef.value.addEventListener('hidden.bs.modal', () => {
        confirmSubmit.value = false
      })
    }
    
    if (timeUpModalRef.value) {
      timeUpModal = new bootstrap.Modal(timeUpModalRef.value, {
        backdrop: 'static',
        keyboard: false
      })
    }
    
    // Load attempt details
    const attemptResponse = await api.get(`/attempts/${attemptId}`)
    const attempt = attemptResponse.data
    
    // Check if attempt is already completed
    if (attempt.status === 'completed') {
      router.push(`/attempts/${attemptId}`)
      return
    }
    
    // Load quiz details
    const quizResponse = await api.get(`/quizzes/${attempt.quiz_id}`)
    quiz.value = quizResponse.data
    
    // Set time left
    timeLeft.value = quiz.value.time_duration * 60
    
    // Load chapter details
    const chapterResponse = await api.get(`/chapters/${quiz.value.chapter_id}`)
    chapter.value = chapterResponse.data
    
    // Load subject details
    const subjectResponse = await api.get(`/subjects/${chapter.value.subject_id}`)
    subject.value = subjectResponse.data
    
    // Load questions
    const questionsResponse = await api.get(`/attempts/${attemptId}/questions`)
    questions.value = questionsResponse.data
    
    // Initialize user answers array
    userAnswers.value = new Array(questions.value.length).fill(null)
    
    // Start the timer
    startTimer()
  } catch (error) {
    console.error('Error loading quiz:', error)
    loading.value = false
  } finally {
    loading.value = false
  }
})

// Clean up before component unmount
onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
  
  // Ensure all modals are properly cleaned up
  hideAllModals()
})
</script>

<template>
  <div class="quiz-attempt">
    <div class="quiz-header bg-white shadow-sm py-2 py-md-3">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col-6 col-md-7">
            <h5 class="mb-0 text-truncate">{{ quiz.title || 'Quiz' }}</h5>
            <p class="text-muted small mb-0 d-none d-md-block">
              {{ chapter.name || 'Chapter' }} / {{ subject.name || 'Subject' }}
            </p>
          </div>
          <div class="col-6 col-md-5">
            <div class="d-flex justify-content-end align-items-center">
              <div class="timer me-2 me-md-3" :class="{ 'text-danger': timeLeft < 300 }">
                <i class="bi bi-clock me-1"></i> {{ formatTime(timeLeft) }}
              </div>
              <div class="progress d-none d-md-block" style="width: 120px">
                <div 
                  class="progress-bar" 
                  role="progressbar"
                  :style="{ width: `${progress}%` }"
                  :class="progressColorClass"
                  aria-valuenow="25" 
                  aria-valuemin="0" 
                  aria-valuemax="100"
                >{{ currentQuestionIndex + 1 }}/{{ questions.length }}</div>
              </div>
              <button 
                @click="confirmSubmit = true" 
                class="btn btn-outline-primary btn-sm ms-2 ms-md-3 d-none d-md-block" 
                :disabled="submitting"
              >
                Submit
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="container-fluid p-3 py-md-4">
      <div v-if="loading" class="text-center my-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">Loading quiz questions...</p>
      </div>
      
      <div v-else-if="questions.length === 0" class="text-center my-5">
        <i class="bi bi-exclamation-triangle-fill text-warning fs-1 mb-3"></i>
        <h5>No questions available</h5>
        <p class="text-muted">This quiz doesn't have any questions</p>
        <router-link to="/subjects" class="btn btn-primary">
          Back to Subjects
        </router-link>
      </div>
      
      <div v-else class="row g-3 g-md-4">
        <div class="col-12 col-lg-8">
          <div class="card shadow-sm">
            <div class="card-body p-3 p-md-4">
              <div class="d-flex justify-content-between mb-3">
                <h5 class="mb-0">Question {{ currentQuestionIndex + 1 }}</h5>
                <span class="badge bg-light text-dark">
                  {{ currentQuestionIndex + 1 }}/{{ questions.length }}
                </span>
              </div>
              
              <div class="question-text mb-4">
                {{ currentQuestion.question_text }}
              </div>
              
              <div class="options-list">
                <div 
                  v-for="i in 4" 
                  :key="i" 
                  class="option-item mb-3"
                  :class="{ 
                    'selected': userAnswers[currentQuestionIndex] === i
                  }"
                  @click="selectOption(i)"
                >
                  <div class="d-flex align-items-center">
                    <div class="option-label me-3">
                      {{ ['A', 'B', 'C', 'D'][i-1] }}
                    </div>
                    <div class="option-text">
                      {{ currentQuestion['option_' + i] }}
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="d-flex justify-content-between mt-4">
                <button 
                  @click="previousQuestion" 
                  class="btn btn-outline-primary" 
                  :disabled="currentQuestionIndex === 0"
                >
                  <i class="bi bi-arrow-left me-2"></i> Previous
                </button>
                
                <button 
                  v-if="currentQuestionIndex === questions.length - 1"
                  @click="confirmSubmit = true"
                  class="btn btn-success"
                  :disabled="submitting"
                >
                  <i class="bi bi-check2 me-2"></i> Finish Quiz
                </button>
                
                <button 
                  v-else
                  @click="nextQuestion" 
                  class="btn btn-primary"
                >
                  Next <i class="bi bi-arrow-right ms-2"></i>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Mobile Submit Button -->
          <div class="d-block d-md-none mt-4">
            <button 
              @click="confirmSubmit = true" 
              class="btn btn-primary btn-lg w-100" 
              :disabled="submitting"
            >
              <span v-if="submitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Submit Quiz
            </button>
          </div>
        </div>
        
        <div class="col-12 col-lg-4">
          <div class="card shadow-sm mb-4">
            <div class="card-header bg-white py-3">
              <h6 class="mb-0">Question Navigator</h6>
            </div>
            <div class="card-body">
              <div class="question-grid">
                <button 
                  v-for="(_, index) in questions" 
                  :key="index"
                  class="question-number"
                  :class="{
                    'active': index === currentQuestionIndex,
                    'answered': userAnswers[index],
                    'unanswered': !userAnswers[index]
                  }"
                  @click="goToQuestion(index)"
                >
                  {{ index + 1 }}
                </button>
              </div>
              
              <div class="mt-3 d-flex">
                <div class="me-3 small">
                  <span class="status-indicator answered"></span> Answered
                </div>
                <div class="small">
                  <span class="status-indicator unanswered"></span> Unanswered
                </div>
              </div>
            </div>
          </div>
          
          <div class="card shadow-sm">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                  <h6 class="mb-1">Quiz Summary</h6>
                  <p class="text-muted small mb-0">{{ questions.length }} questions</p>
                </div>
                <div class="badge bg-primary">{{ quiz.total_marks }} marks</div>
              </div>
              
              <div class="progress mb-3" style="height: 8px;">
                <div 
                  class="progress-bar bg-success" 
                  role="progressbar" 
                  :style="{ width: `${answeredPercentage}%` }"
                  aria-valuenow="25" 
                  aria-valuemin="0" 
                  aria-valuemax="100"
                ></div>
              </div>
              
              <div class="d-flex justify-content-between small">
                <span>{{ answeredCount }}/{{ questions.length }} answered</span>
                <span>{{ unansweredCount }} remaining</span>
              </div>
              
              <button 
                @click="confirmSubmit = true" 
                class="btn btn-primary btn-lg w-100 mt-3 d-none d-lg-block" 
                :disabled="submitting"
              >
                <span v-if="submitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Submit Quiz
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Confirm Submit Modal -->
    <div class="modal fade" tabindex="-1" ref="submitModalRef" id="submitModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Submit Quiz</h5>
            <button 
              type="button" 
              class="btn-close" 
              data-bs-dismiss="modal" 
              aria-label="Close"
              @click="confirmSubmit = false"
            ></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to submit your quiz?</p>
            
            <div v-if="unansweredCount > 0" class="alert alert-warning">
              <i class="bi bi-exclamation-triangle me-2"></i>
              You have {{ unansweredCount }} unanswered questions.
            </div>
            
            <p class="mb-0">Once submitted, you cannot change your answers.</p>
          </div>
          <div class="modal-footer">
            <button 
              type="button" 
              class="btn btn-outline-secondary" 
              data-bs-dismiss="modal"
              @click="confirmSubmit = false"
            >
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="submitQuiz" 
              :disabled="submitting"
            >
              <span v-if="submitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Submit
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Time's Up Modal -->
    <div class="modal fade" tabindex="-1" ref="timeUpModalRef" id="timeUpModal" data-bs-backdrop="static" data-bs-keyboard="false">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title">Time's Up!</h5>
          </div>
          <div class="modal-body">
            <div class="text-center mb-4">
              <i class="bi bi-alarm-fill text-danger fs-1"></i>
              <h4 class="mt-3">Your time has expired</h4>
              <p>Your answers will be automatically submitted.</p>
            </div>
            <div class="d-flex justify-content-center">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<!-- The styles remain the same -->
<style scoped>
.quiz-attempt {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.quiz-header {
  position: sticky;
  top: 0;
  z-index: 100;
}

.timer {
  font-size: 1.2rem;
  font-weight: bold;
}

.question-text {
  font-size: 1.1rem;
  font-weight: 500;
}

.card {
  border-radius: 12px;
  border: none;
}

.options-list {
  margin-left: 0.5rem;
}

.option-item {
  cursor: pointer;
  border-radius: 0.5rem;
  background-color: #f8f9fa;
  border: 1px solid #e5e7eb;
  padding: 1rem;
  transition: all 0.2s;
}

.option-item:hover {
  background-color: #f0f0f0;
}

.option-item.selected {
  background-color: #e8f0fe;
  border-color: #4285f4;
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

.option-item.selected .option-label {
  background-color: #4285f4;
  color: white;
}

.question-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}

.question-number {
  width: 100%;
  aspect-ratio: 1;
  border: none;
  border-radius: 4px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.question-number.active {
  background-color: #4285f4;
  color: white;
}

.question-number.answered:not(.active) {
  background-color: #e8f0fe;
  color: #4285f4;
}

.question-number.unanswered:not(.active) {
  background-color: #f0f0f0;
  color: #5f6368;
}

.status-indicator {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 5px;
}

.status-indicator.answered {
  background-color: #4285f4;
}

.status-indicator.unanswered {
  background-color: #5f6368;
}

/* Responsive adjustments */
@media (max-width: 767.98px) {
  .timer {
    font-size: 1rem;
  }
  
  .question-text {
    font-size: 1rem;
  }
  
  .question-grid {
    grid-template-columns: repeat(8, 1fr);
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
}

@media (max-width: 575.98px) {
  .question-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}
</style>