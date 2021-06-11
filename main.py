from fastapi import FastAPI, Request, WebSocket, Query, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
from fn_library import *


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

user_list = {} # {room_id: {user_nameid: online/offline}}
global_data = {}  # {room_id: {msg_time: {username: msg_itself}}}


async def get_query(
    websocket: WebSocket,
    name: Optional[str] = Query(None),
    room_id: Optional[str] = Query(None),

):
    return name, room_id


@app.get("/")
async def get_name(request: Request):
    return templates.TemplateResponse('index_ask_for_name.html', {"request": request})


@app.get("/chat")
async def get(request: Request, Username: str = None, room_id: str = None):
    return templates.TemplateResponse('index.html', {"request": request, "Username": Username, "room_id": room_id})


@app.websocket("/chat/ws")
async def websocket_endpoint(sock: WebSocket, query: str = Depends(get_query)):
    await sock.accept()
    print('client accepted: ', sock.client[1])
    username, room_id = query

    update_user_list(sock, user_list, room_id, username)


    await download_history_into_page(sock, global_data, room_id)

    while True:
        print('ready to work')
        try:
            print(user_list)
            print(global_data)
            user_msg = await sock.receive_text()
            await update_history_into_DB(global_data, room_id, username, user_msg)
            await send_msg_to_users_in_room(user_list, room_id, username, user_msg)
        except Exception:
            await disconnect_user_if_quited(sock, user_list, room_id, username)
            break
            
