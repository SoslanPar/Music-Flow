<template>
  <div class="send-container">
    <input 
      type="text" 
      v-model="trackUrl" 
      placeholder="Track name" 
      class="send-input"
      @keyup.enter="handleSend"
    >
    <button class="send-btn" @click="handleSend" :disabled="!trackUrl.trim()">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
      </svg>
    </button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      trackUrl: ''
    };
  },
  methods: {
    handleSend() {
      if (this.trackUrl.trim()) {
        this.$emit('send', this.trackUrl.trim());
        this.trackUrl = '';
      }
    }
  }
};
</script>

<style scoped>
.send-container {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(23, 18, 34, 0.7);
  border-radius: 16px;
  border: 1px solid rgba(208, 188, 255, 0.1);
}

.send-input {
  flex: 1;
  background: transparent;
  border: none;
  color: white;
  font-size: 14px;
  outline: none;
  padding: 8px 0;
}

.send-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.send-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba(139, 92, 246, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn svg {
  margin-left: 2px;
}
</style>