import zmq
import json
import time

import spell
from spell.commands import StreamingCommand, GeneratingCommand
# from spell.commands.msgpack import Pack, Unpack
from spell.event import Event


ZMQ_CONTEXT = None


class ZMQBase:
    '''Base ZMQ socket wrapper class.
    '''
    def __init__(self, *args, **kwargs) -> None:
        self.socket = None
    
    def __del__(self):
        self.socket.close()
        ZMQ_CONTEXT.destroy()
    
    def setup(self) -> None:
        '''Common ZMQ socket setup.
        '''
        global ZMQ_CONTEXT
        if not ZMQ_CONTEXT:
            ZMQ_CONTEXT = zmq.Context()


class PUB(StreamingCommand, ZMQBase):
    '''ZMQ 'PUB' socket wrapper.
    '''
    __spell_aliases__ = [ "zmq_pub", ]
    
    def __init__(self, url: str = None, host: str = "127.0.0.1", port: int = 5555, topic: str = "spell") -> None:
        '''Initializes the class instance.
        
        :param url: ZMQ URL
        :param host: IP or host to bind on
        :param port: Port to bind on
        :param topic: ZMQ topic
        '''
        super().__init__()
        self.url = url is not None and url or f'tcp://{host}:{port}'
        self.topic = topic.encode()
    
    # def __del__(self):
    #     super().__del__()

    def to_json(self):
        # return { "url": self.url, "topic": self.topic.decode() }
        return { "name": list(self.__spell_aliases__)[0], "kwargs": { "url": self.url, "topic": self.topic.decode() } }

    def target(self, pipeline, event):
        self.setup()
        if not self.socket:
            self.socket = ZMQ_CONTEXT.socket(zmq.PUB)
            self.socket.bind(self.url)
            time.sleep(1) # Awful hack, but currently required.
        # ---
        # Send and return event
        self.socket.send_multipart([self.topic, event])
        return event


class SUB(ZMQBase, GeneratingCommand):
    '''ZMQ 'SUB' socket wrapper.
    '''
    __spell_aliases__ = [ "zmq_sub", ]
    
    def __init__(self, url: str = None, host: str = "127.0.0.1", port: int = 5555, topic: str = "spell"):
        '''Initialize the class instance.

        :param url: ZMQ URL
        :param host: IP or host to bind on
        :param port: Port to bind on
        :param topic: ZMQ topic
        '''
        super().__init__()
        self.url = url is not None and url or f'tcp://{host}:{port}'
        self.topic = topic.encode()

    def to_json(self):
        return { "name": list(self.__spell_aliases__)[0], "kwargs": { "url": self.url, "topic": self.topic.decode() } }

    def target(self, pipeline, event):
        self.setup()
        socket = ZMQ_CONTEXT.socket(zmq.SUB)
        socket.connect(self.url)
        socket.setsockopt(zmq.SUBSCRIBE, self.topic)
        # ---
        # Receives and forwards events
        while True:
            try:
                topic, event = socket.recv_multipart()
                yield event
            except Exception:
                break
        socket.close()
        ZMQ_CONTEXT.destroy()


class SpellPUB(SUB):
    '''A wrapper around :class:`PUB`, optimized for the Spell pipeline.
    '''
    __spell_aliases__ = [ "spell_zmq_pub", ]

    def __new__(cls, *args, **kwargs):
        # return Pack(), PUB(*args, **kwargs)
        return spell.command("msgpack_packb")(), PUB(*args, **kwargs)


class SpellSUB(SUB):
    '''A wrapper around :class:`SUB`, optimized for the Spell pipeline.
    '''
    __spell_aliases__ = [ "spell_zmq_sub", ]
    
    def __new__(cls, *args, **kwargs):
        # return SUB(*args, **kwargs), Unpack()
        return SUB(*args, **kwargs), spell.command("msgpack_unpackb")()
