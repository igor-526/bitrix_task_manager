from typing import Dict, List

from create_bitrix import AsyncBitrixClient


async def bitrix_get_users(bitrix: AsyncBitrixClient,
                           ids: list = None) -> List[Dict[str, str]]:
    filter_params = {'ACTIVE': True}
    if ids is not None:
        filter_params["@ID"] = ids
    select_params = ["ID", "NAME", "LAST_NAME"]
    users = await bitrix.get('user.get',
                             filter_params=filter_params,
                             select_params=select_params)
    return [{"first_name": user.get("NAME"),
             "last_name": user.get("LAST_NAME"),
             "id": user.get("ID")} for user in users["result"]]
