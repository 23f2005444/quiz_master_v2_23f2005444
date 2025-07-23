<template>
  <section class="testimonials py-5">
    <div class="container">
      <!-- Section Header -->
      <div class="text-center mb-5">
        <span class="badge bg-primary-subtle text-primary px-3 py-2 mb-3">
          Testimonials
        </span>
        <h2 class="display-6 fw-bold mb-3 text-dark">What Our Students Say</h2>
        <p class="lead text-secondary mx-auto" style="max-width: 600px;">
          Hear from our community of learners about their experience with QuizMaster
        </p>
      </div>

      <!-- Testimonials Grid -->
      <div class="row g-4">
        <div v-for="testimonial in testimonials" 
             :key="testimonial.id" 
             class="col-md-6 col-lg-4">
          <div class="testimonial-card h-100 p-4 bg-white rounded-4">
            <!-- Rating -->
            <div class="mb-3">
              <i v-for="n in 5" 
                 :key="n"
                 class="bi bi-star-fill text-warning me-1">
              </i>
            </div>

            <!-- Content -->
            <p class="testimonial-text mb-4">
              "{{ testimonial.content }}"
            </p>

            <!-- Author -->
            <div class="d-flex align-items-center">
              <img :src="testimonial.avatar" 
                   :alt="testimonial.name"
                   class="testimonial-avatar rounded-circle me-3">
              <div>
                <h6 class="mb-1 fw-bold text-dark">{{ testimonial.name }}</h6>
                <p class="mb-0 text-secondary small">{{ testimonial.subject }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Trust Badges -->
      <div class="row justify-content-center align-items-center mt-5 g-4">
        <div v-for="badge in trustBadges" 
             :key="badge.name" 
             class="col-6 col-md-3">
          <div class="text-center">
            <i :class="`bi ${badge.icon} text-primary fs-1 mb-3`"></i>
            <h6 class="fw-bold mb-1 text-dark">{{ badge.name }}</h6>
            <p class="text-secondary small mb-0">{{ badge.description }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const testimonials = [
  {
    id: 1,
    content: 'QuizMaster helped me ace my certification exam. The practice tests were spot-on!',
    name: 'Alex Thompson',
    subject: 'Computer Science',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=60&h=60&fit=crop&crop=face'
  },
  {
    id: 2,
    content: 'The progress tracking feature really helped me identify my weak areas and improve.',
    name: 'Sarah Parker',
    subject: 'Mathematics',
    avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=60&h=60&fit=crop&crop=face'
  },
  {
    id: 3,
    content: 'Excellent platform for self-paced learning. The interface is intuitive and user-friendly.',
    name: 'Michael Chen',
    subject: 'Physics',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=60&h=60&fit=crop&crop=face'
  }
]

const trustBadges = [
  {
    icon: 'bi-shield-check',
    name: 'Trusted Platform',
    description: 'By thousands of students'
  },
  {
    icon: 'bi-award',
    name: 'Quality Content',
    description: 'Expert-verified questions'
  },
  {
    icon: 'bi-clock-history',
    name: '24/7 Support',
    description: 'Always here to help'
  },
  {
    icon: 'bi-hand-thumbs-up',
    name: '95% Success Rate',
    description: 'Among active users'
  }
]
</script>

<style scoped>
.testimonials {
  background-color: var(--bs-light);
}

.testimonial-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(0,0,0,0.05);
}

.testimonial-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.testimonial-avatar {
  width: 48px;
  height: 48px;
  object-fit: cover;
}

.testimonial-text {
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--bs-secondary);
}

@media (max-width: 768px) {
  .testimonial-text {
    font-size: 0.9rem;
  }
}
</style>