import time
from multiprocessing.connection import Connection

from typing import Any, Tuple, Generator

import m42pl
from m42pl.commands import StreamingCommand, GeneratingCommand
# from m42pl.commands.msgpack import Pack, Unpack


class Receive(GeneratingCommand):
    """Receives events from a :class:`multiprocessing.Connection` object.
    """
    
    _aliases_ = ['mpl_mpi_receive',]
    
    def __new__(cls, *args, **kwargs):
        self = super(Receive, cls).__new__(cls)
        self.__init__(*args, **kwargs)
        # return self, Unpack()
        return self, m42pl.command('msgpack_unpackb')()
    
    def __init__(self, connection: Connection) -> None:
        super().__init__()
        self.connection = connection
    
    async def target(self, event, pipeline) -> Generator:
        self._logger.info('receiving')
        while True:
            try:
                yield self.connection.recv_bytes()
            except EOFError:
                break



class Send(StreamingCommand):
    '''Send events to a :class:`multiprocessing.Connection` object.
    '''
    
    _aliases_ = ['mpl_mpi_send',]
    
    def __new__(cls, *args, **kwargs):
        self = super(Send, cls).__new__(cls)
        self.__init__(*args, **kwargs)
        # return Pack(), self
        return m42pl.command('msgpack_packb')(), self
    
    def __init__(self, connection: Connection) -> None:
        super().__init__()
        self.connection = connection
    
    async def target(self, event, pipeline):
        self._logger.info('sending')
        try:
            self.connection.send_bytes(event)
            yield event
        except Exception:
            pass
