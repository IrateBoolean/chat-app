from fn_library_Tier_2 import *
from datetime import datetime


async def download_history_into_page(sock, global_data, room_id):
    try:
        room_msg = global_data[room_id]
        msg_list = await get_ordered_msg_data(room_msg)

        for n in msg_list:
            await sock.send_text(n)
    except Exception as ex:
        print(f'Data for this room is empty: {ex}')
        pass


async def send_msg_to_users_in_room(user_list, room_id, user_name, user_msg):
    try:
        ref_msg = reformat_user_msg(user_name, user_msg)
        for user in user_list[room_id]:
            user_sock = user_list[room_id][user]
            await user_sock.send_text(ref_msg)

    except Exception as ex:
        print(f'Error in send_msg_to_users_in_room - {ex}')


async def disconnect_user_if_quited(sock, user_list,room_id, user_name):
    try:
        user_list[room_id].pop(user_name)
        for user in user_list[room_id]:
            user_sock = user_list[room_id][user]

            user_quit = f'user quit {user_name}'
            await user_sock.send_text(user_quit)
    except Exception as ex:
        print(f'Error, problem in disconnect_user_if_quited {ex}')


async def update_history_into_DB(global_data, room_id, user_name, user_msg):
    msg_time = datetime.now().strftime("%H:%M:%S")
    try:
        global_data[room_id].update({msg_time: {user_name: user_msg}})
    except Exception:  # create new msg theme
        global_data[room_id] = {f'{msg_time}': {user_name: user_msg}}


def update_user_list(sock, user_list, room_id, user_name):
    try:
        user_list[room_id].update({user_name: sock})
    except Exception:
        user_list[room_id] = {user_name: sock}
        pass




