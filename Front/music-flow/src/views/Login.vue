<script setup>
import { ref, onMounted } from 'vue';
import { gsap } from 'gsap';
import { useRouter } from 'vue-router';
import LogoInLogin from '@/assets/logo-in-login.vue';
import AuthForm from '@/components/auth-form.vue';
import YandexButton from '@/components/yandex-button.vue';

const router = useRouter();
const isLogin = ref(true);
const formContainer = ref(null);
const DOMAIN = import.meta.env.VITE_DOMAIN;


onMounted(() => {
  // Анимация появления
  gsap.from('.logo-section', { opacity: 0, y: -20, duration: 0.8, ease: 'power2.out' });
  gsap.from('.form-section', { opacity: 0, y: 20, duration: 0.8, delay: 0.2, ease: 'power2.out' });
  gsap.from('.decoration-circle', { scale: 0, opacity: 0, duration: 1.2, delay: 0.3, ease: 'elastic.out(1, 0.5)', stagger: 0.1 });
  
  window.addEventListener('message', async (event) => {
    // Проверяем origin сообщения для безопасности
    if (event.origin !== window.location.origin) return;
    
    if (event.data.type === 'yandex_auth_success') {
      try {
        const code = event.data.code;
        
        // 1. Сохраняем токен в localStorage
        localStorage.setItem('yandex_token', code);
        
        // 2. Отправляем токен на сервер для валидации
        const response = await fetch(
          `/api/auth/check_token?code=${encodeURIComponent(code)}`,
          {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include'
          }
        );
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        // 3. Проверяем ответ сервера и перенаправляем
        if (result.success) {
          document.cookie = `user_id=${result.user_id}; path=/; SameSite=Lax`;
          router.push('/Main');
        } else {
          router.push('/login?error=invalid_token');
        }
        
      } catch (error) {
        router.push('/login?error=auth_failed');
      }
    }
  });
});

function toggleForm() {
  setTimeout(() => {
    gsap.to(formContainer.value, {
      duration: 0.3,
      scale: 0.95,
      opacity: 0.8,
      ease: 'power2.in',
      onComplete: () => {
        isLogin.value = !isLogin.value;
        gsap.fromTo(formContainer.value,
          { scale: 1.05, opacity: 0.8 },
          { 
            duration: 0.4,
            scale: 1,
            opacity: 1,
            ease: 'power2.out'
          }
        );
      }
    });
  }, 100);
}
</script>

<template>
  <div class="login-page">
    <!-- Декоративные элементы -->
    <div class="decoration-circle circle-1"></div>
    <div class="decoration-circle circle-2"></div>
    <div class="decoration-circle circle-3"></div>
    
    <!-- Кнопка возврата на главную -->
    <router-link to="/" class="back-home">
      <span class="back-arrow">←</span>
      <span class="back-text">На главную</span>
    </router-link>
    
    <div class="login-container">
      <!-- Левая часть - Логотип -->
      <div class="logo-section">
        <div class="logo-wrapper">
          <LogoInLogin class="login-logo" />
          <p class="logo-tagline">Слушайте музыку вместе</p>
        </div>
      </div>
      
      <!-- Правая часть - Форма -->
      <div class="form-section">
        <div ref="formContainer" class="form-wrapper">
          <AuthForm :isLogin="isLogin" @toggle="toggleForm" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  min-height: 100dvh;
  width: 100%;
  background: linear-gradient(135deg, #1a1025 0%, #0d1a24 50%, #1a0f28 100%);
  position: relative;
  overflow: hidden;
}

/* Декоративные круги */
.decoration-circle {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
}

.circle-1 {
  width: clamp(200px, 40vw, 500px);
  height: clamp(200px, 40vw, 500px);
  background: radial-gradient(circle, rgba(0, 217, 231, 0.15) 0%, transparent 70%);
  top: -10%;
  right: -10%;
}

.circle-2 {
  width: clamp(150px, 30vw, 400px);
  height: clamp(150px, 30vw, 400px);
  background: radial-gradient(circle, rgba(208, 188, 255, 0.12) 0%, transparent 70%);
  bottom: -5%;
  left: -5%;
}

