import asyncio
import aiohttp

from m42pl.commands import GeneratingCommand
from m42pl.fields import Field, FieldsMap
from m42pl.event import Event


class WebSocketHub(GeneratingCommand):
    """Websocket server which receive and forward.
    """

    _about_     = 'Websocket hub'
    _syntax_    = '[[host]={host}] [[port]={port}]'
    _aliases_   = ['ws_receive', 'ws_recv']

    def __init__(self, piperef: str, host: str = 'localhost', port: int = 8080):
        super().__init__(piperef, host, port)
        self.piperef = Field(piperef, default=piperef)
        self.fields = FieldsMap(**{
            'host': Field(host, default=host),
            'port': Field(port, default=port)
        })
