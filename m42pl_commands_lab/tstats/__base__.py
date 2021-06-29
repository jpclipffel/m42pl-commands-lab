from m42pl.commands import GeneratingCommand


translates = {
    'mongo': {
        'count': 
    }
}




class TStats(GeneratingCommand):
    _about_     = 'Runs aggregation searches on remote sources'
    _syntax_    = '<function> [as <field>], ... by <field>, ... from <index>'
    _aliases_   = ['tstats',]

    def __init__(self, functions: list, fields: list, index: str):
        pass
