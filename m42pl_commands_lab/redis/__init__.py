from . import publish, subscribe


# import aioredis

# from m42pl.commands import StreamingCommand
# from m42pl.event import Event


# class Command(StreamingCommand):
#     __about__   = 'Executes a Redis command'
#     __syntax__  = '[[command=]<command>]] [[host=]<host>] [[port=]<port>] [...]'
#     __aliases__ = ["redis", ]
    
    
#     def __init__(self, command: str = 'PING', url: str = 'redis://localhost:6379', *args):
#         super().__init__(command.upper(), url, args)
#         self.client = None
#         self.command = [command.upper(), ] + list(*args)
#         self.url = url
        
#     async def target(self, pipeline, event):
#         if not self.client:
#             self.client = await aioredis.create_redis_pool(self.url)
#         print(f'redis.Command --> execute: {self.command}')
#         yield Event(data={
#             'redis': {
#                 'query': {
#                     'command': self.command[0],
#                     'arguments': self.command[1:]
#                 },
#                 'answer': str(await self.client.execute(*self.command))
#             }
#         })

#     async def __aexit__(self, *args, **kwargs):
#         if self.client:
#             self.client.close()
#             await self.client.wait_closed()
