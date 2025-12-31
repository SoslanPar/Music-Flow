<template>
  <header class="main-header">
    <div class="header-left">
      <!-- Кнопка для открытия комнат на десктопе -->
      <button v-if="connected" class="rooms-menu-btn" @click="$emit('toggle-rooms-dropdown')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
        </svg>
      </button>
      
      <!-- Мобильная кнопка sidebar -->
      <button v-if="connected" class="sidebar-toggle mobile-only" @click="$emit('toggle-sidebar')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
        </svg>
      </button>
      
      <Logo class="header-logo-full" />
      
      <!-- Слот для dropdown комнат -->
      <slot name="rooms-dropdown"></slot>
    </div>
    
    <div class="header-center" v-if="connected && roomName">
      <span class="room-title">{{ roomName }}</span>
    </div>
    
    <div class="header-right">
      <button class="icon-btn help-btn" title="Помощь">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/>
        </svg>
      </button>
      
      <!-- Меню аккаунта -->
      <div class="account-menu-wrapper">
        <button class="icon-btn account-btn" @click="$emit('toggle-account-menu')">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
          </svg>
        </button>
        
        <!-- Dropdown меню -->
        <div v-if="showAccountMenu" class="account-dropdown">
          <div class="dropdown-item user-info">
            <span class="user-name">{{ userName }}</span>
          </div>
          <button class="dropdown-item logout-btn" @click="$emit('logout')">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
            </svg>
            <span>Выйти</span>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import Logo from '@/assets/logo.vue';

defineProps({
  connected: Boolean,
  roomName: String,
  userName: String,
  showAccountMenu: Boolean,
});

defineEmits([
  'toggle-rooms-dropdown',
  'toggle-sidebar',
  'toggle-account-menu',
  'logout',
]);
</script>

<style scoped>
.main-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: rgba(15, 12, 24, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: sticky;
  top: 0;
  z-index: 50;
  min-height: 60px;
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.room-title {
  font-size: 1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.rooms-menu-btn,
.sidebar-toggle {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.rooms-menu-btn:hover,
.sidebar-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.header-logo-full {
  height: 32px;
  width: auto;
}

.icon-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.account-menu-wrapper {
  position: relative;
}

.account-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 180px;
  background: rgba(30, 25, 45, 0.98);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  z-index: 100;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  width: 100%;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
  text-align: left;
}

.dropdown-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.user-info {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.user-name {
  font-weight: 600;
}

.logout-btn {
  color: #ff6b6b;
}

.logout-btn:hover {
  background: rgba(255, 107, 107, 0.1);
}

/* Mobile only */
@media (min-width: 769px) {
  .mobile-only {
    display: none !important;
  }
}

@media (max-width: 768px) {
  .main-header {
    padding: 10px 16px;
  }
  
  .header-logo-full {
    height: 28px;
  }
}
</style>
