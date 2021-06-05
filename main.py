from fastapi import FastAPI, WebSocket, Form
from fastapi.responses import HTMLResponse
from typing import List, Optional
from time import sleep

from starlette.requests import Request

app = FastAPI()
user_list = []


async def send_msg_to_all(data, sender=None):
    if sender:
        for sock in user_list:
            await sock.send_text(f'Message From {sender}: {data}')
    else:
        for sock in user_list:
            print('sending quit')
            await sock.send_text(data)


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <p>Hello {{Username}}</p>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/chat/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


html_name_input = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <form method="GET" action="http://127.0.0.1:8000/chat">
        <label for="Username">Your Nickname</label>
        <input name="Username" id="Username" type="text" value="">
        <input type="submit">
    </form>
</body>
</html>
"""

@app.get("/")
async def get_name(Username: str = None):
    return HTMLResponse(html_name_input)


@app.get("/chat/")
async def get():
    return HTMLResponse(html)


@app.websocket("/chat/ws")
async def websocket_endpoint(sock: WebSocket):
    await sock.accept()
    Username = 'anymos'
    print('client accepted: ', Username)
    user_list.append(sock)
    while True:
        try:
            data = await sock.receive_text()
        except Exception:
            if sock in user_list:
                user_list.remove(sock)

                user_quit = f'user quit {Username}'
                await send_msg_to_all(data=user_quit)
            break
        else:
            await send_msg_to_all(sender=Username, data=data)
