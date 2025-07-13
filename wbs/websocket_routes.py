import asyncio
import uuid
import time
from fastapi import WebSocket, WebSocketDisconnect
from .websocket_manager import ConnectionManager  # Импортируй правильно свой файл!

class WebSocketRoutes:
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
        self.message_queues = {}
        self.time_responses = {}
        self.last_track_change = 0

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
            # Получаем актуальное время
            current_position = await self._get_consensus_time(room_id, exclude_user=user_id)

            await self.manager.update_room_state(room_id, {"time_moment": current_position})
            room_state["time_moment"] = current_position

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
        # Запрашиваем время у всех участников
        await self.manager.get_current_playback_time(room_id, exclude_user)

        # Ждём ответы (например, 1 секунду)
        await asyncio.sleep(1.0)

        # Собираем все ответы
        if room_id not in self.time_responses:
            return 0.0

        responses = self.time_responses[room_id].values()
        if not responses:
            return 0.0

        # Берём среднее время (или первый ответ)
        avg_time = sum(responses) / len(responses)
        return avg_time
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
        message = {
            "type": "init",
            "room": room_state,
            "user_id": user_id,
            "current_time": room_state.get("time_moment", 0),
            "is_playing": room_state.get("status_track", False)
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
        print(msg_type)

        if msg_type == "current_time":
            if room_id not in self.time_responses:
                self.time_responses[room_id] = {}
            self.time_responses[room_id][user_id] = data.get("position", 0.0)
            return  # Просто ответ на запрос времени

        if msg_type == "play":
            # await self.manager.update_room_state(room_id, {
            #     "status_track": True,
            #     "time_moment": data.get("position", 0)
            # })
            await self.manager.broadcast(room_id, {
                "type": "play",
                "position": data.get("position", 0)
            }, exclude_user=user_id)

        elif msg_type == "pause":
            # await self.manager.update_room_state(room_id, {
            #     "status_track": False,
            #     "time_moment": data.get("position", 0)
            # })
            await self.manager.broadcast(room_id, {
                "type": "pause",
                "position": data.get("position", 0)
            }, exclude_user=user_id)

        elif msg_type == "seek":
            # await self.manager.update_room_state(room_id, {
            #     "time_moment": data.get("position", 0)
            # })
            await self.manager.broadcast(room_id, {
                "type": "seek",
                "position": data.get("position", 0)
            }, exclude_user=user_id)

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
                        'track_id': track_id
                    })
        elif msg_type == "next_track":
            current_time = time.time()
            # if hasattr(self, 'last_track_change') and current_time - self.last_track_change < 4.0:
            #     return
            self.last_track_change = current_time
            room_state = await self.manager.get_room_state(room_id)
            new_index = (room_state['index_track'] + 1) % len(room_state['list_track'])
            await self.manager.update_room_state(room_id, {
                    "index_track": new_index,
                    "time_moment": 0,
                    "status_track": False,
                })
            await self.manager.broadcast(room_id, {
                    "type": "load_track",
                    "url": room_state['list_track'][new_index],
                    'index': new_index
                })
        elif msg_type == "previous_track":
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
                    "status_track": False,
                })
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

