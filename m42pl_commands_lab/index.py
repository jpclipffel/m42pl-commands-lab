from m42pl.fields import Field
from m42pl_commands.macro import *


class BaseIndex(BaseMacro):
    kvstore_prefix = 'indexes:'
    macros_index = f'{kvstore_prefix}current'

    # index_fqdn = BaseMacro.macro_fqdn

    def index_fqdn(self, name: str) -> str:
        """Returns a full macro name, i.e. with correct prefix.

        :param name:    Macro name as defined by user
        """
        return f'{self.kvstore_prefix}{name}'


class RecordIndex(RecordMacro, BaseIndex):
    _aliases_   = ['_recordindex',]


class RunIndex(RunMacro, BaseIndex):
    _aliases_   = ['_runindex',]


class GetIndexes(GetMacros, BaseIndex):
    _aliases_   = ['indexes',]
    key_name    = 'index'


class DelIndex(DelMacro, BaseIndex):
    _aliases_   = ['delindex',]


class PurgeIndexes(PurgeMacros, BaseIndex):
    _aliases_   = ['purgeindex', 'purgeindexes']


class Index(Macro):
    """Record or run an index.
    
    This command returns an instance of :class:`RecordIndex`,
    :class:`RunIndex` or :class:`GetIndexes` depending on what
    parameters are given.
    """
    _about_     = 'Record an index, search an index or return indexes list'
    _syntax_    = '[<name> [pipeline]]'
    _aliases_   = ['index',]

    def __new__(self, *args, **kwargs):
        if len(args) > 1 or len(kwargs) > 1 or 'pipeline' in kwargs:
            return RecordIndex(*args, **kwargs)
        elif len(args) == 1 or len(kwargs) == 1:
            return RunIndex(*args, **kwargs)
        else:
            return GetIndexes()
