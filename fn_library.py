from fn_library_Tier_2 import *
from datetime import datetime


class ConnectionManager():
    def __init__(self):
        self.active_connections = {}  # {room_id: {user_nameid: sock}}
        self.global_data = {}  # {room_id: {msg_time: {username: msg_itself}}}


    async def connect(self, user_name, room_id, websocket):
        await websocket.accept()
        print('User accepted: ', websocket.client[1])  # server notification that someone is connected
        
        try: 
            self.active_connections[room_id].update({user_name: websocket})
        except Exception:
            self.active_connections[room_id] = {user_name: websocket}

        msg = f'User Connected {user_name}'
        await self.broadcast(user_name, room_id, msg)


    async def download_history_into_page(self, room_id, websocket):
        try:
            room_msg = self.global_data[room_id]
            msg_list = await get_ordered_msg_data(room_msg)

            for msg in msg_list:
                await self.send_personal_message(msg, websocket)
        except Exception as ex:
            print(f'Data for this room is empty: {ex}')
            pass


    async def disconnect(self, user_name, room_id):
        print(f'disconnecting {user_name}')
        self.active_connections[room_id].pop(user_name)

        msg = f'{user_name} quited'
        await self.broadcast(user_name, room_id, msg)
        

    async def send_personal_message(self, user_msg: str, websocket):
        await websocket.send_text(user_msg)


    async def broadcast(self, user_name, room_id, user_msg):
        try:
            ref_msg = reformat_user_msg(user_name, user_msg)

            for user in self.active_connections[room_id]:
                user_websocket = self.active_connections[room_id][user]
                await user_websocket.send_text(ref_msg)
        except Exception as ex:
            print(f'Data for this room is empty: {ex}')

    
    async def update_history_into_DB(self, room_id, user_name, user_msg):
        msg_time = datetime.now().strftime("%H:%M:%S")
        try:
            self.global_data[room_id].update({msg_time: {user_name: user_msg}})
        except Exception:  # create new msg theme
            self.global_data[room_id] = {f'{msg_time}': {user_name: user_msg}}

