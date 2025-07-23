<template>
  <section class="stats py-5 bg-light">
    <div class="container">
      <div class="row g-4">
        <div v-for="(stat, index) in stats" :key="index" class="col-sm-6 col-md-3">
          <div class="stat-card h-100 p-4 bg-white rounded-4 text-center">
            <div class="stat-icon mb-3">
              <i :class="`bi ${stat.icon} fs-2 text-primary`"></i>
            </div>
            <h3 class="stat-value fw-bold mb-2">{{ stat.value }}</h3>
            <p class="stat-label text-secondary mb-2">{{ stat.label }}</p>
            <small class="text-muted d-block">{{ stat.description }}</small>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const stats = [
  {
    icon: 'bi-people-fill',
    value: '10,000+',
    label: 'Active Students',
    description: 'Learning every day'
  },
  {
    icon: 'bi-book-fill',
    value: '50+',
    label: 'Subjects',
    description: 'Across disciplines'
  },
  {
    icon: 'bi-patch-check-fill',
    value: '1,000+',
    label: 'Quizzes',
    description: 'Comprehensive tests'
  },
  {
    icon: 'bi-trophy-fill',
    value: '5,000+',
    label: 'Certificates',
    description: 'Issued to date'
  }
]
</script>

<style scoped>
.stat-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(0,0,0,0.05);
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.stat-icon i {
  padding: 1rem;
  border-radius: 12px;
  background-color: var(--bs-primary-bg-subtle);
}

.stat-value {
  color: var(--bs-primary);
  font-size: 2rem;
}

@media (max-width: 768px) {
  .stat-value {
    font-size: 1.75rem;
  }
}
</style>