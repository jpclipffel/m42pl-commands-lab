from __future__ import annotations
import cv2

from m42pl.commands import GeneratingCommand
from m42pl.fields import Field
from m42pl.event import Event


class CV2Read(GeneratingCommand):
    """Reads a file or a stream with OpenCV.
    """
    
    _aliases_   = ['cv2_read',]
    _syntax_    = '[source=]{source device} [[retries=]<retries count>]'
    _about_     = 'Read a stream with OpenCV'

    _schema_ = {
        'properties': {
            'cv2': {
                'type': 'object',
                'properties': {
                    'frame': {
                        'description': 'Read frame'
                    },
                    'source': {
                        'description': 'Source stream name',
                        'type': 'string'
                    }
                }
            }
        }
    }

    def __init__(self, source: str|int = 0, retries: int = -1):
        """
        :param source:  Source stream
                        Default to `0` (webcam)
        """
        super().__init__()
        self.source = Field(source, default=0)
        self.retries = Field(retries, default=-1)
        self.stream = None

    async def setup(self, event, pipeline):
        self.source = await self.source.read(event, pipeline)
        self.retries = await self.retries.read(event, pipeline)

    def cap_read(self):
        # (re)open source stream
        if not self.stream:
            self.stream = cv2.VideoCapture(self.source)
        # Read next frame
        status, frame = self.stream.read()
        if not status or frame is None or len(frame) < 1:
            raise Exception((
                f'Error while reading frame: status="{status}", '
                f'frame="{type(frame)}"'
            ))
        return frame

    async def target(self, event, pipeline):
        while self.retries != 0:
            try:
                yield Event(data={
                    'cv2': {
                        'frame': self.cap_read(),
                        'source': self.source
                    }
                })
            except Exception as error:
                self.logger.exception(str(error))
                self.logger.info(f'closing stream')
                self.stream.release()
                self.stream = None
                if self.retries >= 0:
                    self.retries -= 1

    async def __aexit__(self, *args, **kwargs):
        try:
            if self.stream:
                self.logger.info(f'closing stream')
                self.stream.release()
        except Exception:
            pass
