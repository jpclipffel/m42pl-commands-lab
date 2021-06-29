import asyncio
import aiohttp

from m42pl.commands import GeneratingCommand
from m42pl.fields import Field, FieldsMap


class WebSocketServer(GeneratingCommand):
    """Websocket server.
    """

    _about_     = 'Websocket server'
    _syntax_    = '[[host]={host}] [[port]={port}]'
    _aliases_   = ['wsread',]
    

    def __init__(self, host: str = 'localhost', port: int = 8080):
        super().__init__(host, port)
        self.fields = FieldsMap(**{
            'host': Field(host, default=host),
            'port': Field(port, default=port)
        })

    async def target(self, event, pipeline):

        async def handler(request):
            print('Websocket connection starting')
            ws = aiohttp.web.WebSocketResponse()
            await ws.prepare(request)
            print('Websocket connection ready')

            async for msg in ws:
                print(msg)
                if msg.type == aiohttp.WSMsgType.TEXT:
                    print(msg.data)
                    # if msg.data == 'close':
                    #     await ws.close()
                    # else:
                    #     await ws.send_str(msg.data + '/answer')

            print('Websocket connection closed')
            await ws.close()
            return ws

        self.fields = await self.fields.read(event, pipeline)

        app = aiohttp.web.Application()
        app.router.add_route('GET', '/', handler)

        runner = aiohttp.web.AppRunner(app)
        await runner.setup()
        site = aiohttp.web.TCPSite(
            runner,
            self.fields.host,
            self.fields.port,
            reuse_port=True
        )
        await site.start()
        # Run forever
        while True:
            await asyncio.sleep(3600)
        # Mark method as a async generator
        yield
        return
