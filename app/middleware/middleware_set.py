from fastapi.responses import JSONResponse
from fastapi import Request, status
from ipaddress import ip_address
from typing import Callable
import re

from app.config.configurate import CorsIpBanned


async def user_agent_ban_middleware(request: Request, call_next: Callable):
    """
    Middleware для блокировки запросов на основе шаблонов  user-agent.

    Этот мидлвар проверяет заголовок User-Agent входящих запросов на
    соответсвие саиску запрещенных шаблонов, определенных в enum
    CorsIpBanned.USER_AGENTS. Если совпаление найденно, возвращаеться ответ
    403 Forbidden с сообезние о блокировке. В противном случае запрос передается
    слудующему мидлвару или конечной точке.

    Args:
        request (Request): входящий запрос.
        call_next (Callable): следующий мидлвар или конечная точка.

    Returns:
        JSONResponse: ответ 403 Forbidden если user-agent заблокирован,
        в противном случаем ответ от слудеющего мидлвара или конечной точке.
    """
    user_agent = request.headers.get("user-agent")
    if user_agent:
        for ban_pattern in CorsIpBanned.USER_AGENTS.value:
            if re.search(ban_pattern, user_agent):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "You are banned"},
                )
    response = await call_next(request)
    return response


async def banned_ips_middleware(request: Request, call_next: Callable):
    """
    Middleware для блокировки запросов с запрещенных IP-адресов..

    Эта асинхронная функция middleware проверяет IP-адрес клиента
    по предопределенному списку запрещенных IP-адресов. Если IP-адрес 
    недействителен или находится в запрещенном списке, возвращается ответ 
    403 Forbidden. В противном случае запрос передается следующему middleware 
    или конечной точке.

    Args:
        request (Request): входящий HTTP-запрос.
        call_next (Callable): следующее middleware или конечная точка для вызова.
    Returns:
        JSONResponse: ответ 403, если IP-адрес запрещен или недействителен, 
        в противном случае
    """
    try:
        ip = ip_address(request.client.host)
    except ValueError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Invalid IP address XXX"},
        )
    if ip in CorsIpBanned.IPS.value:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"}
        )
    response = await call_next(request)
    return response
