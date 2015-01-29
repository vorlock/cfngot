# The MIT License (MIT)
#
# Copyright (c) 2015 vorlock
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from docopt import docopt


def cmd_options():
    """
    Parses USAGE doc string and converting it into comand line arguments and
    options with docopt
    """

    usage = """cfngot

Usage:
    cfngot cfn [--validate|--create|--update|--destroy] --config <file_name>
    cfngot json-diff <file1> <file2>
    cfngot (-v|--version)
    cfngot

Options:
    -v --version    Show version
  """
    return docopt(usage)


def main():
    # Initialize option pareser (docopt)
    opts = cmd_options()

    if opts['cfn']:
        from lib.cfn import CfnTemplateFactory
        cfn = CfnTemplateFactory(opts['<file_name>'])
        print(cfn.render_all())
    elif opts['json-diff']:
        from lib.cfn import CfnDiffFactory
    else:
        print(opts)


if __name__ == '__main__':
    main()
