import time

from fastapi import Request, Response
from fastapi.routing import APIRoute

from src.helpers.logging.logger import logger

class TimerRoute(APIRoute):
    def get_route_handler(self):
        route_handler = super().get_route_handler()
        async def app(request: Request) -> Response:
            timing = time.time()
            response: Response = await route_handler(request)
            duration = time.time() - timing
            if request.method in ["POST", "DELETE", "PUT"]:
                logger.info(f"Received request: {request.method} - {request.url}")
                logger.debug(f"Route {duration = }")
                response.headers["X-Response-Time"] = str(duration)
            
            return response
        return app
