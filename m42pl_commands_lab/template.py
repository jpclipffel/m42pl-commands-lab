import os

from jinja2 import Template, Environment, FunctionLoader

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class Jinja(StreamingCommand):
    __about__   = 'Render a Jinja2 template.'
    __syntax__  = '{[src_field=]<source field>|[src_file=]<source file>} [[dest_field=]<destination field>[dest_file=]<destination file>]'
    __aliases__ = ['template', 'template_jinja', 'jinja']
    
    def __init__(self, src_field: str = None, dest_field: str = None,
                src_file: str = None, dest_file: str = None,
                searchpath: str = '.'):
        """
        :param src_field:           Source field.
        :param optional dest_field: Destination field.
                                    Defaults to `src_field` if neither `dest_field` not `dest_file` are set.
        :param optional src_file:   Source file.
        :param optional dest_file:  Destination file.
        :param optional searchpath: Templates default search path.
        """
        super().__init__(src_field, dest_field, src_file, dest_file, searchpath)
        # ---
        self.src_field  = Field(src_field)
        self.dest_field = Field(dest_field)
        self.src_file   = Field(src_file)
        self.dest_file  = Field(dest_file)
        self.searchpath = Field(searchpath, default=os.path.abspath(searchpath))

    async def setup(self, event, pipeline):
        # Solve fields
        self.src_field  = await self.src_field.read(event, pipeline)
        self.dest_field = await self.dest_field.read(event, pipeline)
        self.src_file   = await self.src_file.read(event, pipeline)
        self.dest_file  = await self.dest_file.read(event, pipeline)
        self.searchpath = await self.searchpath.read(event, pipeline)
        # Update fields value
        if self.dest_field is None and self.dest_file is None:
            self.dest_field = self.src_field
        # Setup renderer and  writer
        self.renderer = self.src_field and self.renderer_field or self.renderer_file
        self.writer = self.dest_field and self.writer_field or self.writer_file
        # Setup Jinja
        self.jinja_env = Environment(loader=FunctionLoader(self.load_template))
        self.current_file = None

    def load_template(self, name):
        """Custom templates loader used by the Jinja environment.
        
        This loader search included templates (templates referenced in
        'include' or 'block' directives) in the parrent directory of
        the currently processed file.
        """
        print(f'load_template --> {name}')
        current_path = self.current_file and os.path.dirname(self.current_file) or self.searchpath
        try:
            with open(os.path.join(current_path, name), 'r') as fd:
                return fd.read()
        except Exception:
            return None

    def renderer_field(self, event):
        # return Template(self.src_field.read(event.data)).render(**event.data)
        return self.jinja_env.from_string(self.src_field.read(event.data)).render(**event.data)
    
    def renderer_file(self, event):
        try:
            self.current_file = self.src_file.read(event.data)
            with open(self.current_file, 'r') as fd:
                # return Template(fd.read()).render(**event.data)
                return self.jinja_env.from_string(fd.read()).render(**event.data)
        except Exception as error:
            self._logger.error(f'failed to render template: {str(error)}')
            return ''
    
    def writer_field(self, event, rendered):
        self.dest_field.write(event.data, rendered)
        return event
    
    def writer_file(self, event, rendered):
        try:
            with open(self.dest_file.read(event.data), 'w') as fd:
                fd.write(rendered)
        except Exception as error:
            print(f'error 2 --> {error}')
            pass
        return event
    
    def target(self, event, pipeline):

        src_field  = await self.src_field.read(event, pipeline)
        dest_field = await self.dest_field.read(event, pipeline)
        src_file   = await self.src_file.read(event, pipeline)
        dest_file  = await self.dest_file.read(event, pipeline)
        searchpath = await self.searchpath.read(event, pipeline)

        try:
            self.writer(event, self.renderer(event))
        except Exception as error:
            print(f'error 3 --> {error}')
            pass
        return event
