from fastapi import FastAPI, Request, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fn_library import *


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

user_list = []
global_data = {}  # room_id: {msg_time: {username: msg_itself}}




@app.get("/")
async def get_name(request: Request):
    return templates.TemplateResponse('index_ask_for_name.html', {"request": request})


@app.get("/chat")
async def get(request: Request, Username: str = None, room_id: str = None):
    return templates.TemplateResponse('index.html', {"request": request, "Username": Username, "room_id": room_id})


@app.websocket("/chat/ws")
async def websocket_endpoint(sock: WebSocket):
    await sock.accept()
    print('client accepted: ', sock.client[1])
    user_list.append(sock)

    data_username_roomid = await sock.receive_text()
    username, room_id = await reformat_user_data(data_username_roomid)

    await download_history_into_page(global_data, room_id, sock)

    while True:
        try:
            user_msg = await sock.receive_text()
            print('start history update')
            await update_history_into_DB(global_data, room_id, username, user_msg)
            print('start messeging')
            await send_msg_to_users_in_room(sock, user_list, data=user_msg, user_name=username)
            print('finish cycle')
        except Exception:
            await disconnect_user_if_quited(sock, user_list, user_name=username)
            break
            
