export function initSocket(roomId, userId, handlers = {}) {
  const socket = new WebSocket(`/ws/room/${roomId}/ws?user_id=${userId}`);
  socket.onopen = () => {
    socket.send(JSON.stringify({ type: 'get_participants' }));
  };
  socket.onmessage = event => {
    const data = JSON.parse(event.data);
    if (handlers[data.type]) {
      handlers[data.type](data);
    } else if (handlers['*']) {
      handlers['*'](data);
    }
  };
  return socket;
}

export function sendSocketMessage(socket, message) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(message));
  }
}
