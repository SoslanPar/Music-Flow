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
  gsap.from('.content-container', { opacity: 0, y: 50, duration: 2, delay: 0.25, ease: 'power2.out' });
});


const currentTab = ref(0);

const tabs = [
  {
    title: 'О сервисе',
    content: `
      <p>Music Flow — это сервис, который позволяет слушать музыку в компании друзей на разных устройствах, создавая общую очередь треков с возможностью глубокой кастомизации порядка воспроизведения.</p>
      <p>Сервис ориентирован на расширение возможностей стримингового сервиса Яндекс.Музыка и предоставляет пользователям новый опыт прослушивания музыки вместе — будь то вечеринки, поездки, игры или просто общение в социальных сетях.</p>`
  },
  {
    title: 'О проекте',
    content: `
      <ul>
        <li>Создавайте общую очередь воспроизведения</li>
        <li>Гибкая кастомизация и тайминги</li>
        <li>Синхронизация между устройствами</li>
        <li>Интуитивно понятный интерфейс</li>
      </ul>`
  },
  {
    title: 'Функционал',
    content: `
      <ul>
        <li>Общий доступ к трекам</li>
        <li>Изменение порядка и приоритета песен</li>
        <li>Синхронное воспроизведение на всех устройствах</li>
      </ul>`
  }
];
</script>







<template>
  <div class="app-background">
    <!-- Header -->
    <header class="header">
      <!-- Логотип -->
      <Logo class="logo" />

      <!-- Иконка входа -->
      <router-link to="/login" class="icon-wrapper">
        <AccountIcon />
      </router-link>
    </header>

    <!-- Используем компонент Button -->
     
    <router-link to="/login">
      <Button class = button-home text="Приступить" textSize="35px"></Button>
    </router-link>

    <!-- Контент -->
    <main class="content-container">
      <h1 class="text-4xl font-bold mb-6 text-white text-center">Music Flow</h1>

      <!-- Переключатели -->
      <div class="tab-buttons flex justify-center gap-4">
        <button
          v-for="(tab, index) in tabs"
          :key="index"
          @click="currentTab = index"
          :class="['tab-button', { active: currentTab === index }]">
          {{ tab.title }}
        </button>
      </div>

      <!-- Текстовый блок -->
      <transition name="fade" mode="out-in">
        <div class="info-box" :key="currentTab">
          <p v-html="tabs[currentTab].content" class="tab-content" />
        </div>
      </transition>
    </main>
  </div>
</template>