.circle-3 {
  width: clamp(100px, 20vw, 300px);
  height: clamp(100px, 20vw, 300px);
  background: radial-gradient(circle, rgba(255, 107, 157, 0.1) 0%, transparent 70%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* Кнопка возврата */
.back-home {
  position: fixed;
  top: clamp(12px, 2vw, 20px);
  left: clamp(12px, 2vw, 20px);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: clamp(8px, 1.5vw, 12px) clamp(12px, 2vw, 18px);
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 50px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: clamp(0.8rem, 1.5vw, 0.95rem);
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  z-index: 100;
}

.back-home:hover {
  background: rgba(255, 255, 255, 0.12);
  color: white;
  transform: translateX(-3px);
  border-color: rgba(0, 217, 231, 0.3);
}

.back-arrow {
  font-size: 1.1em;
  transition: transform 0.3s ease;
}

.back-home:hover .back-arrow {
  transform: translateX(-3px);
}

/* Контейнер */
.login-container {
  display: flex;
  min-height: 100vh;
  min-height: 100dvh;
  width: 100%;
  position: relative;
  z-index: 1;
}

/* Секция логотипа */
.logo-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(20px, 4vw, 60px);
}

.logo-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: clamp(0.75rem, 2vw, 1.5rem);
  text-align: center;
}

.login-logo {
  width: clamp(180px, 25vw, 400px);
  height: auto;
}

.login-logo :deep(svg) {
  width: 100% !important;
  height: auto !important;
}

.logo-tagline {
  font-size: clamp(1rem, 2vw, 1.5rem);
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  background: linear-gradient(90deg, #00d9e7, #D0BCFF);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.feature-icon {
  font-size: 1.1em;
}

/* Секция формы */
.form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(20px, 4vw, 60px);
}

.form-wrapper {
  width: 100%;
  max-width: min(450px, 90vw);
}

/* ==================== RESPONSIVE ==================== */

/* Большие десктопы (1440px+) */
@media (min-width: 1440px) {
  .login-logo {
    width: 450px;
  }
  
  .form-wrapper {
    max-width: 480px;
  }
}

/* Десктопы (1024px - 1439px) */
@media (min-width: 1024px) and (max-width: 1439px) {
  .logo-section {
    padding: 40px;
  }
  
  .form-section {
    padding: 40px;
  }
}

/* Планшеты вертикально (768px - 1023px) */
@media (min-width: 768px) and (max-width: 1023px) {
  .login-container {
    flex-direction: column;
    justify-content: center;
    gap: 1rem;
  }
  
  .logo-section {
    flex: none;
    padding: 80px 30px 20px 30px;
  }
  
  .login-logo {
    width: 280px;
  }
  
  .form-section {
    flex: none;
    padding: 20px 30px 40px 30px;
  }
  
  .form-wrapper {
    max-width: 420px;
  }
}

/* Мобильные (481px - 767px) */
@media (min-width: 481px) and (max-width: 767px) {
  .login-container {
    flex-direction: column;
    justify-content: flex-start;
  }
  
  .logo-section {
    flex: none;
    padding: 70px 20px 15px 20px;
  }
  
  .login-logo {
    width: 220px;
  }
  
  .logo-tagline {
    font-size: 1.1rem;
  }
  
  .form-section {
    flex: 1;
    padding: 15px 20px 30px 20px;
    align-items: flex-start;
  }
  
  .form-wrapper {
    max-width: 400px;
    margin: 0 auto;
  }
}

/* Маленькие мобильные (до 480px) */
@media (max-width: 480px) {
  .login-container {
    flex-direction: column;
    justify-content: flex-start;
  }
  
  .logo-section {
    flex: none;
    padding: 55px 15px 10px 15px;
  }
  
  .login-logo {
    width: 160px;
  }
  
  .logo-tagline {
    font-size: 0.95rem;
  }
  
  .form-section {
    flex: 1;
    padding: 10px 15px 25px 15px;
    align-items: flex-start;
  }
  
  .back-text {
    display: none;
  }
  
  .back-arrow {
    font-size: 1.3em;
  }
  
  .back-home {
    padding: 10px 14px;
  }
}

/* Очень маленькие экраны (до 360px) */
@media (max-width: 360px) {
  .logo-section {
    padding: 50px 10px 8px 10px;
  }
  
  .login-logo {
    width: 140px;
  }
  
  .logo-tagline {
    font-size: 0.85rem;
  }
  
  .form-section {
    padding: 8px 10px 20px 10px;
  }
}

