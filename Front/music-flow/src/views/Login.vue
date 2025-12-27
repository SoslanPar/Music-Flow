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

  
  window.addEventListener('message', async (event) => {
    // Проверяем origin сообщения для безопасности
    if (event.origin !== window.location.origin) return;
    
    if (event.data.type === 'yandex_auth_success') {
      try {
        const code = event.data.code;
        console.log('ПолученЯндекс:', event.data);
        console.log('Получен code от Яндекс:', code);
        
        // 1. Сохраняем токен в localStorage
        localStorage.setItem('yandex_token', code);
        
        // 2. Отправляем токен на сервер для валидации
        console.log(code);
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
        console.log('response:', response);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Ответ сервера:', result);
        
        // 3. Проверяем ответ сервера и перенаправляем
        if (result.success) {
          document.cookie = `user_id=${result.user_id}; path=/; SameSite=Lax`;
          router.push('/Main');
        } else {
          console.error('Сервер отклонил токен:', result.message);
          router.push('/login?error=invalid_token');
        }
        
      } catch (error) {
        console.error('Ошибка при обработке токена:', error);
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
  <div class="login-container">
    <div class="logo-section">
      <LogoInLogin />
    </div>
    <div class="form-section">
      <div ref="formContainer">
        <AuthForm :isLogin="isLogin" @toggle="toggleForm" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #1a1025 0%, #0d1a24 50%, #1a0f28 100%);
}

.logo-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

@media (max-width: 1024px) {
  .login-container {
    flex-direction: column;
    min-height: 100dvh;
  }
  
  .logo-section {
    flex: none;
    padding: 30px 20px 10px 20px;
  }
  
  .form-section {
    flex: 1;
    padding: 10px 20px 30px 20px;
    align-items: flex-start;
  }
}

@media (max-width: 600px) {
  .logo-section {
    padding: 20px 15px 5px 15px;
  }
  
  .logo-section :deep(svg) {
    width: 200px !important;
    height: auto !important;
  }
  
  .form-section {
    padding: 10px 15px 20px 15px;
  }
}

@media (max-width: 380px) {
  .logo-section :deep(svg) {
    width: 160px !important;
  }
}
</style>