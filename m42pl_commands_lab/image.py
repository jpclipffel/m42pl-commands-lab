from PIL import Image

from m42pl.commands import GeneratingCommand, StreamingCommand
from m42pl.fields import Field


class Load(GeneratingCommand):
    _about_     = 'Loads an image'
    _syntax_    = '<path>'
    _aliases_   = ['load_image',]

    def __init__(self, path: str):
        super().__init__(path)
        self.path = Field(path, default=path)
    
    async def target(self, event, pipeline):
        path = await self.path.read(event, pipeline)
        event['data']['image'] = {
            'pil': Image.open(path)
        }
        yield event


class Rotate(StreamingCommand):
    _aliases_   = ['rotate_image',]

    def __init__(self, degrees: int = 0):
        super().__init__(degrees)
        self.degrees = Field(degrees, default=degrees)
    
    async def target(self, event, pipeline):
        event['data']['image']['pil'] = event['data']['image']['pil'].rotate(await self.degrees.read(event, pipeline))
        yield event


class Save(StreamingCommand):
    _aliases_   = ['save_image',]

    def __init__(self, path: str):
        super().__init__(path)
        self.path = Field(path, default=path)
    
    async def target(self, event, pipeline):
        event['data']['image']['pil'].save(await self.path.read(event, pipeline))
        yield event
