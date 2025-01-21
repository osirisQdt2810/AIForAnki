from fastapi import FastAPI

from src.app.core.assistant import Engine

class AppLifecycle:
    def __init__(self, app: FastAPI):
        self.app = app
            
    async def init(self):
        """Initialize resources for the application."""
        self.app.anki_assistant = Engine(lazy_loading=False)

    async def start(self):
        """Start the application lifecycle."""
        pass

    async def stop(self):
        """Clean up resources when the application stops."""
        pass

    async def __aenter__(self):
        await self.init()
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.stop()