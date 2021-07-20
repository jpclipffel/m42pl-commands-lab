import aiohttp

from m42pl.commands import StreamingCommand
from m42pl.fields import Field
import m42pl


class WebSocketSender(StreamingCommand):
    """Writes events to a websocket.
    """

    _about_     = 'Sends event as JSON to a websocket server'
    _syntax_    = '[[url]=<url>]'
    _aliases_   = ['ws_send',]

    def __init__(self, url: str = 'http://localhost:8080/'):
        super().__init__(url)
        self.url = Field(url, default=url)
        self.encoder = m42pl.encoder('json')()
    
    async def setup(self, event, pipeline):
        self.session = aiohttp.ClientSession()
        self.ws = await self.session.ws_connect(
            await self.url.read(event, pipeline)
        )

    async def target(self, event, pipeline):
        try:
            await self.ws.send_str(self.encoder.encode(event))
        except Exception:
            raise
        yield event

    async def __aexit__(self, *args, **kwargs):
        try:
            await self.session.close()
        except Exception:
            raise
