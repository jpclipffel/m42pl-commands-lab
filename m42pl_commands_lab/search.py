from collections import OrderedDict
from textwrap import dedent
import regex
import asyncio

from m42pl.commands import StreamingCommand
from m42pl.utils.eval import Evaluator
from m42pl.errors import CommandError
from m42pl.pipeline import Pipeline, InfiniteRunner
from m42pl.event import derive

from .index import BaseIndex


class Search(StreamingCommand):
    """Searches one or more index(es) and filters the events.
    """

    _about_     = 'Search in one or more index(es)'
    _syntax_    = "(index=='<index name>' | <eval expression>) [...]"
    _aliases_   = ['search',]
    _schema_    = {
        'properties': {
            'index': {'type': 'string', 'description': 'Index name'}
        },
        'additionalProperties': True
    }

    _grammar_ = OrderedDict(StreamingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        start : /.+/
    ''')

    rex_indexes = regex.compile(
        r'index\s*==\s*(?P<index_name>[\'\"a-zA-Z0-9_-]+)'
    )

    class Transformer(StreamingCommand.Transformer):
        def start(self, items):
            indexes = []
            query = str(items[0])
            # Extract all indexes
            for match in Search.rex_indexes.finditer(query):
                group = match.groupdict()
                if group.get('index_name') is not None:
                    indexes.append(group['index_name'])
            # Cleanup indexes
            indexes = [i.strip('"').strip("'") for i in indexes]
            # ---
            return (), {'query': query, 'indexes': indexes}

    def __init__(self, query: str, indexes: list[str]):
        """
        :param pipelines:   Pipelines ID
        """
        super().__init__(query, indexes)
        self.query = query
        self.indexes = indexes
        self.expr = Evaluator(query)
        self.runners = {}

    async def setup(self, event, pipeline):
        for index in self.indexes:
            index_fqdn = BaseIndex().index_fqdn(index)
            index_dict = await pipeline.context.kvstore.read(index_fqdn)
            if index_dict is not None:
                # Add and setup index runner
                self.runners[index] = InfiniteRunner(
                    Pipeline.from_dict(index_dict),
                    pipeline.context,
                    derive(event, {'index': index})
                )
                await self.runners[index].setup()
            else:
                self.logger.warning(
                    f'Could not find the requested index: index="{index}"'
                )
        self.logger.info(
            f'Indexes loaded: count={len(self.runners)}, '
            f'indexes="{", ".join(self.runners.keys())}"'
        )

    async def target(self, event, pipeline):

        async def drain(runner, index):
            """Runs a pipeline 'runner' (...).
            """
            async for item in runner(derive(event, {'index': index})):
                await queue.put(item)
            await queue.put(None)

        queue = asyncio.Queue(1)
        tasks = [
            asyncio.create_task(drain(runner, index))
            for index, runner
            in self.runners.items()
        ]
        while not all(task.done() for task in tasks):
            _event = await queue.get()
            if _event and self.expr(_event['data']):
                yield _event
