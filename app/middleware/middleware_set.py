from fastapi.responses import JSONResponse
from fastapi import Request, status
from ipaddress import ip_address
from typing import Callable
import re

from app.config.configurate import CorsIpBanned


async def user_agent_ban_middleware(request: Request, call_next:Callable):
    user_agent = request.headers.get('user-agent')
    if user_agent:
        for ban_pattern in CorsIpBanned.USER_AGENTS.value:
            if re.search(ban_pattern, user_agent):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        'detail':'You are banned'
                    }
                )
    response = await call_next(request)
    return response



async def banned_ips_middleware(request: Request, call_next: Callable):
    try:
        ip = ip_address(request.client.host)
    except ValueError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                'detail':'Invalid IP address XXX'
            }
        )
    if ip in CorsIpBanned.IPS.value:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, 
            content={
                "detail": "You are banned"
                }
                )
    response = await call_next(request)
    return response