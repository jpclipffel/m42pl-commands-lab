from textwrap import dedent

from m42pl.commands import MergingCommand
from m42pl.fields import Field


class MPLMerge(MergingCommand):
    _about_     = 'Force-merge a split pipeline'
    _syntax_    = '[pipeline]'
    _aliases_   = ['mpl_merge',]
    _grammar_   = MergingCommand._grammar_
    _grammar_['start'] = dedent('''\
        start   : piperef
    ''')

    class Transformer(MergingCommand.Transformer):
        def start(self, items):
            return (), {
                'pipeline': len(items) > 0 and items[0] or None
            }

    def __init__(self, pipeline: str = None):
        super().__init__(pipeline)
        self.piperef = Field(pipeline, default=None)
        self.pipeline = None
        self.target = self.target_echo
    
    async def setup(self, event, pipeline):
        try:
            self.pipeline = pipeline.context.pipelines[self.piperef]
            self.target = self.target_pipeline
        except KeyError:
            pass
        super().__init__(event, pipeline)

    async def target_pipeline(self, event, pipeline):
        async for e in self.pipeline(event, pipeline):
            yield e

    async def target_echo(self, event, pipeline):
        yield event
