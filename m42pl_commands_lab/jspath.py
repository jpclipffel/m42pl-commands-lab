from textwrap import dedent
import jsonpath_ng

from m42pl.commands import StreamingCommand
from m42pl.field import Field


class JSPath(StreamingCommand):
    __about__   = 'Evaluate JsonPath expressions and assign results to fields'
    __syntax__  = '<field name> = <expression> [, ...]'
    __aliases__ = ['jspath', 'jsonpath', ]
    __grammar__ = dedent('''\
        string          : STRING
        field_name      : NAME | STRING | DOTPATH
        jspath_field    : field_name "=" string
        jspath_fields   : (jspath_field ","?)+
        start           : jspath_fields
    ''')

    class Transformer(StreamingCommand.BaseTransformer):
        string          = lambda self, items: str(items[0][1:-1])
        field_name      = lambda self, items: str(items[0])
        jspath_field    = lambda self, items: (items[0], items[1])
        jspath_fields   = lambda self, items: dict(items)
        start           = lambda self, items: ((), { 'fields': items[0] })

    def __init__(self, fields: dict):
        super().__init__(fields)
        self.fields = dict([ (Field(field), jsonpath_ng.parse(expr)) for field, expr in fields.items() ])

    def target(self, event, pipeline):
        for field, expr in self.fields.items():
            matches = expr.find(event.data)
            field.write(event.data, len(matches) == 1 and matches[0].value or [m.value for m in matches] )
        return event
