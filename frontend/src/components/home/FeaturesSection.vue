<template>
  <section class="features py-5">
    <div class="container">
      <!-- Section Header -->
      <div class="text-center mb-5">
        <span class="badge bg-primary-subtle text-primary px-3 py-2 mb-3">
          Platform Features
        </span>
        <h2 class="display-6 fw-bold mb-3 text-dark">Why Choose QuizMaster?</h2>
        <p class="lead text-secondary mx-auto" style="max-width: 600px;">
          Discover powerful features designed to enhance your learning experience
        </p>
      </div>

      <!-- Features Grid -->
      <div class="row g-4">
        <div v-for="(feature, index) in features" 
             :key="index" 
             class="col-md-6 col-lg-4">
          <div class="feature-card h-100 p-4 bg-white rounded-4">
            <div class="feature-icon mb-4">
              <i :class="`bi ${feature.icon} text-primary fs-3`"></i>
            </div>
            <h4 class="fw-bold mb-3 text-dark">{{ feature.title }}</h4>
            <p class="text-secondary mb-4">{{ feature.description }}</p>
            <ul class="feature-list list-unstyled mb-0">
              <li v-for="(item, idx) in feature.items" 
                  :key="idx"
                  class="d-flex align-items-center mb-2">
                <i class="bi bi-check-circle-fill text-success me-2"></i>
                <span class="text-secondary">{{ item }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const features = [
  {
    icon: 'bi-lightning-charge-fill',
    title: 'Interactive Learning',
    description: 'Engage with dynamic quizzes that adapt to your learning style.',
    items: [
      'Real-time feedback',
      'Adaptive difficulty',
      'Progress tracking',
      'Performance analytics'
    ]
  },
  {
    icon: 'bi-graph-up',
    title: 'Progress Tracking',
    description: 'Monitor your performance with detailed analytics and insights.',
    items: [
      'Visual statistics',
      'Learning patterns',
      'Improvement areas',
      'Achievement badges'
    ]
  },
  {
    icon: 'bi-shield-check',
    title: 'Comprehensive Tests',
    description: 'Access a wide range of carefully curated quiz content.',
    items: [
      'Multiple subjects',
      'Various difficulty levels',
      'Timed assessments',
      'Practice mode'
    ]
  },
  {
    icon: 'bi-trophy',
    title: 'Certifications',
    description: 'Earn recognition for your achievements and expertise.',
    items: [
      'Digital certificates',
      'Shareable badges',
      'Achievement tracking',
      'Skill validation'
    ]
  },
  {
    icon: 'bi-people',
    title: 'Community Learning',
    description: 'Connect with fellow learners and share knowledge.',
    items: [
      'Discussion forums',
      'Study groups',
      'Peer support',
      'Knowledge sharing'
    ]
  },
  {
    icon: 'bi-device-hdd',
    title: 'Accessible Platform',
    description: 'Learn anywhere, anytime with our flexible platform.',
    items: [
      'Mobile friendly',
      'Offline access',
      '24/7 availability',
      'Cross-device sync'
    ]
  }
]
</script>

<style scoped>
.features {
  background-color: var(--bs-light);
}

.feature-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(0,0,0,0.05);
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.feature-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background-color: var(--bs-primary-bg-subtle);
}

.feature-list li {
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .feature-card {
    text-align: center;
  }

  .feature-icon {
    margin: 0 auto;
  }
}
</style>