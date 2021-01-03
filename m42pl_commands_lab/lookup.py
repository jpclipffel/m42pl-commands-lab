from m42pl.commands import StreamingCommand


class Lookup(StreamingCommand):
    __syntax__  = 'lookup <field, [...]> in <script>'
    __aliases__ = ['lookup', ]
    __grammar__ = dedent('''\
        start: /.+/
    ''')

    class Transformer(StreamingCommand.BaseTransformer):
        def start(self, items):
            return (), { 'pipeline': str(items[0]) }

    def __init__(self, pipeline: str):
        super().__init__()
        self.pipeline_id = pipeline

    async def target(self, event, pipeline):
        sub_pipeline = pipeline.context.pipelines[self.pipeline_id]
        sub_pipeline.set_chunk(self._chunk, self._chunks)
        async for e in sub_pipeline(event):
            yield e
