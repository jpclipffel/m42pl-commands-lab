from m42pl.commands import StreamingCommand


class Tester(StreamingCommand):
    __aliases__ = ['test', ]

    def _target(object self, object event, object pipeline):
        print(f'Tester.target() !')
        print(event.data)

    async def target(self, event, pipeline):
        self._target(event, pipeline)
        yield event
