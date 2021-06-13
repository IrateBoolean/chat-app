from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Query, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, List
from fn_library import ConnectionManager


app = FastAPI()
manager = ConnectionManager()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


async def get_query(
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
async def websocket_endpoint(websocket: WebSocket, query: str = Depends(get_query)):
    user_name, room_id = query
    await manager.connect(user_name, room_id, websocket)
    await manager.download_history_into_page(room_id, websocket)

    print('ready to work')
    while True:
        print(manager.global_data)
        try:
            user_msg = await websocket.receive_text()
            await manager.update_history_into_DB(room_id, user_name, user_msg)
            await manager.broadcast(user_name, room_id, user_msg)
        except WebSocketDisconnect:
            await manager.disconnect(user_name, room_id)
            break
            
