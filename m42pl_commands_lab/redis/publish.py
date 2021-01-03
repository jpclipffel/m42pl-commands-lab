import aioredis

from m42pl.commands import StreamingCommand
from m42pl.event import Event
from m42pl.field import Field

from .common import Common


class Command(Common, StreamingCommand):
    __about__   = 'Publish events to a Redis channel'
    __syntax__  = '[channel=]<channel name> [[url=]<redis url>]'
    __aliases__ = ['redis_pub', 'redis_publish', ]
    
    def __init__(self, channel: str, url: str = 'redis://localhost:6379'):
        StreamingCommand.__init__(self, url, channel)
        Common.__init__(self, url)
        self.channel = Field(channel)
    
    async def target(self, event, pipeline):
        client = await self.get_client()
        channel = self.channel.read(event.data)
        await client.publish_json(channel, event.data)
        yield event
