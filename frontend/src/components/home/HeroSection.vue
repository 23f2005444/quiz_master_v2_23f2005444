<template>
  <section class="hero">
    <div class="container py-5">
      <!-- Left Content -->
      <div class="row align-items-center">
        <div class="col-lg-6 mb-5 mb-lg-0">
          <!-- Badge -->
          <div class="mb-4">
            <span class="badge bg-primary-subtle text-primary px-3 py-2">
              <i class="bi bi-mortarboard-fill me-2"></i>
              Educational Platform
            </span>
          </div>

          <!-- Heading -->
          <h1 class="display-4 fw-bold text-dark mb-4">
            Master Your Knowledge with
            <span class="text-primary d-block">Interactive Quizzes</span>
          </h1>

          <!-- Description -->
          <p class="lead text-secondary mb-4">
            Join thousands of students improving their skills through our comprehensive 
            quiz platform. Test your knowledge, track progress, and achieve your goals.
          </p>

          <!-- Features List -->
          <div class="mb-5">
            <div class="d-flex align-items-center mb-3" v-for="feature in features" :key="feature">
              <div class="feature-icon me-3">
                <i class="bi bi-check-circle-fill text-success"></i>
              </div>
              <span class="text-secondary">{{ feature }}</span>
            </div>
          </div>

          <!-- CTA Buttons -->
          <div class="d-flex flex-wrap gap-3 mb-5">
            <RouterLink to="/register" class="btn btn-primary">
              <i class="bi bi-rocket-takeoff-fill me-2"></i>
              Start Learning
            </RouterLink>
            <RouterLink to="/subjects" class="btn btn-outline-primary">
              <i class="bi bi-book-fill me-2"></i>
              Browse Subjects
            </RouterLink>
          </div>

          <!-- Stats -->
          <div class="row g-4">
            <div class="col-4" v-for="stat in stats" :key="stat.value">
              <div class="text-center p-3 rounded-3 bg-white shadow-sm">
                <h3 class="fw-bold text-primary mb-1">{{ stat.value }}</h3>
                <p class="text-secondary small mb-0">{{ stat.label }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Content - Quiz Demo -->
        <div class="col-lg-6 position-relative">
          <div class="quiz-demo p-4 bg-white rounded-4 shadow-lg">
            <!-- Quiz Header -->
            <div class="quiz-header mb-4">
              <div class="d-flex align-items-center justify-content-between mb-3">
                <span class="badge bg-primary-subtle text-primary px-3 py-2">
                  JavaScript Fundamentals
                </span>
                <span class="badge bg-success-subtle text-success px-3 py-2">
                  <i class="bi bi-clock me-1"></i>
                  15:00
                </span>
              </div>
              <div class="progress" style="height: 8px;">
                <div class="progress-bar bg-primary" style="width: 60%"></div>
              </div>
            </div>

            <!-- Quiz Question -->
            <div class="quiz-content">
              <p class="fw-medium mb-3 text-dark">What is the output of console.log(typeof null)?</p>
              <div class="d-flex flex-column gap-2">
                <button 
                  v-for="option in options" 
                  :key="option.value"
                  class="btn btn-outline-light text-start p-3"
                  :class="{ 'active': option.selected }"
                >
                  {{ option.label }}
                </button>
              </div>
            </div>

            <!-- Floating Achievement Cards -->
            <div class="achievement-cards">
              <div v-for="card in achievementCards" 
                   :key="card.title"
                   class="achievement-card text-dark"
                   :class="card.position">
                <div class="d-flex align-items-center">
                  <div class="icon-wrapper" :class="card.iconBg">
                    <i :class="card.icon"></i>
                  </div>
                  <div class="ms-3">
                    <h6 class="mb-0">{{ card.title }}</h6>
                    <small class="text-secondary">{{ card.subtitle }}</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const features = ref([
  'Multiple subjects and topics available',
  'Real-time progress tracking',
  'Performance analytics and insights'
])

const stats = ref([
  { value: '50+', label: 'Subjects' },
  { value: '1000+', label: 'Quizzes' },
  { value: '10K+', label: 'Students' }
])

const options = ref([
  { value: 'null', label: 'A. "null"', selected: false },
  { value: 'object', label: 'B. "object"', selected: true },
  { value: 'undefined', label: 'C. "undefined"', selected: false },
  { value: 'boolean', label: 'D. "boolean"', selected: false }
])

const achievementCards = ref([
  {
    title: 'Achievement',
    subtitle: 'Quiz Master',
    icon: 'bi bi-trophy-fill text-white',
    iconBg: 'bg-primary',
    position: 'top-left'
  },
  {
    title: 'Progress',
    subtitle: '85% Complete',
    icon: 'bi bi-graph-up-arrow text-white',
    iconBg: 'bg-success',
    position: 'top-right'
  },
  {
    title: 'Streak',
    subtitle: '7 Days',
    icon: 'bi bi-lightning-fill text-white',
    iconBg: 'bg-warning',
    position: 'bottom-left'
  }
])
</script>

<style scoped>
.hero {
  background-color: #f8f9fa;
  min-height: 100vh;
  display: flex;
  align-items: center;
}

.feature-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quiz-demo {
  position: relative;
  max-width: 500px;
  margin: 0 auto;
}

.achievement-card {
  position: absolute;
  background: white;
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  animation: float 3s ease-in-out infinite;
}

.top-left {
  top: -20px;
  left: -20px;
  animation-delay: 0s;
}

.top-right {
  top: 20%;
  right: -20px;
  animation-delay: 1s;
}

.bottom-left {
  bottom: 10%;
  left: -20px;
  animation-delay: 2s;
}

.icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-outline-light {
  border-color: #dee2e6;
  color: #212529;
}

.btn-outline-light:hover,
.btn-outline-light.active {
  background-color: #e9ecef;
  border-color: #0d6efd;
  color: #0d6efd;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

@media (max-width: 991.98px) {
  .hero {
    min-height: auto;
    padding: 4rem 0;
  }

  .achievement-card {
    display: none;
  }

  .quiz-demo {
    margin-top: 3rem;
  }
}

@media (max-width: 575.98px) {
  .d-flex.flex-wrap {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>