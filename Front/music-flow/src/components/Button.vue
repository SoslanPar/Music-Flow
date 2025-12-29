<template>
    <button class="button font-nunito font-semibold" :style="{ fontSize: textSize }">
      <span class="button-text">
        <!-- Белый слой -->
        <span class="text-white-layer">{{ text }}</span>
        <!-- Градиентный слой -->
        <span class="text-gradient-layer">{{ text }}</span>
      </span>
    </button>
</template>
  
  
  <script setup>
  
  const props = defineProps({
    text: {
      type: String,
      default: 'Button text'
    },
    textSize: {
      type: String,
      default: '20px'
    }
  })
  </script>
  
  <style scoped>
/* Стили для кнопки */
.button {
  @apply inline-flex items-center justify-center
         font-bold text-white
         bg-[rgba(50,208,177,0.75)]
         rounded-full shadow-[0_0_40px_5px_rgba(255,255,255,0.2)];
  padding: 0.6em 1.5em;
  max-width: 100%;
  box-sizing: border-box;
  transition:
    background-color 0.5s cubic-bezier(0.4,0,0.2,1),
    box-shadow 0.5s cubic-bezier(0.4,0,0.2,1);
}

.button:hover {
  background-color: #296456;
  box-shadow: 0 0 40px 5px rgba(255,255,255,0.2);
}

/* Обёртка для текста, чтобы наложить слои */
.button-text {
  position: relative;
  display: inline-block;
  white-space: nowrap;
}

/* Общие свойства для обоих слоёв */
.button-text span {
  display: block;
  transition: opacity 0.5s cubic-bezier(0.4,0,0.2,1);
}

/* Белый слой */
.text-white-layer {
  opacity: 1;
  color: white;
}

/* Градиентный слой (скрыт по умолчанию) */
.text-gradient-layer {
  position: absolute;
  top: 0; left: 0;
  opacity: 0;
  background-image: linear-gradient(90deg, #1fdeb1, #e45cfc);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* При ховере — кроссфейд */
.button:hover .text-white-layer {
  opacity: 0;
}
.button:hover .text-gradient-layer {
  opacity: 1;
}

/* Адаптивность кнопки */
@media (max-width: 480px) {
  .button {
    padding: 0.5em 1.2em;
  }
}

@media (max-height: 600px) and (orientation: landscape) {
  .button {
    padding: 0.4em 1em;
  }
}

@media (max-height: 450px) and (orientation: landscape) {
  .button {
    padding: 0.35em 0.9em;
  }
}

@media (max-height: 380px) and (orientation: landscape) {
  .button {
    padding: 0.3em 0.8em;
  }
}
</style>
  