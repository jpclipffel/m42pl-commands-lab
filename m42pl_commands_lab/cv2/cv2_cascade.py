import cv2

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class CV2Cascade(StreamingCommand):
    """Applies a CV2 cascade classifier.
    """
    
    _aliases_   = ['cv2_cascade',]
    _syntax_    = '[src=]{source field}'
    _about_     = 'Apply an OpenCV2 cascade classifier'

    def __init__(self, src: str = 'cv2.frame', dest: str = 'cv2.objects'):
        self.src = Field(src)
        self.dest = Field(dest, default=[], seqn=True)
        # ---
        self.classifier = cv2.CascadeClassifier()
        self.classifier.load('/Users/jpc/Stash/opencv/haarcascade_frontalface_alt.xml')

    async def target(self, event, pipeline):
        # Read frame
        frame = await self.src.read(event, pipeline)
        if frame is not None:
            # DEBUG - Greyscale frame
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame_gray = cv2.equalizeHist(frame_gray)
            # ---
            # Get already found objects
            objects = await self.dest.read(event, pipeline)
            # Find objects
            found = self.classifier.detectMultiScale(frame_gray)
            # Add found objects
            for x, y, h, w in found:
                objects.append([
                    float(x),
                    float(y),
                    float(h),
                    float(w)
                ])
                # DEBUG - Show objects
                center = (x + w//2, y + h//2)
                frame = cv2.ellipse(
                    frame, 
                    center, 
                    (w//2, h//2), 0, 0, 360, (255, 0, 255), 4
                )
                # ---
            # DEBUG - Update frame
            await self.src.write(event, frame)
            # ---
            # Done
            yield await self.dest.write(event, objects)
        else:
            yield event
