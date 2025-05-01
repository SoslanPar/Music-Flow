from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    Depends,
    WebSocket,
    Response,
    Cookie,
)
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    StreamingResponse,
    Response,
    RedirectResponse,
)
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from yandex_music import Client
from dotenv import load_dotenv
import requests
import json
import os
import sqlalchemy

from services.rooms_services import RoomsServices
from services.users_services import UserServices
from services.tokens_services import TokenServices

from models.Users import Users
from models.Rooms import Rooms

from db.base import Database
from wbs.websocket_manager import ConnectionManager
from wbs.websocket_routes import WebSocketRoutes

# from db.base import Database


load_dotenv()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Или конкретный домен, например ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
db = Database()
manager = ConnectionManager(db)
templates = Jinja2Templates(directory="templates")
OAUTH_TOKEN = os.getenv("OAUTH_TOKEN")
CLIENT_ID = os.getenv("YANDEX_CLIENT_ID")
CLIENT_SECRET = os.getenv("YANDEX_CLIENT_SECRET")
# REDIRECT_URI = "http://localhost:8000/callback"
REDIRECT_URI = "https://fjxp38df-8000.euw.devtunnels.ms/callback"
DOMAIN = "developmental-educators-allergy-civilization.trycloudflare.com"
# client = Client(OAUTH_TOKEN).init()
# DOMAIN = "localhost"
# Инициализация клиента Яндекс.Музыки
# client = Client(OAUTH_TOKEN).init()

ws_routes = WebSocketRoutes(manager)


@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    await ws_routes.handle_websocket(websocket, room_id, user_id)


@app.get("/", response_class=HTMLResponse)
async def player_page(request: Request):
    cookies = request.cookies
    print(cookies)
    return templates.TemplateResponse("player.html", {"request": request})


@app.get("/join-room")
async def join_room(room_id: str, request: Request):
    return RedirectResponse(f"/room/{room_id}")


@app.websocket("/room/{room_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket, room_id: str, user_id: str = Cookie(None)
):
    if not user_id:
        await websocket.close(code=4001, reason="User ID cookie required")
        return

    await ws_routes.handle_websocket(websocket, room_id, user_id)


@app.get("/room/{room_id}", response_class=HTMLResponse)
async def get_room_page(request: Request, room_id: str):
    # Проверяем существование комнаты
    async with db.session_factory() as session:

        room = await session.get(Rooms, room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
    cookies = request.cookies
    # print(f'Cookie in room: {cookies}')
    return templates.TemplateResponse(
        "room.html", {"request": request, "room_id": room_id}
    )


@app.get("/get_cookie")
async def get_cookie(request: Request):
    try:
        cookies = request.cookies
        # print(f'after join: {cookies}')
        return Response(content=json.dumps(cookies), status_code=200)
    except Exception as e:
        return Response(content=json.dumps({"error": str(e)}), status_code=500)


@app.get("/check_token")
async def check_token(token: str, db: Database = Depends(Database)):
    try:
        # 1. Проверяем токен в БД
        user_services = UserServices(db)
        existing_user = await user_services.check_yandex_token(token)

        if existing_user:
            return JSONResponse(
                {
                    "status": "authenticated",
                    "user_id": str(existing_user.id),
                    "username": existing_user.username,
                    "action": "login",
                    "success": True,
                }
            )

        try:
            profile = await user_services.get_yandex_profile(token)
            login = profile.get("login")
            email = profile.get("default_email", "None")
            birthday = profile.get("birthday", "None")
            # Проверки на пустые поля
            email = email if email else None
            login = login if login else None
            birthday = birthday if birthday else None
            if not login:
                raise HTTPException(
                    status_code=400, detail="Не удалось получить логин Яндекса"
                )

            new_user = await user_services.create_new_user(
                email=email,
                password="12345",
                username=login,
                birthday=birthday,
                yandex_token=token,
                rooms_list=[],
            )
            return JSONResponse(
                {
                    "status": "registered",
                    "user_id": str(new_user.id),
                    "username": login,
                    "action": "register",
                    "success": True,
                }
            )
        except Exception as e:
            print(str(e))
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера(registered)"
            )

    except Exception as e:
        print(str(e))
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка сервера(/check_token)"
        )


