"""
Jiggle Version.

Usage:
  jiggle_version --project=<project> --source=<source> [--debug=<debug>]
  jiggle_version -h | --help
  jiggle_version --version

Options:
  --project=<project>  Project name, e.g. my_lib in src/my_lib
  --source=<source>  Source folder. e.g. src/
  -h --help     Show this screen.
  --version     Show version.
  --debug=<debug>  Show diagnostic info [default: False].
"""

from docopt import docopt

from jiggle_version.jiggle_class import JiggleVersion


def go(project, source, debug): # type: (str, str, bool) ->None
    """
    Entry point
    :return:
    """
    jiggler = JiggleVersion(project, source, debug)
    jiggler.jiggle_source_code()
    jiggler.jiggle_config_file()

def process_docopts():
    arguments = docopt(__doc__, version='Jiggle Version 1.0')
    print(arguments)
    go(project=arguments["--project"], source=arguments["--source"], debug=arguments["--debug"])

if __name__ == '__main__':
    process_docopts()