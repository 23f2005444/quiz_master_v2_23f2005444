<template>
  <footer class="footer py-5 bg-light">
    <div class="container">
      <!-- Footer Content -->
      <div class="row g-4 mb-5">
        <!-- Brand -->
        <div class="col-lg-4 mb-4 mb-lg-0">
          <RouterLink to="/" class="d-flex align-items-center text-decoration-none mb-3">
            <div class="footer-logo me-2">
              <i class="bi bi-mortarboard-fill text-primary"></i>
            </div>
            <span class="h5 fw-bold text-dark mb-0">QuizMaster</span>
          </RouterLink>
          <p class="text-secondary mb-4">
            Empowering students through interactive learning and comprehensive assessments.
          </p>
          <div class="d-flex gap-3">
            <a href="#" class="text-secondary">
              <i class="bi bi-facebook"></i>
            </a>
            <a href="#" class="text-secondary">
              <i class="bi bi-twitter"></i>
            </a>
            <a href="#" class="text-secondary">
              <i class="bi bi-linkedin"></i>
            </a>
          </div>
        </div>

        <!-- Quick Links -->
        <div class="col-6 col-lg-2">
          <h6 class="fw-bold mb-3 text-dark">Platform</h6>
          <ul class="list-unstyled">
            <li class="mb-2">
              <RouterLink to="/subjects" class="text-secondary text-decoration-none">Subjects</RouterLink>
            </li>
            <li class="mb-2">
              <RouterLink to="/features" class="text-secondary text-decoration-none">Features</RouterLink>
            </li>
            <li class="mb-2">
              <RouterLink to="/pricing" class="text-secondary text-decoration-none">Pricing</RouterLink>
            </li>
          </ul>
        </div>

        <!-- Company -->
        <div class="col-6 col-lg-2">
          <h6 class="fw-bold mb-3 text-dark">Company</h6>
          <ul class="list-unstyled">
            <li class="mb-2">
              <RouterLink to="/about" class="text-secondary text-decoration-none">About</RouterLink>
            </li>
            <li class="mb-2">
              <RouterLink to="/contact" class="text-secondary text-decoration-none">Contact</RouterLink>
            </li>
            <li class="mb-2">
              <RouterLink to="/careers" class="text-secondary text-decoration-none">Careers</RouterLink>
            </li>
          </ul>
        </div>

        <!-- Resources -->
        <div class="col-6 col-lg-2">
          <h6 class="fw-bold mb-3 text-dark">Resources</h6>
          <ul class="list-unstyled">
            <li class="mb-2">
              <RouterLink to="/blog" class="text-secondary text-decoration-none">Blog</RouterLink>
            </li>
            <li class="mb-2">
              <RouterLink to="/help" class="text-secondary text-decoration-none">Help Center</RouterLink>
            </li>
            <li class="mb-2">
              <RouterLink to="/faq" class="text-secondary text-decoration-none">FAQ</RouterLink>
            </li>
          </ul>
        </div>

        <!-- Legal -->
        <div class="col-6 col-lg-2">
          <h6 class="fw-bold mb-3 text-dark">Legal</h6>
          <ul class="list-unstyled">
            <li class="mb-2">
              <RouterLink to="/privacy" class="text-secondary text-decoration-none">Privacy</RouterLink>
            </li>
            <li class="mb-2">
              <RouterLink to="/terms" class="text-secondary text-decoration-none">Terms</RouterLink>
            </li>
            <li class="mb-2">
              <RouterLink to="/cookies" class="text-secondary text-decoration-none">Cookies</RouterLink>
            </li>
          </ul>
        </div>
      </div>

      <!-- Footer Bottom -->
      <div class="border-top pt-4">
        <div class="row align-items-center">
          <div class="col-md-6 text-center text-md-start mb-3 mb-md-0">
            <p class="small text-secondary mb-0">
              © {{ new Date().getFullYear() }} QuizMaster. All rights reserved.
            </p>
          </div>
          <div class="col-md-6 text-center text-md-end">
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.footer {
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.footer-logo {
  width: 36px;
  height: 36px;
  background-color: var(--bs-primary-bg-subtle);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
}

.text-secondary {
  transition: color 0.2s ease;
}

.text-secondary:hover {
  color: var(--bs-primary) !important;
}

.payment-methods {
  opacity: 0.5;
}

@media (max-width: 991.98px) {
  .mb-lg-4 {
    margin-bottom: 2rem !important;
  }
}
</style>