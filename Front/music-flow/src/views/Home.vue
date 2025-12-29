<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import Logo from '@/assets/logo.vue';
import AccountIcon from '@/assets/Account.vue';
import Button from '@/components/Button.vue';
import { gsap } from "gsap/dist/gsap";
import { getCookie } from '@/utils/cookies.js';

const router = useRouter();

onMounted(async () => {
  // Если пользователь авторизован, редирект на Main
  const userId = getCookie('user_id');
  if (userId) {
    router.push('/main');
    return;
  }
  
  await nextTick();
  gsap.from('.hero-section', { opacity: 0, y: 30, duration: 1, ease: 'power2.out' });
  gsap.from('.features-grid', { opacity: 0, y: 50, duration: 1, delay: 0.3, ease: 'power2.out' });
  gsap.from('.content-container', { opacity: 0, y: 50, duration: 1, delay: 0.6, ease: 'power2.out' });
});


const currentTab = ref(0);

const features = [
  {
    icon: '🎵',
    title: 'Общая очередь',
    description: 'Добавляйте треки в общую очередь воспроизведения с друзьями'
  },
  {
    icon: '🔄',
    title: 'Синхронизация',
    description: 'Музыка играет одновременно на всех подключённых устройствах'
  },
  {
    icon: '🎛️',
    title: 'Кастомизация',
    description: 'Настраивайте порядок треков, приоритеты и правила воспроизведения'
  },
  {
    icon: '🎧',
    title: 'Яндекс.Музыка',
    description: 'Интеграция с вашей медиатекой Яндекс.Музыки'
  }
];

const tabs = [
  {
    title: 'О сервисе',
    content: `
      <p class="mb-4">Music Flow — это инновационный сервис для совместного прослушивания музыки. Он позволяет слушать музыку в компании друзей на разных устройствах, создавая общую очередь треков с возможностью глубокой кастомизации порядка воспроизведения.</p>
      <p class="mb-4">Сервис расширяет возможности стримингового сервиса Яндекс.Музыка и предоставляет пользователям уникальный опыт прослушивания музыки вместе — будь то вечеринки, поездки, игры или просто общение с друзьями.</p>
      <p><strong>Ключевая идея:</strong> Музыка объединяет людей, и Music Flow делает это проще, чем когда-либо!</p>`
  },
  {
    title: 'Как это работает',
    content: `
      <div class="steps-list">
        <div class="step"><span class="step-number">1</span> Создайте комнату или присоединитесь к существующей</div>
        <div class="step"><span class="step-number">2</span> Авторизуйтесь через Яндекс.Музыку для доступа к медиатеке</div>
        <div class="step"><span class="step-number">3</span> Добавляйте треки в общую очередь воспроизведения</div>
        <div class="step"><span class="step-number">4</span> Наслаждайтесь музыкой синхронно на всех устройствах!</div>
      </div>`
  },
  {
    title: 'Возможности',
    content: `
      <ul>
        <li>🎵 Создание приватных и публичных комнат для прослушивания</li>
        <li>📝 Управление очередью воспроизведения с гибкими настройками</li>
        <li>🔄 Синхронное воспроизведение на всех устройствах в реальном времени</li>
        <li>⚡ Мгновенный поиск и добавление треков из Яндекс.Музыки</li>
        <li>👥 Совместное управление плейлистом с друзьями</li>
        <li>📱 Адаптивный интерфейс для любых устройств</li>
      </ul>`
  }
];
</script>

<template>
  <div class="app-background home-page">
    <!-- Header -->
    <header class="header">
      <Logo class="logo home-logo" />
      <router-link to="/login" class="icon-wrapper">
        <AccountIcon />
      </router-link>
    </header>

    <!-- Hero Section -->
    <section class="hero-section">
      <h1 class="hero-title">Music Flow</h1>
      <p class="hero-subtitle">Слушайте музыку вместе с друзьями</p>
      <p class="hero-description">
        Создавайте комнаты, добавляйте любимые треки и наслаждайтесь 
        синхронным воспроизведением на всех устройствах
      </p>
      <router-link to="/login" class="hero-cta">
        <Button text="Начать" textSize="clamp(18px, 4vw, 28px)" />
      </router-link>
    </section>

    <!-- Features Grid -->
    <section class="features-grid">
      <div 
        v-for="(feature, index) in features" 
        :key="index" 
        class="feature-card"
      >
        <span class="feature-icon">{{ feature.icon }}</span>
        <h3 class="feature-title">{{ feature.title }}</h3>
        <p class="feature-description">{{ feature.description }}</p>
      </div>
    </section>

    <!-- Tabs Content -->
    <main class="content-container">
      <div class="tab-buttons">
        <button
          v-for="(tab, index) in tabs"
          :key="index"
          @click="currentTab = index"
          :class="['tab-button', { active: currentTab === index }]"
        >
          {{ tab.title }}
        </button>
      </div>

      <transition name="fade" mode="out-in">
        <div class="info-box" :key="currentTab">
          <div v-html="tabs[currentTab].content" class="tab-content" />
        </div>
      </transition>
    </main>

    <!-- Footer -->
    <footer class="home-footer">
      <p>© 2024 Music Flow. Все права защищены.</p>
    </footer>
  </div>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
}

