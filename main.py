from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

user_list = []


async def send_msg_to_all(data, sender=None):
    if sender:
        for sock in user_list:
            await sock.send_text(f'Message From {sender}: {data}')
    else:
        for sock in user_list:
            print('sending quit')
            await sock.send_text(data)



@app.get("/")
async def get_name(request: Request):
    return templates.TemplateResponse('index_ask_for_name.html', {"request": request})


@app.get("/chat")
async def get(request: Request, Username: str = None):
    return templates.TemplateResponse('index.html', {"request": request, "Username": Username})


@app.websocket("/chat/ws")
async def websocket_endpoint(sock: WebSocket):
    await sock.accept()
    print('client accepted: ', sock.client[1])
    user_list.append(sock)
    while True:
        try:
            data = await sock.receive_text()
            data = data.split(',')
            Username = data[0]
            user_msg = data[1]
        except Exception:
            if sock in user_list:
                user_list.remove(sock)

                user_quit = f'user quit {Username}'
                await send_msg_to_all(data=user_quit)
            break
        else:
            await send_msg_to_all(sender=Username, data=user_msg)
