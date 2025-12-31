import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './main.css'
import { gsap } from "gsap/dist/gsap";
import { Flip } from "gsap/dist/Flip";

gsap.registerPlugin(Flip);

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.mount('#app');