from typing import Tuple

import aiohttp
from loguru import logger

EMPTY_RESPONSE: str = "[]"

BASE_PATH: str = "https://ws.infotbm.com/ws/1.0"

_STOP_INFO_ENDPOINT: str = f"{BASE_PATH}/network/stoparea-informations/"
_LINE_INFO_ENDPOINT: str = f"{BASE_PATH}/network/line-informations/"
_ALERT_INFO_ENDPOINT: str = f"{BASE_PATH}/alerts/by-transport/"
_SEARCH_ENDPOINT: str = f"{BASE_PATH}/get-schedule/"
_SCHEDULE_ENDPOINT: str = f"{BASE_PATH}/get-realtime-pass/"


async def _make_request(__base_path: str, __resource: str) -> Tuple[int, str]:
    _full_path: str = f"{__base_path}{__resource}"
    logger.debug(f"Target url '{_full_path}'")

    async with aiohttp.ClientSession() as session:
        async with session.get(_full_path) as response:
            status: int = response.status
            if status != 200:
                logger.error(
                    f"Url '{_full_path}' returned an invalid status code ({status})"
                )
                return status, ""

            content: str = await response.text()
            if content == EMPTY_RESPONSE:
                logger.warning(
                    f"Url '{_full_path}' returned a valid status code ({status}) but no content"
                )
                return 404, ""

            logger.debug(f"Target status: {response.status}")
            logger.debug(f"Target content: {content}")
            logger.success(
                f"Url '{_full_path}' returned a valid status code ({status}) and a content"
            )
            return status, content


async def get_line_info(line_id: str) -> Tuple[int, str]:
    return await _make_request(_LINE_INFO_ENDPOINT, line_id)


async def get_stop_info(stop_id: str) -> Tuple[int, str]:
    return await _make_request(_STOP_INFO_ENDPOINT, stop_id)


async def get_line_alerts(line_id: str) -> Tuple[int, str]:
    return await _make_request(_ALERT_INFO_ENDPOINT, line_id)


async def get_stop_schedule(stop_code: str, line_id: str) -> Tuple[int, str]:
    return await _make_request(_SCHEDULE_ENDPOINT, f"{stop_code}/{line_id}")


async def search_for(query: str) -> Tuple[int, str]:
    return await _make_request(_SEARCH_ENDPOINT, query)


async def get(query: str) -> Tuple[int, str]:
    return await _make_request(BASE_PATH, query)
