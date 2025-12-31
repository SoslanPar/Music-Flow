/**
 * WebSocket Manager с автоматическим переподключением
 */
class SocketManager {
  constructor(roomId, userId, handlers = {}) {
    this.roomId = roomId;
    this.userId = userId;
    this.handlers = handlers;
    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.isIntentionallyClosed = false;
  }

  connect() {
    if (this.socket?.readyState === WebSocket.OPEN) {
      return this.socket;
    }

    this.socket = new WebSocket(`/ws/room/${this.roomId}/ws?user_id=${this.userId}`);
    
    this.socket.onopen = () => {
      this.reconnectAttempts = 0;
      this.socket.send(JSON.stringify({ type: 'get_participants' }));
      if (this.handlers.onConnect) {
        this.handlers.onConnect();
      }
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (this.handlers[data.type]) {
          this.handlers[data.type](data);
        } else if (this.handlers['*']) {
          this.handlers['*'](data);
        }
      } catch (e) {
        // Игнорируем ошибки парсинга
      }
    };

    this.socket.onclose = (event) => {
      if (this.isIntentionallyClosed) {
        return;
      }
      
      // Переподключение с экспоненциальной задержкой
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
        
        if (this.handlers.onReconnecting) {
          this.handlers.onReconnecting(this.reconnectAttempts, this.maxReconnectAttempts);
        }
        
        setTimeout(() => this.connect(), delay);
      } else {
        if (this.handlers.onMaxReconnectAttemptsReached) {
          this.handlers.onMaxReconnectAttemptsReached();
        }
      }
    };

    this.socket.onerror = () => {
      // Ошибка будет обработана в onclose
    };

    return this.socket;
  }

  send(message) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
      return true;
    }
    return false;
  }

  close(code = 1000, reason = 'Normal closure') {
    this.isIntentionallyClosed = true;
    if (this.socket) {
      this.socket.close(code, reason);
    }
  }

  get readyState() {
    return this.socket?.readyState ?? WebSocket.CLOSED;
  }
}

/**
 * Создать WebSocket соединение с автореконнектом
 */
export function initSocket(roomId, userId, handlers = {}) {
  const manager = new SocketManager(roomId, userId, handlers);
  manager.connect();
  return manager;
}

/**
 * Отправить сообщение через WebSocket
 */
export function sendSocketMessage(socketManager, message) {
  if (socketManager?.send) {
    return socketManager.send(message);
  }
  // Обратная совместимость с обычным WebSocket
  if (socketManager?.readyState === WebSocket.OPEN) {
    socketManager.send(JSON.stringify(message));
    return true;
  }
  return false;
}
