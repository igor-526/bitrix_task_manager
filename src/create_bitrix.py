import datetime
from pprint import pprint
from typing import Any, Dict

import aiohttp

from database.engine import async_session_maker
from database.models import User

from settings import BITRIX_BASE_URL, BITRIX_CLIENT_ID, BITRIX_CLIENT_SECRET

from sqlalchemy import select, update


class BitrixException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        return self.message if self.message else \
            "В библиотеке API Битрикс24 произошла ошибка"


class AsyncBitrixClient:
    access_token: str
    refresh_token: str
    method: str
    user_id: int

    def __init__(self, access_token: str,
                 refresh_token: str, user_id: int) -> None:
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.rest_url = BITRIX_BASE_URL
        self.user_id = user_id

    async def _refresh_token(self) -> None:
        new_access_token = None
        new_refresh_token = None
        async with aiohttp.ClientSession() as session:
            params = {
                'client_id': BITRIX_CLIENT_ID,
                'client_secret': BITRIX_CLIENT_SECRET,
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
            response = await session.get(
                url='https://oauth.bitrix.info/oauth/token',
                params=params
            )
            if response.status == 200:
                response = await response.json()
                new_access_token = response.get("access_token")
                new_refresh_token = response.get("refresh_token")
        async with async_session_maker() as session:
            query = select(User).where(User.bx_id == self.user_id)
            user = (await session.execute(query)).scalar_one_or_none()
            if user is None:
                pass
            query = update(User).where(
                User.id == user.id
            ).values(access_token=new_access_token,
                     refresh_token=new_refresh_token)
            await session.execute(query)
            await session.commit()
        self.access_token = new_access_token
        self.refresh_token = new_refresh_token

    async def _prepare_response(self, response):
        json_response = await response.json()
        if response.status == 200:
            return json_response
        print(response.status)
        pprint(json_response)
        if response.status == 401:
            if json_response.get('error') == 'expired_token':
                await self._refresh_token()
                return {"token_refreshed": True}
            raise BitrixException(json_response.get("error"))
        if response.status == 400:
            raise BitrixException(json_response.get("error"))

    def _get_url(self, endpoint,
                 select_params=None, filter_params=None) -> str:
        url_params = []
        if filter_params is None:
            filter_params = {}
        if select_params is None:
            select_params = []
        for param in select_params:
            url_params.append(f'select[]={param}')
        for filter_param in filter_params:
            if type(filter_params[filter_param]) is list:
                for param in filter_params[filter_param]:
                    url_params.append(f'filter[{filter_param}][]={param}')
            else:
                url_params.append(f'filter[{filter_param}]='
                                  f'{filter_params[filter_param]}')
        url_params.append(f'auth={self.access_token}')
        return f"{BITRIX_BASE_URL}rest/{endpoint}?{'&'.join(url_params)}"

    async def get(self, endpoint, select_params: list = None,
                  filter_params: dict = None) -> dict:
        async with aiohttp.ClientSession() as session:
            response = await session.get(self._get_url(endpoint,
                                                       select_params,
                                                       filter_params))
            response = await self._prepare_response(response)
            if response.get("token_refreshed"):
                return await self.get(endpoint, select_params, filter_params)
            return response

    def check_param(self, param: Any) -> str | int | None:
        if type(param) is datetime.datetime:
            return param.isoformat()
        return param

    def _get_post_params(self, fields: dict = None, **kwargs) \
            -> Dict[str, Any]:
        params = {
            "auth": self.access_token,
            **kwargs
        }
        if fields:
            for field in fields:
                if type(fields[field]) is list:
                    for i, param in enumerate(fields[field]):
                        params[f'fields[{field}][{i}]'] = (
                            self.check_param(param)
                        )
                else:
                    params[f'fields[{field}]'] = (
                        self.check_param(fields[field])
                    )
        return params

    async def post(self, endpoint: str, fields: dict = None,
                   **kwargs) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                url=f'{BITRIX_BASE_URL}rest/{endpoint}/',
                params=self._get_post_params(fields, **kwargs))
            response = await self._prepare_response(response)
            if response.get("token_refreshed"):
                return await self.post(endpoint, fields, **kwargs)
            return response
