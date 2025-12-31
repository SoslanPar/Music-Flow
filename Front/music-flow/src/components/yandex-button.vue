<script setup>
import { onMounted, ref } from 'vue';

const isLoading = ref(true);
const error = ref(null);
const retryCount = ref(0);
const MAX_RETRIES = 3;

const loadYandexSDK = () => {
  return new Promise((resolve, reject) => {
    // Проверяем, может SDK уже загружен
    if (window.YaAuthSuggest) {
      return resolve();
    }

    // Проверяем существующий скрипт
    const existingScript = document.querySelector(
      'script[src^="https://yastatic.net/s3/passport-sdk"]'
    );

    if (existingScript) {
      existingScript.onload = () => resolve();
      existingScript.onerror = () => reject(new Error('Script load error'));
      return;
    }

    // Создаем новый скрипт
    const script = document.createElement('script');
    script.src = 'https://yastatic.net/s3/passport-sdk/autofill/v1/sdk-suggest-with-polyfills-latest.js';
    script.async = true;
    
    script.onload = () => {
      if (!window.YaAuthSuggest) {
        reject(new Error('SDK not available after load'));
        return;
      }
      resolve();
    };

    script.onerror = () => {
      reject(new Error('Failed to load script'));
    };

    document.head.appendChild(script);
  });
};

const initYandexAuth = async () => {
  try {
    error.value = null;
    isLoading.value = true;
    
    await loadYandexSDK();

    const result = await window.YaAuthSuggest.init(
      {
        client_id: import.meta.env.VITE_CLIENT_ID,
        response_type: 'code',
        redirect_uri: `${window.location.origin}/yandex-callback`,
      },
      window.location.origin,
      {
        view: 'button',
        parentId: 'yandex-auth-button',
        buttonView: 'additional',
        buttonTheme: 'dark',
        buttonSize: 'm',
        buttonBorderRadius: 22,
      }
    );

    if (result.status !== 'ok') {
      throw new Error('Init failed: ' + result.status);
    }

    const data = await result.handler();
    
    window.postMessage({
      type: 'yandex_auth_success',
      code: data.code
    }, window.location.origin);
    
  } catch (err) {
    error.value = `Ошибка: ${err.message}`;
    
    if (retryCount.value < MAX_RETRIES) {
      retryCount.value++;
      setTimeout(initYandexAuth, 2000);
      return;
    }
    
    renderFallbackButton();
  } finally {
    isLoading.value = false;
  }
};

const renderFallbackButton = () => {
  const container = document.getElementById('yandex-auth-button');
  if (!container) return;
  
  container.innerHTML = `
    <a href="https://oauth.yandex.ru/authorize?
      response_type=token&
      client_id=${import.meta.env.VITE_CLIENT_ID}&
      redirect_uri=${encodeURIComponent(window.location.origin + '/yandex-callback')}"
      class="yandex-fallback-button">
      Войти через Яндекс
    </a>
  `;
};

const retry = () => {
  retryCount.value = 0;
  initYandexAuth();
};

onMounted(() => {
  initYandexAuth();
});

// Обработчик ошибок браузера
window.addEventListener('error', (event) => {
  if (event.message.includes('cookie') || event.message.includes('third-party')) {
    error.value = 'Пожалуйста, разрешите сторонние куки в настройках браузера';
  }
});
</script>

<template>
  <div class="yandex-auth-wrapper">
    <!-- Основной контейнер для кнопки -->
    <div id="yandex-auth-button" class="yandex-button-container"></div>
    
    <!-- Состояние загрузки -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-content">
        <div class="loader"></div>
        <div class="loading-text">Загрузка авторизации...</div>
      </div>
    </div>
    
    <!-- Сообщения об ошибках -->
    <div v-if="error && !isLoading" class="error-overlay">
      <div class="error-content">
        <div class="error-text">{{ error }}</div>
        <button @click="retry" class="retry-button">
          Попробовать снова
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.yandex-auth-wrapper {
  margin: 20px auto;
  min-height: 48px;
  position: relative;
  width: 100%;
  max-width: 300px;
}

.yandex-button-container {
  display: flex;
  justify-content: center;
  min-height: 48px;
}

.loading-overlay,
.error-overlay {
  opacity: 0;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(255, 255, 255, 0.9);
  z-index: 10;
  border-radius: 8px;
}

.loading-content,
.error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.loader {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #FF0000;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 14px;
  color: #555;
}

.error-text {
  font-size: 14px;
  color: #d32f2f;
  text-align: center;
  margin-bottom: 10px;
}

.retry-button {
  padding: 8px 16px;
  background-color: #FF0000;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.retry-button:hover {
  background-color: #d50000;
}

.yandex-fallback-button {
  display: inline-block;
  padding: 10px 20px;
  background: #000;
  color: #fff;
  border-radius: 22px;
  text-decoration: none;
  font-size: 14px;
}

/* Адаптация для горизонтальной ориентации на мобильных */
@media (max-height: 600px) and (orientation: landscape) {
  .yandex-auth-wrapper {
    margin: clamp(8px, 2vh, 16px) auto;
    min-height: clamp(36px, 8vh, 44px);
    max-width: 260px;
  }
  
  .yandex-button-container {
    min-height: clamp(36px, 8vh, 44px);
  }
  
  .yandex-fallback-button {
    padding: 8px 16px;
    font-size: 13px;
  }
}

@media (max-height: 450px) and (orientation: landscape) {
  .yandex-auth-wrapper {
    margin: clamp(5px, 1.5vh, 10px) auto;
    min-height: clamp(32px, 7vh, 38px);
    max-width: 220px;
  }
  
  .yandex-button-container {
    min-height: clamp(32px, 7vh, 38px);
  }
  
  .yandex-fallback-button {
    padding: 6px 14px;
    font-size: 12px;
    border-radius: 18px;
  }
}

@media (max-height: 380px) and (orientation: landscape) {
  .yandex-auth-wrapper {
    margin: clamp(3px, 1vh, 8px) auto;
    min-height: clamp(28px, 6vh, 34px);
    max-width: 200px;
  }
  
  .yandex-button-container {
    min-height: clamp(28px, 6vh, 34px);
  }
  
  .yandex-fallback-button {
    padding: 5px 12px;
    font-size: 11px;
  }
}
</style>