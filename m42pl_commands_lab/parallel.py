from collections import OrderedDict
from textwrap import dedent

import asyncio

from m42pl.commands import GeneratingCommand
from m42pl.pipeline import Pipeline
from m42pl.fields import Field


class Parallel(GeneratingCommand):
    """Runs multiple sub-pipeline in parallel using `asyncio`.

    This primitive implementation relies on this SO answers:
    stackoverflow.com/questions/55299564
    """

    _about_     = 'Run multiple sub-pipelines in parallel'
    _syntax_    = '<pipeline> [, ...]'
    _aliases_   = ['parallel', 'parallel_queue']
    _grammar_   = OrderedDict(GeneratingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        start : piperef (","? piperef)*
    ''')

    class Transformer(GeneratingCommand.Transformer):
        def start(self, items):
            return (), {'pipelines': items}

    def __init__(self, pipelines: list):
        """
        :param pipelines:   Pipelines ID
        """
        super().__init__(pipelines)
        self.pipelines = Field(pipelines)

    async def target(self, event, pipeline):

        async def drain(aiter):
            async for item in aiter(event):
                await queue.put(item)

        queue = asyncio.Queue(1)
        tasks = [
            asyncio.create_task(drain(piperef))
            for piperef
            in [
                pipeline.context.pipelines.get(p.name)
                for p
                in self.pipelines.name
            ]
        ]

        while not all(task.done() for task in tasks):
            yield await queue.get()
