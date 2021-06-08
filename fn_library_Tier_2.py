async def get_ordered_msg_data(data):
    msg_list = []
    try:
        for msg_time in data:
            for user_name in data[msg_time]:
                user_msg = data[msg_time][user_name]
                msg = f'{msg_time} - {user_name}: {user_msg}'
                msg_list.append(msg)
        return msg_list
    except Exception as ex:
        print(f'Broken in get_ordered_msg_data: {ex}')
        pass