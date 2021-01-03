import aioredis
import json

from m42pl.commands import GeneratingCommand
from m42pl.event import Event
from m42pl.field import Field

from .common import Common


class Command(Common, GeneratingCommand):
    __about__   = 'Publish events to Redis'
    __syntax__  = '[channel=]<channel name> [[url=]<redis url>] [[format=]{raw|json}]'
    __aliases__ = ['redis_sub', 'redis_subscribe', ]

    formatters = {
        'raw':  lambda msg: msg.decode('UTF-8'),
        'json': lambda msg: json.loads(msg.decode('UTF-8'))
    }

    def __init__(self, channel: str, url: str = 'redis://localhost:6379', format: str = 'raw'):
        self.url = Field(url).read()
        self.channels = [Field(channel).read(), ]
        self.format = Field(format.lower()).read()
        self.formatter = self.formatters.get(self.format, self.formatters['raw'])
        # ---
        Common.__init__(self, url)
        GeneratingCommand.__init__(self, channel, url, format)

    async def target(self, pipeline):
        client = await self.get_client()
        channels = await client.psubscribe(*self.channels)
        # ---
        while True:
            for channel in channels:
                try:
                    channel_name, message = await channel.get()
                    yield Event(data={
                        'redis': {
                            'received': self.formatter(message),
                            'channel': channel_name.decode('UTF-8'),
                            'format': self.format,
                        }
                    })
                except aioredis.RedisError as redis_error:
                    yield Event(data={
                        'redis': {
                            'error': str(redis_error)
                        }
                    })
