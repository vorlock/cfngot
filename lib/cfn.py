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

from jinja2 import Template
import yaml
import fnmatch
import os

import json
import subprocess
import tempfile


class CfnTemplateFactory(object):
    """
    Wrapper creating cloudformation templates (in pure json) after running
    jinja2 on provided templates with j2 variables provided in yaml
    configguration file
    """
    def __init__(self, yaml_fname, jinja_temp=None):
        self.jinja_temp = jinja_temp
        self.yaml_fname = yaml_fname

        with open(self.yaml_fname, 'r') as vars_file:
            self.config = yaml.load(vars_file)

    def j2_finder(self):
        matches = []
        for root, dirnames, filenames in os.walk('.'):
            for filename in fnmatch.filter(filenames, '*.json.j2'):
                matches.append(os.path.join(root, filename))
        return matches

    def render_all(self):
        j2s = self.j2_finder()
        for file in j2s:
            template = Template(open(file).read())
            stack = template.render(self.config)
            s_name = file[:-3]
            with open(s_name, "w") as out_file:
                out_file.write(stack)


class CfnDiffFactory(object):
    """
    Class for comparing cloudformastion templates downloaded from AWS and
    generated with CfnTemplateFactory class or any other way
    """
    def __init__(self, f_name1, f_name2):
        self.f_name1 = f_name1
        self.f_name2 = f_name2

    def _load_file(self):
        file_contents = ''
        with open(os.path.realpath(fname)) as file_name:
            loaded_template = json.load(file_name)
            sorted_template = self._walk_and_sort(loaded_template)
            file_contents = json.dumps(sorted_template, indent=4,
                                       sort_keys=True)

        # smash the output into a temporary file, so we can call vimdiff on it
        temp_file = tempfile.NamedTemporaryFile(delete=False,
                                                suffix=fname.replace('/', '_'))
        temp_file.write(file_contents)
        temp_file.close()

        return temp_file.name

    def _walk_and_sort(self, dictionary):
        if isinstance(dictionary, dict):
            for key, item in dictionary.iteritems():
                if isinstance(item, dict):
                    self._walk_and_sort(item)
                elif isinstance(item, list):
                    item.sort()

        return dictionary

    def diff(a, b, difftool):
        subprocess.Popen(['vimdiff', _load_file(a), _load_file(b)])
        print('You should periodically clear the /tmp/tmp* files from your \
               system to prevent interesting ASCII art :-)')
