<script setup>
import { ref } from 'vue';
import {onMounted, nextTick } from 'vue';
import Logo from '@/assets/logo.vue';
import AccountIcon from '@/assets/Account.vue';
import Button from '@/components/Button.vue';
import { gsap } from "gsap/dist/gsap";

onMounted(async () => {
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
// let dom = window.location.hostname;
// console.log(dom);
// let matches = fetch(`https://uniform-connections-scroll-cloud.trycloudflare.com/auth/sign-in?nickname=ch1l&hashed_password=5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5&domen=${dom}`, { method: 'GET'});
// console.log(matches);

// let matches = await fetch("/https://uniform-connections-scroll-cloud.trycloudflare.com/auth/sign-in?nickname=ch1l&hashed_password=5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5", {method:GET});

// async function getCookie(name) {
//                 let matches = await fetch("/https://uniform-connections-scroll-cloud.trycloudflare.com/get_cookie", {method:GET});
//                 return await matches.json();
//             }
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