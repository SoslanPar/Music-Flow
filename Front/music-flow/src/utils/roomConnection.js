import { initSocket } from './playerSocket.js';
import { getCookie } from './cookies.js';

export function connectToRoom(roomId, onMessage) {
  const userId = getCookie('user_id');
  if (!userId) {
    throw new Error('User not authorized');
  }
  const socket = initSocket(roomId, userId, { '*': onMessage });
  return { socket, userId };
}
