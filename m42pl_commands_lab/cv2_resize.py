import cv2

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class CV2Resize(StreamingCommand):
    _aliases_   = ['cv2_resize',]
    _about_     = 'Resize an OpenCV2 frame'
    _syntax_    = '[[field=]{frame}] [[ratio=]{float}]'

    def __init__(self, field: str = 'cv2.frame', ratio: float = 1.0):
        super().__init__(field)
        self.field = Field(field)
        self.ratio = Field(ratio, default=1.0)

    async def target(self, event, pipeline):
        try:
            ratio = await self.ratio.read(event, pipeline)
            await self.field.write(
                event,
                cv2.resize(
                    await self.field.read(event, pipeline),
                    (0, 0),
                    fx=ratio,
                    fy=ratio
                )
            )
        except Exception as error:
            self.logger.exception(error)
        yield event

