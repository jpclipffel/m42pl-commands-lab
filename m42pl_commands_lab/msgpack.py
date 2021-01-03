import msgpack

from m42pl.commands import StreamingCommand
from m42pl.event import Event


class Pack(StreamingCommand):
    _aliases_ = ['msgpack_packb',]
    
    def __init__(self):
        super().__init__()

    async def target(self, event, pipeline):
        self._logger.info("packing")
        yield msgpack.packb({
            "data": event.data,
            "signature": event.signature
        })


class Unpack(StreamingCommand):
    _aliases_ = ['msgpack_unpackb',]
    
    def __init__(self):
        super().__init__()

    async def target(self, event, pipeline):
        self._logger.info("unpacking")
        yield Event(**msgpack.unpackb(event))
