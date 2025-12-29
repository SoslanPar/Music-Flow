  <script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import Button from '@/components/Button.vue'
import YandexButton from './yandex-button.vue'
import { authApi } from '@/utils/api.js'

const router = useRouter()

const props = defineProps({
  isLogin: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['toggle'])

const showYandexBtn = ref(true)
const username = ref('')
const email = ref('')
const password = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const isLoading = ref(false)

watch(() => props.isLogin, (newVal) => {
  errorMessage.value = ''
  successMessage.value = ''
  if (!newVal) {
    showYandexBtn.value = false
  } else {
    setTimeout(() => {
      showYandexBtn.value = true
    }, 150)
  }
})

/**
 * Валидация формы регистрации
 */
function validateSignUp() {
  if (!email.value || !password.value || !username.value) {
    errorMessage.value = 'Заполните все поля'
    return false
  }
  
  if (username.value.length < 3) {
    errorMessage.value = 'Имя пользователя должно быть не менее 3 символов'
    return false
  }
  
  if (password.value.length < 6) {
    errorMessage.value = 'Пароль должен быть не менее 6 символов'
    return false
  }
  
  // Простая валидация email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email.value)) {
    errorMessage.value = 'Введите корректный email'
    return false
  }
  
  return true
}

/**
 * Валидация формы входа
 */
function validateSignIn() {
  if (!email.value || !password.value) {
    errorMessage.value = 'Заполните все поля'
    return false
  }
  return true
}