/* Header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  position: relative;
  z-index: 10;
}

.home-logo {
  width: clamp(150px, 20vw, 300px);
  padding: 0.5rem;
}

/* Hero Section */
.hero-section {
  text-align: center;
  padding: 2rem 1.5rem 3rem;
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: clamp(2.5rem, 8vw, 4.5rem);
  font-weight: 800;
  background: linear-gradient(135deg, #00d9e7 0%, #D0BCFF 50%, #ff6b9d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
  text-shadow: 0 0 60px rgba(0, 217, 231, 0.3);
}

.hero-subtitle {
  font-size: clamp(1.2rem, 4vw, 1.8rem);
  color: #D0BCFF;
  margin-bottom: 1rem;
  font-weight: 600;
}

.hero-description {
  font-size: clamp(0.95rem, 2.5vw, 1.15rem);
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  max-width: 600px;
  margin: 0 auto 2rem;
}

.hero-cta {
  display: inline-block;
}

/* Features Grid */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.feature-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 217, 231, 0.2);
  border-radius: 20px;
  padding: 2rem 1.5rem;
  text-align: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.feature-card:hover {
  transform: translateY(-5px);
  border-color: rgba(0, 217, 231, 0.5);
  box-shadow: 0 10px 40px rgba(0, 217, 231, 0.15);
}

.feature-icon {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 1rem;
}

.feature-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.5rem;
}

.feature-description {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.5;
}

/* Content Container */
.content-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  flex: 1;
  width: 100%;
  box-sizing: border-box;
}

/* Tab Buttons */
.tab-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.tab-button {
  background: transparent;
  color: #D0BCFF;
  border: 2px solid #D0BCFF;
  padding: 0.6rem 1.2rem;
  border-radius: 9999px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: clamp(0.85rem, 2vw, 1rem);
  white-space: nowrap;
}

.tab-button:hover {
  background-color: rgba(123, 99, 148, 0.25);
}

.tab-button.active {
  background-color: #D0BCFF33;
  color: white;
}

/* Info Box */
.info-box {
  background-color: rgba(255, 255, 255, 0.08);
  border: 2px solid rgba(0, 217, 231, 0.4);
  padding: clamp(1.5rem, 4vw, 3rem);
  border-radius: 1rem;
  backdrop-filter: blur(10px);
  color: #ffffff;
  transition: all 0.3s ease;
}

.tab-content {
  font-size: clamp(0.95rem, 2vw, 1.15rem);
  line-height: 1.8;
}

.tab-content :deep(ul) {
  list-style: none;
  padding-left: 0;
}

.tab-content :deep(ul li) {
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tab-content :deep(ul li:last-child) {
  border-bottom: none;
}

.tab-content :deep(.steps-list) {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.tab-content :deep(.step) {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(0, 217, 231, 0.1);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.tab-content :deep(.step:hover) {
  background: rgba(0, 217, 231, 0.15);
}

.tab-content :deep(.step-number) {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  min-width: 32px;
  background: linear-gradient(135deg, #00d9e7, #D0BCFF);
  border-radius: 50%;
  font-weight: bold;
  color: #1a1025;
}

/* Footer */
.home-footer {
  text-align: center;
  padding: 2rem;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
  margin-top: auto;
}

/* Animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Responsive */
@media (max-width: 768px) {
  .header {
    padding: 0.75rem 1rem;
  }

  .hero-section {
    padding: 1.5rem 1rem 2rem;
  }

  .features-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    padding: 1.5rem 1rem;
  }

  .feature-card {
    padding: 1.5rem 1rem;
  }

  .feature-icon {
    font-size: 2rem;
  }

  .feature-title {
    font-size: 1rem;
  }

  .feature-description {
    font-size: 0.85rem;
  }

  .content-container {
    padding: 1.5rem 1rem;
  }
}

@media (max-width: 480px) {
  .features-grid {
    grid-template-columns: 1fr;
  }

  .tab-buttons {
    gap: 0.5rem;
  }

  .tab-button {
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
  }

  .info-box {
    padding: 1.25rem;
  }

  .tab-content :deep(.step) {
    padding: 0.75rem;
    gap: 0.75rem;
  }

  .tab-content :deep(.step-number) {
    width: 28px;
    height: 28px;
    min-width: 28px;
    font-size: 0.9rem;
  }
}
</style>