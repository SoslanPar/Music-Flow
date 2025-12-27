<template>
  <div class="rooms-container">
    <div class="rooms-card">
      <h2 class="rooms-title">Комнаты</h2>
      
      <!-- Табы -->
      <div class="tabs">
        <button 
          :class="['tab-btn', { active: activeTab === 'join' }]" 
          @click="activeTab = 'join'"
        >
          Войти в комнату
        </button>
        <button 
          :class="['tab-btn', { active: activeTab === 'create' }]" 
          @click="activeTab = 'create'"
        >
          Создать комнату
        </button>
      </div>

      <!-- Контент табов -->
      <div class="tab-content">
        <!-- Вход в комнату -->
        <div v-if="activeTab === 'join'" class="tab-panel">
          <input
            v-model="roomIdInput"
            type="text"
            placeholder="Введите ID комнаты"
            class="rooms-input"
            @keyup.enter="joinRoom"
          />
          <Button text="Подключиться" @click="joinRoom" :disabled="!roomIdInput.trim()" />
        </div>

        <!-- Создание комнаты -->
        <div v-if="activeTab === 'create'" class="tab-panel">
          <input
            v-model="newRoomName"
            type="text"
            placeholder="Название комнаты"
            class="rooms-input"
            @keyup.enter="createRoom"
          />
          <Button text="Создать" @click="createRoom" :disabled="!newRoomName.trim() || isCreating" />
        </div>
      </div>

      <!-- Сообщение об ошибке -->
      <transition name="fade">
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
      </transition>

      <!-- Сообщение об успехе -->
      <transition name="fade">
        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import Button from '@/components/Button.vue';
import { roomsApi } from '@/utils/api.js';
import { getCookie } from '@/utils/cookies.js';

export default {
  components: { Button },
  data() {
    return { 
      roomIdInput: '',
      newRoomName: '',
      activeTab: 'join',
      isCreating: false,
      errorMessage: '',
      successMessage: '',
    };
  },
  methods: {
    joinRoom() {
      this.clearMessages();
      const value = this.roomIdInput.trim();
      if (value) {
        this.$emit('join-room', value);
      }
    },
    async createRoom() {
      this.clearMessages();
      const name = this.newRoomName.trim();
      
      if (!name) {
        this.errorMessage = 'Введите название комнаты';
        return;
      }

      const userId = getCookie('user_id');
      if (!userId) {
        this.errorMessage = 'Необходимо авторизоваться';
        return;
      }

      this.isCreating = true;
      
      try {
        const result = await roomsApi.createRoom(name);
        
        if (result.Status === 'Error') {
          this.errorMessage = result.Message || 'Ошибка при создании комнаты';
          return;
        }

        // Найдём созданную комнату (последнюю в списке)
        if (Array.isArray(result) && result.length > 0) {
          const newRoom = result[result.length - 1];
          this.successMessage = `Комната "${name}" создана!`;
          
          // Автоматически входим в созданную комнату через 1 секунду
          setTimeout(() => {
            this.$emit('join-room', newRoom.id);
          }, 1000);
        }
      } catch (error) {
        this.errorMessage = error.message || 'Не удалось создать комнату';
      } finally {
        this.isCreating = false;
      }
    },
    clearMessages() {
      this.errorMessage = '';
      this.successMessage = '';
    }
  }
};
</script>

<style scoped>
.rooms-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  width: 100%;
  height: 100%;
  padding: 20px;
  box-sizing: border-box;
}

.rooms-card {
  background: rgba(23, 18, 34, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 30px;
  padding: 40px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 0 40px rgba(160, 85, 245, 0.1);
}

.rooms-title {
  text-align: center;
  font-size: 2rem;
  font-weight: bold;
  color: white;
  margin-bottom: 30px;
  text-shadow: 0 0 10px rgba(0, 217, 231, 0.5);
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 25px;
}

.tab-btn {
  flex: 1;
  padding: 12px 20px;
  border: 2px solid rgba(208, 188, 255, 0.3);
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.tab-btn:hover {
  background: rgba(208, 188, 255, 0.1);
  color: white;
}

.tab-btn.active {
  background: rgba(208, 188, 255, 0.2);
  border-color: rgba(208, 188, 255, 0.5);
  color: white;
}

.tab-content {
  min-height: 150px;
}

.tab-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.rooms-input {
  width: 100%;
  padding: 14px 24px;
  border-radius: 50px;
  border: 2px solid rgba(160, 85, 245, 0.2);
  background: rgba(160, 85, 245, 0.1);
  color: white;
  outline: none;
  font-size: 16px;
  transition: all 0.3s ease;
}

.rooms-input:focus {
  border-color: rgba(160, 85, 245, 0.5);
  background: rgba(160, 85, 245, 0.15);
}

.rooms-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.error-message {
  margin-top: 15px;
  padding: 12px 20px;
  background: rgba(255, 82, 82, 0.2);
  border: 1px solid rgba(255, 82, 82, 0.3);
  border-radius: 12px;
  color: #ff8a8a;
  text-align: center;
  font-size: 14px;
}

.success-message {
  margin-top: 15px;
  padding: 12px 20px;
  background: rgba(46, 164, 140, 0.2);
  border: 1px solid rgba(46, 164, 140, 0.3);
  border-radius: 12px;
  color: #5ff5d5;
  text-align: center;
  font-size: 14px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 600px) {
  .rooms-card {
    padding: 25px;
    border-radius: 20px;
  }
  
  .rooms-title {
    font-size: 1.5rem;
  }
  
  .tabs {
    flex-direction: column;
  }
}
</style>
