import datetime

from m42pl.commands import StreamingCommand
from m42pl.fields import Field, FieldsMap
from m42pl.utils import time


class Bin(StreamingCommand):
    _about_     = ''
    _aliases_   = ['bin',]

    def __init__(self, field: str, span: str = None, bins: int = 0):
        super().__init__(field, span, bins)
        self.field = Field(field)
        self.span = span and Field(span) or None
        self.bins = bins and Field(bins) or None

    async def target_span(self, event, pipeline):
        print(self.span, type(self.span))
        done = time.reltime(
            self.span,
            datetime.datetime.fromtimestamp(await self.field.read(event, pipeline))
        )
        print(done)
        yield event

    async def target_bins(self, event, pipeline):
        yield event

    async def target_noop(self, event, pipeline):
        yield event

    async def setup(self, event, pipeline):
        if self.span:
            self.span = await self.span.read(event, pipeline)
            self.target = self.target_span
        # ---
        elif self.bins:
            self.bins = await self.bins.read(event, pipeline)
            self.target = self.target_bins
        # ---
        else:
            self.target = self.target_noop
