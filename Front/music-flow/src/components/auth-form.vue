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
const isLoading = ref(false)

watch(() => props.isLogin, (newVal) => {
  errorMessage.value = ''
  if (!newVal) {
    showYandexBtn.value = false
  } else {
    setTimeout(() => {
      showYandexBtn.value = true
    }, 150)
  }
})

// Простой хэш пароля (в продакшене использовать bcrypt на сервере)
async function hashPassword(password) {
  const encoder = new TextEncoder()
  const data = encoder.encode(password)
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
}

async function handleSubmit() {
  errorMessage.value = ''
  
  if (!email.value || !password.value) {
    errorMessage.value = 'Заполните все поля'
    return
  }
  
  if (!props.isLogin && !username.value) {
    errorMessage.value = 'Введите имя пользователя'
    return
  }
  
  isLoading.value = true
  
  try {
    const hashedPassword = await hashPassword(password.value)
    
    if (props.isLogin) {
      // Вход
      const result = await authApi.signIn(email.value, hashedPassword)
      
      if (result.status === 'Successfully') {
        document.cookie = `user_id=${result.user_id}; path=/; SameSite=Lax`
        router.push('/main')
      } else {
        errorMessage.value = result.message || 'Неверный логин или пароль'
      }
    } else {
      // Регистрация - пока показываем сообщение
      errorMessage.value = 'Используйте авторизацию через Яндекс ID'
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
  gap: 20px;
  padding: 40px;
  background: rgba(23, 18, 34, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 30px;
  max-width: 450px;
  width: 100%;
}

.welcome-title {
  font-size: 2rem;
  font-weight: bold;
  color: white;
  text-align: center;
  margin-bottom: 10px;
  text-shadow: 0 0 10px rgba(0, 217, 231, 0.5);
}

.form-fields {
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 100%;
}

.auth-input {
  width: 100%;
  padding: 14px 24px;
  border-radius: 50px;
  border: 2px solid rgba(160, 85, 245, 0.2);
  background: rgba(160, 85, 245, 0.1);
  color: white;
  outline: none;
  font-size: 16px;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.auth-input:focus {
  border-color: rgba(160, 85, 245, 0.5);
  background: rgba(160, 85, 245, 0.15);
}

.auth-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.error-message {
  padding: 12px 20px;
  background: rgba(255, 82, 82, 0.2);
  border: 1px solid rgba(255, 82, 82, 0.3);
  border-radius: 12px;
  color: #ff8a8a;
  text-align: center;
  font-size: 14px;
  width: 100%;
  box-sizing: border-box;
}

.form-button {
  width: 100%;
  display: flex;
  justify-content: center;
}

.login-bottom-text {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  cursor: pointer;
  transition: color 0.3s ease;
}

.login-bottom-text:hover {
  color: white;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 600px) {
  .auth-form {
    padding: 24px 20px;
    border-radius: 24px;
    gap: 16px;
  }
  
  .welcome-title {
    font-size: 1.4rem;
    margin-bottom: 5px;
  }
  
  .form-fields {
    gap: 12px;
  }
  
  .auth-input {
    padding: 12px 20px;
    font-size: 15px;
  }
  
  .error-message {
    padding: 10px 16px;
    font-size: 13px;
  }
  
  .login-bottom-text {
    font-size: 13px;
  }
}

@media (max-width: 380px) {
  .auth-form {
    padding: 20px 16px;
    border-radius: 20px;
  }
  
  .welcome-title {
    font-size: 1.2rem;
  }
  
  .auth-input {
    padding: 10px 16px;
    font-size: 14px;
  }
}
</style>