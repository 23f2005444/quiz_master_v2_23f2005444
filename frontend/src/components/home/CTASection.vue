<template>
  <section class="cta py-5 bg-primary">
    <div class="container">
      <div class="row align-items-center g-4">
        <!-- CTA Content -->
        <div class="col-lg-7">
          <div class="mb-4">
            <span class="badge bg-white text-primary px-3 py-2">
              <i class="bi bi-rocket-takeoff-fill me-2"></i>
              Start Learning Today
            </span>
          </div>
          <h2 class="display-6 fw-bold text-white mb-4">
            Ready to Begin Your Learning Journey?
          </h2>
          <p class="lead text-white opacity-75 mb-4">
            Join thousands of students who trust QuizMaster for their exam preparation.
            Start learning, track your progress, and achieve your goals.
          </p>
          
          <!-- Features List -->
          <div class="d-flex flex-wrap gap-4 mb-4">
            <div v-for="feature in features" 
                 :key="feature"
                 class="d-flex align-items-center">
              <i class="bi bi-check-circle-fill text-white me-2"></i>
              <span class="text-white opacity-75">{{ feature }}</span>
            </div>
          </div>
        </div>

        <!-- CTA Card -->
        <div class="col-lg-5">
          <div class="cta-card bg-white p-4 rounded-3 text-dark">
            <h4 class="fw-bold mb-4">Create Your Free Account</h4>
            <div class="d-grid gap-3">
              <RouterLink to="/register" class="btn btn-primary btn-lg fw-medium">
                Sign Up Now
              </RouterLink>
              <RouterLink to="/login" class="btn btn-outline-primary btn-lg fw-medium">
                Login to Your Account
              </RouterLink>
            </div>
            <p class="text-center text-secondary small mt-4 mb-0">
              No credit card required. Cancel anytime.
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { RouterLink } from 'vue-router'

const features = [
  'Interactive quizzes',
  'Progress tracking',
  'Personalized feedback'
]
</script>

<style scoped>
.cta {
  background-color: var(--bs-primary);
}

.cta-card {
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.btn-lg {
  padding: 0.875rem 1.5rem;
  font-size: 1rem;
}

@media (max-width: 991.98px) {
  .cta {
    text-align: center;
  }
  
  .d-flex.flex-wrap {
    justify-content: center;
  }
}
</style>