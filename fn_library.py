from fn_library_Tier_2 import *
from datetime import datetime


async def download_history_into_page(data, room_id, sock):
    try:
        room_msg = data[room_id]
        msg_list = await get_ordered_msg_data(room_msg)
        print(msg_list)

        for n in msg_list:
            await sock.send_text(n)
    except Exception as ex:
        print(f'Data for this room is empty: {ex}')
        pass


async def send_msg_to_users_in_room(sock, user_list, data, user_name):
    try:
        # if sender == None:
        #     sender = sock.client[1]
        for sock in user_list:
            await sock.send_text(f'Message From {user_name}: {data}')
    except Exception as ex:
        print(f'Error in send_msg_to_users_in_room - {ex}')

async def disconnect_user_if_quited(sock, user_list, user_name):
    try:
        # if sender == None:
        #     sender_name = sock.client[1]
        user_list.remove(sock)
        for sock in user_list:
            user_quit = f'user quit {user_name}'
            await sock.send_text(user_quit)
    except Exception as ex:
        print(f'Error, problem in disconnect_user_if_quited {ex}')


async def update_history_into_DB(global_data, room_id, user_name, user_msg):
    msg_time = datetime.now().strftime("%H:%M:%S")
    try:
        global_data[room_id].update({f'{msg_time}': {user_name: user_msg}})
    except Exception:  # create new msg theme
        global_data[room_id] = {f'{msg_time}': {user_name: user_msg}}
    finally:  # for degunning
        print(global_data)


async def reformat_user_data(data_username_roomid):
    print('received: ', data_username_roomid)
    data_username_roomid = data_username_roomid.split(',')
    return data_username_roomid