async function handleSubmit() {
  errorMessage.value = ''
  successMessage.value = ''
  
  isLoading.value = true
  
  try {
    if (props.isLogin) {
      // Вход
      if (!validateSignIn()) {
        isLoading.value = false
        return
      }
      
      const result = await authApi.signIn(email.value, password.value)
      
      if (result.success) {
        document.cookie = `user_id=${result.user_id}; path=/; SameSite=Lax`
        router.push('/main')
      } else {
        errorMessage.value = result.message || 'Неверный логин или пароль'
      }
    } else {
      // Регистрация
      if (!validateSignUp()) {
        isLoading.value = false
        return
      }
      
      const result = await authApi.signUp(email.value, username.value, password.value)
      
      if (result.success) {
        successMessage.value = 'Регистрация успешна! Выполняется вход...'
        document.cookie = `user_id=${result.user_id}; path=/; SameSite=Lax`
        
        // Небольшая задержка для показа сообщения
        setTimeout(() => {
          router.push('/main')
        }, 1000)
      } else {
        errorMessage.value = result.message || 'Ошибка регистрации'
      }
    }
  } catch (error) {
    console.error('Auth error:', error)
    errorMessage.value = error.message || 'Ошибка авторизации'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <form class="auth-form" @submit.prevent="handleSubmit">
    <h2 class="welcome-title">
      {{ isLogin ? 'С возвращением!' : 'Добро пожаловать!' }}
    </h2>

    <div class="form-fields">
      <input
        v-if="!isLogin"
        v-model="username"
        type="text"
        placeholder="Имя пользователя"
        class="auth-input"
        key="username"
      />
      <input 
        v-model="email" 
        type="email" 
        :placeholder="isLogin ? 'Email' : 'Электронная почта'" 
        class="auth-input" 
      />
      <input 
        v-model="password" 
        type="password" 
        placeholder="Пароль" 
        class="auth-input" 
      />
    </div>

    <!-- Сообщение об ошибке -->
    <transition name="fade">
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </transition>

    <!-- Сообщение об успехе -->
    <transition name="fade">
      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>
    </transition>

    <div class="form-button">
      <Button 
        :text="isLoading ? 'Загрузка...' : (isLogin ? 'Войти' : 'Зарегистрироваться')" 
        textSize="28px"
        :disabled="isLoading"
        @click="handleSubmit"
      />
    </div>

    <YandexButton v-show="isLogin && showYandexBtn" :key="'yandex-btn'" />
    
    <div class="login-bottom-text cursor-pointer" @click="emit('toggle')">
      {{ isLogin ? 'Регистрация' : 'Уже есть аккаунт? Войти' }}
    </div>
  </form>
</template>

<style scoped>
.auth-form {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: clamp(14px, 2.5vw, 24px);
  padding: clamp(24px, 4vw, 45px);
  background: rgba(23, 18, 34, 0.75);
  backdrop-filter: blur(15px);
  border-radius: clamp(20px, 4vw, 35px);
  border: 1px solid rgba(0, 217, 231, 0.15);
  max-width: 450px;
  width: 100%;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.welcome-title {
  font-size: clamp(1.4rem, 4vw, 2.2rem);
  font-weight: bold;
  color: white;
  text-align: center;
  margin-bottom: clamp(5px, 1vw, 12px);
  text-shadow: 0 0 20px rgba(0, 217, 231, 0.4);
  background: linear-gradient(135deg, #ffffff 0%, #D0BCFF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.form-fields {
  display: flex;
  flex-direction: column;
  gap: clamp(10px, 2vw, 16px);
  width: 100%;
}

.auth-input {
  width: 100%;
  padding: clamp(12px, 2vw, 16px) clamp(18px, 3vw, 26px);
  border-radius: 50px;
  border: 2px solid rgba(160, 85, 245, 0.2);
  background: rgba(160, 85, 245, 0.08);
  color: white;
  outline: none;
  font-size: clamp(14px, 2vw, 16px);
  transition: all 0.5s ease;
  box-sizing: border-box;
}

.auth-input:focus {
  border-color: rgba(0, 217, 231, 0.5);
  background: rgba(160, 85, 245, 0.12);
  box-shadow: 0 0 20px rgba(0, 217, 231, 0.15);
}

/* Плавное выделение текста */
.auth-input::selection {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.auth-input::-moz-selection {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.auth-input::placeholder {
  color: rgba(255, 255, 255, 0.45);
}

.error-message {
  padding: clamp(10px, 1.5vw, 14px) clamp(14px, 2vw, 20px);
  background: rgba(255, 82, 82, 0.15);
  border: 1px solid rgba(255, 82, 82, 0.25);
  border-radius: 12px;
  color: #ff8a8a;
  text-align: center;
  font-size: clamp(12px, 1.5vw, 14px);
  width: 100%;
  box-sizing: border-box;
}

.success-message {
  padding: clamp(10px, 1.5vw, 14px) clamp(14px, 2vw, 20px);
  background: rgba(82, 255, 123, 0.15);
  border: 1px solid rgba(82, 255, 123, 0.25);
  border-radius: 12px;
  color: #8affb0;
  text-align: center;
  font-size: clamp(12px, 1.5vw, 14px);
  width: 100%;
  box-sizing: border-box;
}

.form-button {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-top: clamp(4px, 1vw, 8px);
  padding: 0 5px;
  box-sizing: border-box;
}

.form-button :deep(.button) {
  font-size: clamp(14px, 3.5vw, 22px) !important;
  padding: clamp(10px, 2vw, 16px) clamp(20px, 5vw, 40px) !important;
  max-width: 100%;
  white-space: nowrap;
}

.login-bottom-text {
  color: rgba(255, 255, 255, 0.6);
  font-size: clamp(12px, 1.5vw, 15px);
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 4px 8px;
  border-radius: 8px;
}

.login-bottom-text:hover {
  color: white;
  background: rgba(255, 255, 255, 0.05);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Планшеты вертикально */
@media (min-width: 768px) and (max-width: 1023px) {
  .auth-form {
    padding: 35px;
    gap: 18px;
  }
  
  .welcome-title {
    font-size: 1.8rem;
  }
  
  .auth-input {
    padding: 14px 22px;
    font-size: 15px;
  }
}

/* Мобильные */
@media (max-width: 480px) {
  .auth-form {
    padding: 22px 18px;
    border-radius: 22px;
    gap: 14px;
  }
  
  .welcome-title {
    font-size: 1.3rem;
    margin-bottom: 4px;
  }
  
  .form-fields {
    gap: 10px;
  }
  
  .auth-input {
    padding: 12px 18px;
    font-size: 14px;
  }
  
  .error-message,
  .success-message {
    padding: 10px 14px;
    font-size: 12px;
    border-radius: 10px;
  }
  
  .login-bottom-text {
    font-size: 12px;
  }
}

/* Очень маленькие экраны */
@media (max-width: 360px) {
  .auth-form {
    padding: 18px 14px;
    border-radius: 18px;
    gap: 12px;
  }
  
  .welcome-title {
    font-size: 1.15rem;
  }
  
  .auth-input {
    padding: 10px 14px;
    font-size: 12px;
  }
}

/* Горизонтальная ориентация на мобильных */
@media (max-height: 600px) and (orientation: landscape) {
  .auth-form {
    padding: clamp(10px, 2.5vh, 20px) clamp(14px, 3.5vw, 24px);
    gap: clamp(6px, 1.5vh, 12px);
    max-width: 100%;
    border-radius: clamp(14px, 3vh, 24px);
    max-height: calc(100vh - 20px);
    max-height: calc(100dvh - 20px);
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .welcome-title {
    font-size: clamp(0.95rem, 3.5vh, 1.4rem);
    margin-bottom: 0;
  }
  
  .form-fields {
    gap: clamp(6px, 1.5vh, 10px);
  }
  
  .auth-input {
    padding: clamp(8px, 2vh, 12px) clamp(12px, 2.5vw, 18px);
    font-size: clamp(12px, 2vh, 14px);
  }
  
  .error-message,
  .success-message {
    padding: 6px 12px;
    font-size: 11px;
  }
  
  .form-button {
    margin-top: clamp(2px, 0.5vh, 6px);
  }
  
  .form-button :deep(.button) {
    font-size: clamp(12px, 2.5vh, 16px) !important;
    padding: clamp(8px, 2vh, 12px) clamp(16px, 3.5vw, 30px) !important;
  }
  
  .login-bottom-text {
    font-size: 11px;
    padding: 2px 6px;
  }
}

/* Очень низкая высота */
@media (max-height: 450px) and (orientation: landscape) {
  .auth-form {
    padding: clamp(6px, 2vh, 14px) clamp(10px, 2.5vw, 18px);
    gap: clamp(4px, 1.2vh, 8px);
    border-radius: clamp(10px, 2.5vh, 18px);
    max-height: calc(100vh - 16px);
    max-height: calc(100dvh - 16px);
  }
  
  .welcome-title {
    font-size: clamp(0.85rem, 3vh, 1.1rem);
    margin-bottom: 0;
  }
  
  .form-fields {
    gap: clamp(4px, 1.2vh, 8px);
  }
  
  .auth-input {
    padding: clamp(6px, 1.8vh, 10px) clamp(10px, 2vw, 16px);
    font-size: clamp(11px, 1.8vh, 13px);
  }
  
  .error-message,
  .success-message {
    padding: 5px 10px;
    font-size: 10px;
  }
  
  .form-button {
    margin-top: 0;
  }
  
  .form-button :deep(.button) {
    font-size: clamp(11px, 2.2vh, 14px) !important;
    padding: clamp(6px, 1.8vh, 10px) clamp(14px, 3vw, 24px) !important;
  }
  
  .login-bottom-text {
    font-size: 10px;
    padding: 2px 4px;
  }
}

/* Экстремально низкая высота */
@media (max-height: 380px) and (orientation: landscape) {
  .auth-form {
    padding: clamp(5px, 1.5vh, 10px) clamp(8px, 2vw, 14px);
    gap: clamp(3px, 1vh, 6px);
    border-radius: clamp(8px, 2vh, 14px);
  }
  
  .welcome-title {
    font-size: clamp(0.8rem, 2.5vh, 1rem);
  }
  
  .form-fields {
    gap: clamp(3px, 1vh, 6px);
  }
  
  .auth-input {
    padding: clamp(5px, 1.5vh, 8px) clamp(8px, 1.8vw, 14px);
    font-size: clamp(10px, 1.6vh, 12px);
  }
  
  .form-button :deep(.button) {
    font-size: clamp(10px, 2vh, 12px) !important;
    padding: clamp(5px, 1.5vh, 8px) clamp(12px, 2.5vw, 20px) !important;
  }
  
  .login-bottom-text {
    font-size: 9px;
  }
}

/* Высокие экраны */
@media (min-height: 900px) and (min-width: 1024px) {
  .auth-form {
    padding: 50px;
    gap: 26px;
  }
  
  .welcome-title {
    font-size: 2.4rem;
  }
  
  .auth-input {
    padding: 18px 28px;
    font-size: 17px;
  }
}

/* Ультраширокие мониторы */
@media (min-width: 1920px) {
  .auth-form {
    max-width: 500px;
    padding: 55px;
  }
  
  .welcome-title {
    font-size: 2.5rem;
  }
}
</style>