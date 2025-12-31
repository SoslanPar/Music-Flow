<template>
  <div class="rooms-dropdown">
    <div class="rooms-dropdown-header">
      <span>Ваши комнаты</span>
      <button class="add-room-small-btn" @click.stop="showCreateForm = true">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
      </button>
    </div>
    
    <!-- Inline форма создания комнаты -->
    <div v-if="showCreateForm" class="dropdown-create-form">
      <input 
        v-model="newRoomName" 
        placeholder="Название комнаты"
        class="dropdown-create-input"
        @keyup.enter="createRoom"
        @click.stop
        ref="roomInput"
      />
      <div class="dropdown-create-buttons">
        <button class="dropdown-btn-cancel" @click.stop="cancelCreate">Отмена</button>
        <button class="dropdown-btn-create" @click.stop="createRoom" :disabled="!newRoomName.trim()">Создать</button>
      </div>
    </div>
    
    <ul v-else class="rooms-dropdown-list">
      <li 
        v-for="room in rooms" 
        :key="room.id" 
        class="rooms-dropdown-item"
        :class="{ 'current': room.id === currentRoomId }"
        @click="$emit('select-room', room)"
      >
        <div class="room-avatar-small">{{ room.name.charAt(0).toUpperCase() }}</div>
        <span>{{ room.name }}</span>
        <span v-if="room.id === currentRoomId" class="current-badge">Сейчас</span>
      </li>
      <li v-if="rooms.length === 0" class="empty-dropdown-item">Нет комнат</li>
    </ul>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue';

const props = defineProps({
  rooms: {
    type: Array,
    default: () => [],
  },
  currentRoomId: {
    type: [String, Number],
    default: null,
  },
});

const emit = defineEmits(['select-room', 'create-room']);

const showCreateForm = ref(false);
const newRoomName = ref('');
const roomInput = ref(null);

watch(showCreateForm, (val) => {
  if (val) {
    nextTick(() => {
      roomInput.value?.focus();
    });
  }
});

function createRoom() {
  const name = newRoomName.value.trim();
  if (name) {
    emit('create-room', name);
    cancelCreate();
  }
}

function cancelCreate() {
  showCreateForm.value = false;
  newRoomName.value = '';
}
</script>

<style scoped>
.rooms-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  min-width: 220px;
  background: rgba(30, 25, 45, 0.98);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  z-index: 100;
}

.rooms-dropdown-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.add-room-small-btn {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: rgba(139, 92, 246, 0.2);
  border: none;
  color: #a78bfa;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.add-room-small-btn:hover {
  background: rgba(139, 92, 246, 0.3);
  color: white;
}

.dropdown-create-form {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.dropdown-create-input {
  width: 100%;
  padding: 10px 12px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 0.9rem;
  outline: none;
  margin-bottom: 10px;
  transition: border-color 0.2s;
}

.dropdown-create-input:focus {
  border-color: rgba(139, 92, 246, 0.5);
}

.dropdown-create-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.dropdown-create-buttons {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.dropdown-btn-cancel,
.dropdown-btn-create {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.dropdown-btn-cancel {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.6);
}

.dropdown-btn-cancel:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.dropdown-btn-create {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
}

.dropdown-btn-create:hover:not(:disabled) {
  box-shadow: 0 0 15px rgba(139, 92, 246, 0.4);
}

.dropdown-btn-create:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.rooms-dropdown-list {
  list-style: none;
  margin: 0;
  padding: 8px 0;
  max-height: 300px;
  overflow-y: auto;
}

.rooms-dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.rooms-dropdown-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.rooms-dropdown-item.current {
  background: rgba(139, 92, 246, 0.1);
}

.room-avatar-small {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
}

.rooms-dropdown-item span:not(.current-badge):not(.room-avatar-small) {
  flex: 1;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.current-badge {
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(139, 92, 246, 0.3);
  color: #a78bfa;
}

.empty-dropdown-item {
  padding: 16px;
  text-align: center;
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.85rem;
}
</style>
