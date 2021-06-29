import cv2

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class CV2Show(StreamingCommand):
    _aliases_   = ['cv2_show',]

    def __init__(self, field: str = "cv2.frame"):
        super().__init__(field)
        self.field = Field(field)
    
    async def target(self, event, pipeline):
        try:
            cv2.imshow('Camera', await self.field.read(event, pipeline))
            cv2.waitKey(10)
        except Exception as error:
            self.logger.exception(error)
        yield event

    async def __aexit__(self, *args, **kwargs):
        try:
            cv2.waitKey(1)
            cv2.destroyAllWindows()
        except Exception:
            pass