/* Горизонтальная ориентация на мобильных (низкая высота) */
@media (max-height: 600px) and (orientation: landscape) {
  .login-page {
    min-height: 100vh;
    min-height: 100dvh;
    overflow-y: auto;
    overflow-x: hidden;
  }
  
  .login-container {
    flex-direction: row;
    align-items: center;
    justify-content: center;
    gap: clamp(1.5rem, 5vw, 4rem);
    padding: 10px clamp(15px, 4vw, 50px);
    min-height: 100vh;
    min-height: 100dvh;
  }
  
  .logo-section {
    flex: 0 0 auto;
    padding: 10px;
    max-width: 35vw;
  }
  
  .logo-wrapper {
    gap: 0.5rem;
  }
  
  .login-logo {
    width: clamp(100px, 20vh, 180px);
  }
  
  .logo-tagline {
    font-size: clamp(0.75rem, 2vh, 1rem);
  }
  
  .form-section {
    flex: 0 1 auto;
    padding: 10px;
    align-items: center;
    max-width: 55vw;
  }
  
  .form-wrapper {
    max-width: clamp(260px, 45vw, 380px);
    width: 100%;
  }
  
  .circle-1, .circle-2, .circle-3 {
    opacity: 0.2;
  }
  
  .back-home {
    top: 8px;
    left: 8px;
    padding: 6px 10px;
  }
  
  .back-text {
    display: none;
  }
}

/* Очень низкая высота (телефоны в ландшафте) */
@media (max-height: 450px) and (orientation: landscape) {
  .login-page {
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .login-container {
    gap: clamp(1rem, 4vw, 2.5rem);
    padding: 8px clamp(10px, 3vw, 40px);
    min-height: max(100vh, 320px);
    min-height: max(100dvh, 320px);
  }
  
  .logo-section {
    padding: 8px;
    max-width: 30vw;
  }
  
  .logo-wrapper {
    gap: 0.35rem;
  }
  
  .login-logo {
    width: clamp(300px, 200vh, 200px);
  }
  
  .logo-tagline {
    font-size: clamp(0.65rem, 1.8vh, 0.9rem);
  }
  
  .form-section {
    padding: 10px;
    max-width: 80vw;
  }
  
  .form-wrapper {
    max-width: clamp(240px, 50vw, 340px);
  }
  
  .back-home {
    top: 5px;
    left: 5px;
    padding: 5px 8px;
    font-size: 0.75rem;
  }
}

/* Экстремально низкая высота (менее 380px) */
@media (max-height: 380px) and (orientation: landscape) {
  .login-container {
    gap: clamp(0.75rem, 3vw, 2rem);
    padding: 5px clamp(8px, 2vw, 30px);
  }
  
  .logo-section {
    padding: 5px;
    max-width: 25vw;
  }
  
  .login-logo {
    width: clamp(60px, 15vh, 100px);
  }
  
  .logo-tagline {
    font-size: clamp(0.6rem, 1.5vh, 0.8rem);
    display: none;
  }
  
  .form-section {
    padding: 5px;
    max-width: 65vw;
  }
  
  .form-wrapper {
    max-width: clamp(220px, 55vw, 320px);
  }
  
  .circle-1, .circle-2, .circle-3 {
    display: none;
  }
  
  .back-home {
    top: 3px;
    left: 3px;
    padding: 4px 6px;
  }
}

/* Высокие экраны (десктоп с большой высотой) */
@media (min-height: 900px) and (min-width: 1024px) {
  .login-container {
    align-items: center;
  }
  
  .logo-wrapper {
    gap: 2rem;
  }
}

/* Ультраширокие мониторы */
@media (min-width: 1920px) {
  .login-container {
    max-width: 1600px;
    margin: 0 auto;
  }
  
  .login-logo {
    width: 500px;
  }
  
  .form-wrapper {
    max-width: 500px;
  }
}

/* Масштабирование системы (zoom) - поддержка через относительные единицы уже встроена */
/* Доступность: уменьшенное движение */
@media (prefers-reduced-motion: reduce) {
  .decoration-circle {
    animation: none;
  }
  
  .back-home,
  .feature-item {
    transition: none;
  }
}
</style>