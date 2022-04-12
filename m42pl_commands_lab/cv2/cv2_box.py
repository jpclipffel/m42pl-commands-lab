import cv2

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class CV2Box(StreamingCommand):
    """Draws boxes on a CV2 frame.

    The command is reading objects coordinates and 
    """

    _aliases_   = ['cv2_box', 'cv2_boxes']
    _syntax_    = '[[frame=]{frame field}], [[objects=]{objects}]'
    _about_     = 'Draws boxes on OpenCV2 frames'

    def __init__(self, frame: str = 'cv2.frame', objects: str = 'cv2.objects'):
        self.frame = Field(frame)
        self.objects = Field(objects, default=[], seqn=True)

    async def target(self, event, pipeline):
        for obj in await self.objects.read(event, pipeline):
            # We're expecting only objects with 4 values:
            # x, y, w, h, w
            if isinstance(obj, (list, tuple)) and len(obj) == 4:

