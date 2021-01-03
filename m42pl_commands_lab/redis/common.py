import aioredis


class Common:
    '''Common Redis wrapper for M42PL commands.
    '''

    def __init__(self, url: str):
        '''Initializes class instance.

        :param url:     Redis URL
        :attr client:   Redis client instance (initialzed later)
        '''
        self.url = url
        self.client = None

    async def get_client(self):
        '''Returns newly initialized Redis client or existing one.
        '''
        if not self.client:
            self.client = await aioredis.create_redis_pool(self.url)
        return self.client

    async def __aexit__(self, *args, **kwargs):
        '''Properly close Redis client.
        '''
        if self.client:
            self.client.close()
            await self.client.wait_closed()
