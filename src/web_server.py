from typing import Dict

from database.engine import session_maker
from database.models import User

from flask import Flask, render_template, request

import requests

from settings import (BITRIX_CLIENT_ID,
                      BITRIX_CLIENT_SECRET,
                      TG_BOT_NICKNAME)

app = Flask("web_server")


def orm_add_user(access_token: str,
                 refresh_token: str,
                 bx_id: int,
                 tg_id: int) -> Dict[str: bool, str: str]:
    try:
        with session_maker() as session:
            session.add(User(
                bx_id=bx_id,
                access_token=access_token,
                refresh_token=refresh_token,
                tg_id=tg_id,
            ))
            session.commit()
        return {"status": True,
                "error": None}
    except Exception as e:
        return {"status": False,
                "error": str(e)}


@app.get("/install")
def get_data():
    url = (f"https://oauth.bitrix.info/oauth/token/?"
           f"grant_type=authorization_code&"
           f"client_id={BITRIX_CLIENT_ID}&"
           f"client_secret={BITRIX_CLIENT_SECRET}&"
           f"code={request.args.get('code')}")
    request_result = requests.request(method="GET", url=url)
    request_result = request_result.json()
    access_token = request_result.get('access_token')
    refresh_token = request_result.get('refresh_token')
    bx_id = request_result.get('user_id')
    tg_id = request.args.get('state')
    add_user_result = orm_add_user(access_token,
                                   refresh_token,
                                   int(bx_id),
                                   int(tg_id))

    return render_template("connect_template.html",
                           connect_status=add_user_result.get("status"),
                           bot_nickname=TG_BOT_NICKNAME
                           )
