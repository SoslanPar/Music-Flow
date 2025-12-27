





<template>
  <div class="participants-container">
    <h3 class="participants-title">Участники ({{ participants.length }})</h3>
    <ul class="participants-list">
      <li 
        v-for="participant in participants" 
        :key="participant.id"
        :class="['participant-item', { 'you': participant.id === userId }]"
      >
        <div class="participant-avatar">
          {{ participant.name.charAt(0).toUpperCase() }}
        </div>
        <span class="participant-name">
          {{ participant.name }}
          <span v-if="participant.id === userId" class="you-badge">(вы)</span>
        </span>
        <span class="status-badge status-online">online</span>
      </li>
    </ul>
    <div v-if="participants.length === 0" class="empty-state">
      Пока никого нет
    </div>
  </div>
</template>

<script>
export default {
  name: 'ParticipantsList',
  props: {
    participants: {
      type: Array,
      required: true,
      default: () => []
    },
    userId: {
      type: String,
      default: ''
    }
  }
}
</script>

<style scoped>
.participants-container {
  width: 100%;
  height: 100%;
  background: rgba(23, 18, 34, 0.5);
  border-radius: 2rem;
  padding: 1.5rem;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.participants-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
  margin-bottom: 1rem;
  text-align: center;
  text-shadow: 0 0 10px rgba(0, 217, 231, 0.5);
  flex-shrink: 0;
}

.participants-list {
  list-style: none;
  padding: 10px;
  margin: 0;
  flex-grow: 1;
  overflow-y: auto;
}

.participant-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  margin-bottom: 10px;
  border-radius: 50px;
  transition: all 0.3s ease;
  background: rgba(208, 188, 255, 0.08);
}

.participant-item.you {
  background: rgba(208, 188, 255, 0.2);
  box-shadow: 0 0 10px rgba(208, 188, 255, 0.2);
}

.participant-avatar {
  width: 40px;
  height: 40px;
  min-width: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1rem;
  margin-right: 12px;
  background: linear-gradient(135deg, #D0BCFF 0%, #2EA48C 100%);
  color: #1F1431;
  text-shadow: 0 1px 1px rgba(255, 255, 255, 0.3);
}

.participant-name {
  flex-grow: 1;
  color: white;
  font-weight: 500;
  font-size: 1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.you-badge {
  color: rgba(208, 188, 255, 0.7);
  font-size: 0.8rem;
  margin-left: 5px;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 50px;
  font-size: 11px;
  font-weight: bold;
  text-transform: uppercase;
  flex-shrink: 0;
}

.status-online {
  background: rgba(46, 164, 79, 0.2);
  color: #2EA44F;
}

.empty-state {
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  padding: 20px;
  font-size: 14px;
}

/* Scrollbar */
.participants-list::-webkit-scrollbar {
  width: 6px;
}

.participants-list::-webkit-scrollbar-track {
  background: transparent;
}

.participants-list::-webkit-scrollbar-thumb {
  background-color: rgba(208, 188, 255, 0.3);
  border-radius: 3px;
}

.participants-list::-webkit-scrollbar-thumb:hover {
  background-color: rgba(208, 188, 255, 0.5);
}

@media (max-width: 768px) {
  .participants-container {
    padding: 1rem;
    border-radius: 1.5rem;
  }
  
  .participants-title {
    font-size: 1.2rem;
  }
  
  .participant-item {
    padding: 10px 12px;
  }
  
  .participant-avatar {
    width: 32px;
    height: 32px;
    min-width: 32px;
    font-size: 0.9rem;
  }
  
  .participant-name {
    font-size: 0.9rem;
  }
  
  .status-badge {
    font-size: 10px;
    padding: 3px 8px;
  }
}
</style>