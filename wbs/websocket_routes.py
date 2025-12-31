import asyncio
import uuid
import time
from fastapi import WebSocket, WebSocketDisconnect
from .websocket_manager import ConnectionManager

class WebSocketRoutes:
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
        self.message_queues = {}
        self.time_responses = {}
        # Время последнего переключения трека по комнатам
        self.last_track_change = {}

    async def handle_websocket(self, websocket: WebSocket, room_id: str, user_id: str):
        try:
            room_state = await self.manager.get_room_state(room_id)
        except Exception:
            await websocket.close(code=1008, reason="Room not found")
            return

        await self.manager.connect(websocket, room_id, user_id)

        # Создаем очередь сообщений
        message_queue = asyncio.Queue()
        self.message_queues[websocket] = message_queue

        reader_task = asyncio.create_task(self._message_reader(websocket, message_queue, room_id, user_id))
        try:
            # Используем сохранённое время из БД (без ожидания ответов от других клиентов)
            # Это ускоряет подключение с 1+ секунды до ~50мс
            current_position = room_state.get("time_moment", 0)
            
            # Асинхронно запрашиваем актуальное время у других участников (не блокируем)
            asyncio.create_task(self._sync_time_async(room_id, user_id))

            await self._send_initial_state(websocket, room_state, user_id)

            # Обрабатываем входящие сообщения
            while True:
                data = await message_queue.get()
                await self._handle_message(data, websocket, room_id, user_id)

        except WebSocketDisconnect:
            print(f"WebSocket disconnected for user {user_id}")
        except asyncio.CancelledError:
            # Корректно обрабатываем отмену задачи
            print('asyncio disconnect')
            pass
        finally:
            reader_task.cancel()
            await self.manager.disconnect(room_id, user_id)
            self.message_queues.pop(websocket, None)

    async def _message_reader(self, websocket: WebSocket, queue: asyncio.Queue, room_id: str, user_id: str):
        try:
            while True:
                data = await websocket.receive_json()
                await queue.put(data)
        except WebSocketDisconnect:
            print(f"WebSocket disconnected for user {user_id}")
        except asyncio.CancelledError:
            # Корректно обрабатываем отмену задачи
            print('asyncio disconnect')
            pass
        finally:
            await self.manager.disconnect(room_id, user_id)
            self.message_queues.pop(websocket, None)
        # except Exception as e:
        #     print('ERROR 66:', str(e))

    async def _get_consensus_time(self, room_id: str, exclude_user: str) -> float:
        """Быстрое получение времени - используем сохранённое в БД"""
        room_state = await self.manager.get_room_state(room_id)
        return room_state.get("time_moment", 0.0)
    
    async def _sync_time_async(self, room_id: str, exclude_user: str):
        """Асинхронная синхронизация времени (не блокирует подключение)"""
        try:
            # Запрашиваем время у участников
            await self.manager.get_current_playback_time(room_id, exclude_user)
            
            # Ждём короткое время для ответов
            await asyncio.sleep(0.3)
            
            # Обновляем время если получили ответы
            if room_id in self.time_responses and self.time_responses[room_id]:
                responses = list(self.time_responses[room_id].values())
                if responses:
                    avg_time = sum(responses) / len(responses)
                    await self.manager.update_room_state(room_id, {"time_moment": avg_time})
                    self.time_responses[room_id].clear()
        except Exception as e:
            print(f"Time sync error: {e}")
    # async def _get_consensus_time(self, room_id: str, exclude_user: str) -> float:
    #     connections = [
    #         conn for uid, conn in self.manager.active_connections.get(room_id, {}).items()
    #         if uid != exclude_user
    #     ]
    #     print(connections)
    #     if not connections:
    #         return 0.0

    #     tasks = [asyncio.create_task(self._request_current_time(conn)) for conn in connections]


    #     try:
    #         done, _ = await asyncio.wait(tasks, timeout=7.0, return_when=asyncio.FIRST_COMPLETED)
    #         for task in done:
    #             result = await task
    #             print(result)
    #             if result is not None:
    #                 return result
    #     except Exception as e:
    #         print('ERROR FROM _get_consensus_time:', e)
    #         pass

    #     return 0.0

    # async def _request_current_time(self, connection: WebSocket):
    #     try:
    #         await connection.send_json({"type": "request_current_time"})
    #         response = await asyncio.wait_for(connection.receive_json(), timeout=1.0)
    #         print('resp:', response)
    #         if response.get("type") == "current_time":
    #             return response.get("position", 0.0)
    #     except Exception as e:
    #         print('ERROR FROM _request_current_time:', e)

    async def _send_initial_state(self, websocket: WebSocket, room_state: dict, user_id: str):
        # При подключении к комнате всегда начинаем с паузы
        # Пользователь сам запустит воспроизведение когда будет готов
        message = {
            "type": "init",
            "room": room_state,
            "user_id": user_id,
            "current_time": room_state.get("time_moment", 0),
            "is_playing": False  # Всегда пауза при заходе в комнату
        }

        if room_state.get("list_track") and len(room_state["list_track"]) > 0:
            message.update({
                "track_url": room_state["list_track"][room_state["index_track"]],
            })

        await websocket.send_json(message)

    async def _handle_message(self, data: dict, websocket: WebSocket, room_id: str, user_id: str):
        if not isinstance(data, dict) or "type" not in data:
            return  # Игнорируем некорректные данные

        msg_type = data["type"]
        print(f"[WS] {user_id}: {msg_type}")

        # Heartbeat ping/pong
        if msg_type == "ping":
            await websocket.send_json({"type": "pong"})
            return
        
        # Синхронизация времени из фоновой вкладки (не сбрасывает воспроизведение)
        if msg_type == "sync_time":
            position = data.get("position", 0)
            await self.manager.update_room_state(room_id, {
                "time_moment": position
            })
            return
        
        # Синхронизация состояния (при возврате из фона)
        if msg_type == "sync_state":
            room_state = await self.manager.get_room_state(room_id)
            await websocket.send_json({
                "type": "state_sync",
                "room": room_state,
                "current_time": room_state.get("time_moment", 0),
                "is_playing": room_state.get("status_track", False),
                "track_url": room_state["list_track"][room_state["index_track"]] if room_state.get("list_track") else None,
                "index": room_state.get("index_track", 0)
            })
            return

        if msg_type == "current_time":
            if room_id not in self.time_responses:
                self.time_responses[room_id] = {}
            self.time_responses[room_id][user_id] = data.get("position", 0.0)
            return  # Просто ответ на запрос времени

        if msg_type == "play":
            await self.manager.update_room_state(room_id, {
                "status_track": True,
                "time_moment": data.get("position", 0)
            })
            await self.manager.broadcast(room_id, {
                "type": "play",
                "position": data.get("position", 0)
            }, exclude_user=user_id)

        elif msg_type == "pause":
            await self.manager.update_room_state(room_id, {
                "status_track": False,
                "time_moment": data.get("position", 0)
            })
            await self.manager.broadcast(room_id, {
                "type": "pause",
                "position": data.get("position", 0)
            }, exclude_user=user_id)

        elif msg_type == "seek":
            await self.manager.update_room_state(room_id, {
                "time_moment": data.get("position", 0)
            })
            await self.manager.broadcast(room_id, {
                "type": "seek",
                "position": data.get("position", 0)
            }, exclude_user=user_id)

        elif msg_type == "remove_track":
            # Удаление трека из очереди
            track_index = data.get("index")
            if track_index is not None:
                room_state = await self.manager.get_room_state(room_id)
                tracks = list(room_state.get("list_track", []))
                
                if 0 <= track_index < len(tracks):
                    tracks.pop(track_index)
                    
                    # Корректируем текущий индекс если нужно
                    current_index = room_state.get("index_track", 0)
                    if track_index < current_index:
                        current_index = max(0, current_index - 1)
                    elif track_index == current_index and current_index >= len(tracks):
                        current_index = max(0, len(tracks) - 1)
                    
                    await self.manager.update_room_state(room_id, {
                        "list_track": tracks,
                        "index_track": current_index
                    })
                    
                    # Оповещаем всех участников
                    await self.manager.broadcast(room_id, {
                        "type": "track_removed",
                        "removed_index": track_index,
                        "tracks": tracks,
                        "index": current_index
                    })

        elif msg_type == "change_track":
            tracks = data.get("tracks", [])
            index = data.get("index", 0)
            print(tracks)
            if tracks:
                await self.manager.update_room_state(room_id, {
                    "list_track": tracks,
                    "index_track": index,
                    "status_track": False,
                    "time_moment": 0
                })
                await self.manager.broadcast(room_id, {
                    "type": "load_track",
                    "url": tracks[index]
                })
        elif msg_type == "add_track":
            tracks = data.get("tracks", [])
            index = data.get("index", 0)
            print(tracks)
            if tracks:
                await self.manager.update_room_state(room_id, {
                    "new_track": tracks
                })
                room_state = await self.manager.get_room_state(room_id)
                if len(room_state['list_track']) == 1:
                    await self.manager.broadcast(room_id, {
                    "type": "load_track",
                    "url": room_state['list_track'][0],
                    'index': 0
                })
                clean_url = tracks[0].split("?")[0]
                track_id = clean_url.split("track/")[1].split("/")[0]
                await self.manager.broadcast(room_id, {
                        "type": "add_track",
                        'track_id': track_id,
                        'track_url': tracks[0]  # URL для формирования полных метаданных
                    })
        elif msg_type == "next_track":
            current_time = time.time()
            # Защита от дублирующих запросов (2 секунды)
            if room_id in self.last_track_change and current_time - self.last_track_change[room_id] < 2.0:
                print(f"[WS] Ignoring duplicate next_track from {user_id}")
                return
            self.last_track_change[room_id] = current_time
            
            room_state = await self.manager.get_room_state(room_id)
            new_index = (room_state['index_track'] + 1) % len(room_state['list_track'])
            await self.manager.update_room_state(room_id, {
                    "index_track": new_index,
                    "time_moment": 0,
                    "status_track": True,  # При переключении - воспроизводим
                })
            # Отправляем ВСЕМ участникам, включая инициатора
            await self.manager.broadcast(room_id, {
                    "type": "load_track",
                    "url": room_state['list_track'][new_index],
                    'index': new_index
                })
        elif msg_type == "previous_track":
            current_time = time.time()
            # Защита от дублирующих запросов (2 секунды)
            if room_id in self.last_track_change and current_time - self.last_track_change[room_id] < 2.0:
                print(f"[WS] Ignoring duplicate previous_track from {user_id}")
                return
            self.last_track_change[room_id] = current_time
            
            room_state = await self.manager.get_room_state(room_id)
            # if room_state['time_moment'] > 5:
            #     await self.manager.update_room_state(room_id, {
            #             "time_moment": 0
            #         })
            #     await self.manager.broadcast(room_id, {
            #         "type": "seek",
            #         "position": 0
            #     }, exclude_user=user_id)
            # else:
            new_index = room_state['index_track'] - 1
            new_index = new_index if new_index >= 0 else len(room_state['list_track']) - 1
            await self.manager.update_room_state(room_id, {
                    "index_track": new_index,
                    "time_moment": 0,
                    "status_track": True,  # При переключении - воспроизводим
                })
            # Отправляем ВСЕМ участникам, включая инициатора
            await self.manager.broadcast(room_id, {
                    "type": "load_track",
                    "url": room_state['list_track'][new_index],
                    'index': new_index
                })

        elif msg_type == "get_participants":
            participants = list(self.manager.active_connections.get(room_id, {}).keys())
            # await websocket.send_json({
            #     "type": "participants_update",
            #     "participants": participants
            # })
            await self.manager.update_participants(room_id)

        elif msg_type == "reorder_tracks":
            # Получаем новый порядок треков и текущий индекс
            new_tracks = data.get("tracks", [])
            new_index = data.get("index", 0)
            old_index = data.get("old_index")
            moved_to_index = data.get("new_index")
            
            if new_tracks:
                await self.manager.update_room_state(room_id, {
                    "list_track": new_tracks,
                    "index_track": new_index
                })
                # Оповещаем всех участников о новом порядке
                await self.manager.broadcast(room_id, {
                    "type": "tracks_reordered",
                    "tracks": new_tracks,
                    "index": new_index,
                    "old_index": old_index,
                    "new_index": moved_to_index
                }, exclude_user=user_id)

        elif msg_type == "play_track_by_index":
            # Воспроизведение трека по индексу
            index = data.get("index", 0)
            room_state = await self.manager.get_room_state(room_id)
            
            if room_state.get("list_track") and 0 <= index < len(room_state["list_track"]):
                await self.manager.update_room_state(room_id, {
                    "index_track": index,
                    "time_moment": 0,
                    "status_track": True,  # При выборе трека - воспроизводим
                })
                # Отправляем ВСЕМ участникам, включая инициатора
                await self.manager.broadcast(room_id, {
                    "type": "load_track",
                    "url": room_state["list_track"][index],
                    "index": index
                })

