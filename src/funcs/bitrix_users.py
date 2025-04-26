from typing import Dict, List
from create_bitrix import bitrix


async def bitrix_get_users(ids: list = None) -> List[Dict[str, str]]:
    params = {
        'filter': {'ACTIVE': True}
    }
    if ids is not None:
        params['filter']["@ID"] = ids
    users = await bitrix.get_all('user.get', params=params)
    return [{"first_name": user.get("NAME"),
             "last_name": user.get("LAST_NAME"),
             "id": user.get("ID")} for user in users]
