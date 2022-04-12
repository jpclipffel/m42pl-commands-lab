import cv2
import mediapipe as mp

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class MPFaces(StreamingCommand):
    """Mediapipe faces detection binding.
    """
    
    _aliases_   = ['mp_faces', 'mp_face']
    _about_     = 'Detects faces'
    _syntax_    = '[[frame=]{source frame}]'

    def __init__(self, field: str = 'cv2.frame'):
        super().__init__(field)
        self.field = Field(field)

    async def target(self, event, pipeline):
        mp_face_detection = mp.solutions.face_detection
        mp_drawing = mp.solutions.drawing_utils

        with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
            image = await self.field.read(event, pipeline)
            if image is not None:

                # Flip the image horizontally for a later selfie-view display, and convert
                # the BGR image to RGB.
                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                image.flags.writeable = False
                results = face_detection.process(image)

                # Draw the face detection annotations on the image.
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                if results.detections:
                    for detection in results.detections:
                        mp_drawing.draw_detection(image, detection)
                # cv2.imshow('MediaPipe Face Detection', image)
                # if cv2.waitKey(5) & 0xFF == 27:
                #     break
                yield await self.field.write(event, image)
