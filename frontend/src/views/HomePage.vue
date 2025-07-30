<template>
  <div class="home">
    <NavBar />
    <HeroSection />
    <StatsSection />
    <FeaturesSection />
    <CTASection />
    <Footer />
  </div>
</template>

<script setup>
import NavBar from '@/components/common/NavBar.vue'
import HeroSection from '@/components/home/HeroSection.vue'
import StatsSection from '@/components/home/StatsSection.vue'
import FeaturesSection from '@/components/home/FeaturesSection.vue'
import CTASection from '@/components/home/CTASection.vue'
import Footer from '@/components/common/Footer.vue'
</script>

<style scoped>
/* Global Styles */
.home {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
  color: #2d3748;
}

/* Card Animations */
.card {
  background-color: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border-color: #cbd5e0;
}

/* Button Styles */
.btn {
  padding: 0.875rem 2rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background-color: #4338ca;
  border-color: #4338ca;
  color: white;
}

.btn-primary:hover {
  background-color: #3730a3;
  border-color: #3730a3;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(67, 56, 202, 0.3);
}

.btn-outline-dark {
  border: 2px solid #374151;
  color: #374151;
  background-color: transparent;
}

.btn-outline-dark:hover {
  background-color: #374151;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(55, 65, 81, 0.2);
}

.btn-light {
  background-color: white;
  border: 2px solid #e5e7eb;
  color: #374151;
}

.btn-light:hover {
  background-color: #f9fafb;
  border-color: #d1d5db;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

/* Badge Styles */
.badge {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: 20px;
  letter-spacing: 0.5px;
}

.badge-primary {
  background-color: #ddd6fe;
  color: #5b21b6;
}

/* Typography */
.display-4 {
  font-weight: 800;
  line-height: 1.2;
  color: #1a202c;
}

.lead {
  font-size: 1.125rem;
  font-weight: 400;
  color: #4a5568;
}

/* Section Spacing */
.py-section {
  padding: 5rem 0;
}

.py-section-sm {
  padding: 3rem 0;
}

/* Icon Styles */
.icon-feature {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.icon-primary {
  background-color: #eef2ff;
  color: #4338ca;
}

.icon-success {
  background-color: #ecfdf5;
  color: #059669;
}

.icon-warning {
  background-color: #fffbeb;
  color: #d97706;
}

.icon-info {
  background-color: #eff6ff;
  color: #2563eb;
}

/* Responsive Design */
@media (max-width: 768px) {
  .display-4 {
    font-size: 2.5rem;
  }
  
  .btn {
    padding: 0.75rem 1.5rem;
    font-size: 0.9rem;
  }
  
  .py-section {
    padding: 3rem 0;
  }
}

/* Smooth Scroll */
html {
  scroll-behavior: smooth;
}

/* Focus States */
.btn:focus,
.card:focus {
  outline: 2px solid #4338ca;
  outline-offset: 2px;
}

/* Loading States */
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Dark Mode Support */
@media (prefers-color-scheme: dark) {
  .home {
    background-color: #1a202c;
    color: #e2e8f0;
  }
  
  .card {
    background-color: #2d3748;
    border-color: #4a5568;
  }
  
  .btn-light {
    background-color: #2d3748;
    border-color: #4a5568;
    color: #e2e8f0;
  }
}
</style>