from docopt import docopt

def command_create_time(argv):
    """climesync.py create-time

    Usage: create-time [-h] --duration=<duration> 
                            --project=<project slug>
                            --activities="<activity slugs>"

                           [--date-worked=<date worked>
                            --issue-uri=<issue uri>
                            --notes=<notes>]
    """
    print argv
    args = docopt(command_create_time.__doc__, argv=argv)
    print args
