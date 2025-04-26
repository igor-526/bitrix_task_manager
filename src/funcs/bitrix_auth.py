from create_bitrix import bitrix
from settings import BITRIX_TG_ID_FIELD


async def get_user_id_by_tg(tg_id: int) -> int | None:
    user = await bitrix.get_all('user.get',
                                params={
                                    'filter': {'ACTIVE': True,
                                               BITRIX_TG_ID_FIELD: tg_id}
                                }
                                )
    return None if not user else user[0]["ID"]