@app.get("/auth/current-user")
async def get_current_user(user_id: str = Cookie(None)):
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    async with db.session_factory() as session:
        user = await session.get(Users, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {"id": user.id, "username": user.username}


async def get_access_token(code: str):
    """
    Обмен кода авторизации на токен доступа.
    """
    token_url = "https://oauth.yandex.ru/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    print("response")
    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Ошибка при получении токена")
    # print(response.json())
    return response.json().get("access_token")


@app.post("/create_room")
async def create_room(
    request: Request, name_rooms: str = None, db: Database = Depends(Database)
):
    if not (name_rooms):
        return Response(
            content=json.dumps(
                {"Status": "Error", "Message": "Введите название комнаты"}
            ),
            status_code=500,
        )
    cookies = request.cookies
    # print(cookies)
    if "user_id" not in cookies and not (cookies["user_id"]):
        # print(1)
        return Response(
            content=json.dumps({"Status": "Error", "Message": "Авторизуйтесь"}),
            status_code=500,
        )
    resp = RoomsServices(db)
    user_model = UserServices(db)
    # print(name_rooms)
    try:
        done = await resp.create_room(name_rooms, cookies["user_id"])
        op = await user_model.add_room(str(done["id"]), cookies["user_id"])
        # print(type(done))
    except sqlalchemy.exc.IntegrityError as e:
        return Response(
            content=json.dumps({"Status": "Error", "Message": str(e)}), status_code=500
        )
    done = await resp.get_all()
    # print(done)
    return Response(content=json.dumps(done), status_code=200)


@app.get("/auth/sign-in")
async def auth_login(
    request: Request,
    response: Response,
    nickname: str,
    hashed_password: str,
    db: Database = Depends(Database),
):
    try:
        # obj = await request.json()
        obj = {"nickname": nickname, "hashed_password": hashed_password}

        user_model = UserServices(db)
        token_model = TokenServices(db)

        user = await user_model.logging(obj)

        if user:
            # token = await token_model.new_token(obj=obj, user_id=user.id)
            usr_id = user.id
            response = JSONResponse(
                content=json.dumps(
                    {"status": "Successfully hui", "user_id": str(usr_id)}
                ),
                status_code=200,
            )
            response.set_cookie(
                key="user_id",
                value=str(usr_id),
                httponly=True,
                secure=False,
                samesite="lax",
                domain=DOMAIN,  # Явное указание домена
                path="/",
            )
            return response
        return {"status": "error", "message": "Неправильный логин или пароль"}
    except Exception as e:
        print(e)
        return {"message": str(e)}


@app.get("/callback")
async def callback(code: str):
    # print(f'code: {code}')
    """
    Обработка перенаправления от Yandex и получение токена доступа.
    """
    global access_token
    access_token = await get_access_token(code)
    return {"message": "Авторизация успешна", "access_token": access_token}


@app.get("/stream")
async def stream_audio(url: str, request: Request):
    try:
        # # Удаляем лишние параметры из URL
        # print(f'TOKEN: {OAUTH_TOKEN}')
        user_id = request.cookies["user_id"]
        user_model = UserServices(db)
        print(user_id)
        yan_tok = await user_model.get_yandex_token_by_user_id(user_id=user_id)
        # print(f'Token from bd: {yan_tok}')
        print(f"{user_id} - {yan_tok}")
        client = Client(yan_tok if yan_tok else OAUTH_TOKEN).init()
        clean_url = url.split("?")[0]
        track_id = clean_url.split("track/")[1].split("/")[0]

        # Получаем трек
        track = client.tracks(track_id)[0]
        download_info = track.get_download_info(get_direct_links=True)[0]
        stream_url = download_info.get_direct_link()

        # Проверяем ссылку
        test_request = requests.head(stream_url)
        if test_request.status_code != 200:
            return {"error": "Не удалось получить аудиопоток"}
        response = requests.get(stream_url)
        print(response.json)

        # Потоковая передача
        # def generate():
        #     with requests.get(stream_url, stream=True) as r:
        #         print(r)
        #         for chunk in r.iter_content(chunk_size=32768):  # Увеличенный буфер
        #             if chunk:
        #                 yield chunk
        #                 del chunk
        def generate():
            stream_url = download_info.get_direct_link()
            with requests.get(stream_url, stream=True) as r:
                for chunk in r.iter_content(chunk_size=32768):
                    if chunk:
                        yield chunk

        return StreamingResponse(
            generate(),
            media_type="audio/mpeg",
            headers={
                "Track-Info": json.dumps(
                    {
                        "title": track.title,
                        "artist": track.artists[0].name,
                        "cover": f"https://{track.cover_uri.replace('%%', '400x400')}",
                    }
                ),
                "Accept-Ranges": "bytes",
                "Content-Length": str(len(response.content)),  # Важно указать размер
                "Content-Type": "audio/mpeg",
            },
        )

    except Exception as e:
        print(e)
        return {"error": str(e)}
    # @app.get("/stream")
    # async def stream_audio(url: str):
    #     try:
    #         clean_url = url.split('?')[0]
    #         track_id = clean_url.split('track/')[1].split('/')[0]

    #         track = client.tracks(track_id)[0]
    #         download_info = track.get_download_info(get_direct_links=True)[0]
    #         stream_url = download_info.get_direct_link()

    #         # Загружаем весь трек за один запрос
    #         response = requests.get(stream_url)
    #         if response.status_code != 200:
    #             return {"error": "Не удалось получить аудиопоток"}

    #         audio_data = response.content

    #         # Формируем заголовки
    #         headers = {
    #             "Track-Info": json.dumps({
    #                 "title": track.title,
    #                 "artist": track.artists[0].name,
    #                 "cover": f"https://{track.cover_uri.replace('%%', '400x400')}"
    #             }),
    #             "Content-Length": str(len(audio_data))  # Важно указать размер
    #         }

    #         # Отправляем полный файл
    #         return Response(
    #             content=audio_data,
    #             media_type="audio/mpeg",
    #             headers=headers
    #         )

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        port=8000,
        reload=True,  # Автоперезагрузка при изменениях
    )
