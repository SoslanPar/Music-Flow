<script setup>
import { onMounted } from 'vue';

const loadYandexSdk = () => {
  return new Promise((resolve, reject) => {
    if (window.YaSendSuggestToken) {
      resolve();
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://yastatic.net/s3/passport-sdk/autofill/v1/sdk-suggest-token-with-polyfills-latest.js';
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Не удалось загрузить Yandex SDK'));
    document.head.appendChild(script);
  });
};

onMounted(async () => {
  const params = new URLSearchParams(window.location.search);
  const token = params.get('code');

  if (!token) {
    console.error('Код авторизации не найден в URL');
    // Отправляем сообщение об ошибке родителю
    if (window.opener) {
      window.opener.postMessage({
        type: 'yandex_auth_error',
        error: 'Code not found'
      }, window.location.origin);
      window.close();
    }
    return;
  }

  localStorage.setItem('yandex_token', token);

  try {
    await loadYandexSdk();

    window.YaSendSuggestToken(window.location.origin, {
      token: token
    });
  } catch (e) {
    console.error('Ошибка при работе с Yandex SDK:', e);
  }

  // Закрываем popup
  if (window.opener) {
    setTimeout(() => {
      window.close();
    }, 500);
  }
});
</script>

<template>
  <div class="callback-container">
    <div class="loader"></div>
    <p>Авторизация через Яндекс... Подождите</p>
  </div>
</template>

<style scoped>
.callback-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  gap: 20px;
  background: linear-gradient(135deg, #1F1431 0%, #112433 50%, #361A3C 100%);
}

p {
  font-family: 'Nunito', sans-serif;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
}

.loader {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(208, 188, 255, 0.3);
  border-top-color: #D0BCFF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
