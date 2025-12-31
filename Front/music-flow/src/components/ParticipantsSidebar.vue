<template>
  <aside class="sidebar" :class="{ 'sidebar-open': isOpen }">
    <div class="sidebar-section">
      <div class="sidebar-header">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
        </svg>
        <span>Участники</span>
      </div>
      <ul class="sidebar-list participants-list">
        <li v-for="participant in participants" :key="participant.id" class="sidebar-item">
          <div class="item-avatar" :class="{ 'you': participant.id === currentUserId }">
            {{ participant.name.charAt(0).toUpperCase() }}
          </div>
          <span class="item-name">{{ participant.name }}</span>
          <span v-if="participant.id === currentUserId" class="you-badge">Вы</span>
        </li>
        <li v-if="participants.length === 0" class="empty-item">
          Нет участников
        </li>
      </ul>
    </div>
    
    <button class="leave-room-btn desktop-only" @click="$emit('leave-room')">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
        <path d="M10.09 15.59L11.5 17l5-5-5-5-1.41 1.41L12.67 11H3v2h9.67l-2.58 2.59zM19 3H5c-1.11 0-2 .9-2 2v4h2V5h14v14H5v-4H3v4c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/>
      </svg>
      <span>Выйти из комнаты</span>
    </button>
    
    <!-- Кнопка выхода для мобильных -->
    <div class="sidebar-section sidebar-leave-section mobile-only">
      <button class="sidebar-leave-btn" @click="$emit('leave-room')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
          <path d="M10.09 15.59L11.5 17l5-5-5-5-1.41 1.41L12.67 11H3v2h9.67l-2.58 2.59zM19 3H5c-1.11 0-2 .9-2 2v4h2V5h14v14H5v-4H3v4c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/>
        </svg>
        <span>Выйти из комнаты</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  participants: {
    type: Array,
    default: () => [],
  },
  currentUserId: {
    type: String,
    default: '',
  },
  isOpen: {
    type: Boolean,
    default: false,
  },
});

defineEmits(['leave-room']);
</script>

<style scoped>
.sidebar {
  width: 240px;
  background: rgba(20, 16, 30, 0.95);
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  padding: 16px 0;
  flex-shrink: 0;
  height: 100%;
  overflow-y: auto;
}

.sidebar-section {
  padding: 0 16px;
  margin-bottom: 16px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.sidebar-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 8px;
  transition: background 0.2s;
}

.sidebar-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.item-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
}

.item-avatar.you {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

.item-name {
  flex: 1;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.you-badge {
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.empty-item {
  padding: 12px 10px;
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.85rem;
}

.leave-room-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: auto 16px 16px;
  padding: 12px 16px;
  border-radius: 10px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: #ef4444;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.leave-room-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.3);
}

.sidebar-leave-section {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.sidebar-leave-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 12px 16px;
  background: transparent;
  border: none;
  color: #ef4444;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s;
}

.sidebar-leave-btn:hover {
  background: rgba(239, 68, 68, 0.1);
}

/* Mobile styles */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 60px;
    bottom: 0;
    z-index: 40;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .sidebar.sidebar-open {
    transform: translateX(0);
  }
  
  .desktop-only {
    display: none !important;
  }
}

@media (min-width: 769px) {
  .mobile-only {
    display: none !important;
  }
}
</style>
