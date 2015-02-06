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

from lib.helpers import *


class CfnTemplateFactory(object):
    """
    Wrapper creating cloudformation templates (in pure json) after running
    jinja2 on provided templates with j2 variables provided in yaml
    configguration file
    """
    def __init__(self, yaml_fname, jinja_temp=None):
        """
        @param string yaml_fname    Path to the yaml configuration file
        @param string jinja_temp    Path to the jinja2 templa if in single file
                                    rendering mode
        """
        self.jinja_temp = jinja_temp
        self.yaml_fname = yaml_fname

        try:
            with open(self.yaml_fname, 'r') as vars_file:
                self.config = yaml.load(vars_file)
        except (IOError, OSError) as e:
            raise Exception(e)

    def render_all(self):
        """
        Takes all jinja2 templaes renders them into pure json files and saves
        them into the same location as original j2 files
        """
        j2s = Helpers._find_all_files('*.json.j2')
        for file in j2s:
            template = Template(open(file).read())
            stack = template.render(self.config)
            s_name = file[:-3]
            with open(s_name, "w") as out_file:
                out_file.write(stack)
            # testing if 'stack' is a valid JSON
            try:
                json.loads(stack)
            except ValueError as e:
                raise Exception("Not a valid JSON: %s" % e)


class CfnDiffFactory(object):
    """
    Class for comparing cloudformastion templates downloaded from AWS and
    generated with CfnTemplateFactory class or any other way
    """
    def __init__(self, kwargs):
        self.f_name1 = kwargs['<file1>']
        self.f_name2 = kwargs['<file2>']

    def _load_file(self, fname):
        file_contents = ''
        with open(os.path.realpath(fname)) as file_name:
            loaded_template = json.load(file_name)
            sorted_template = self._walk_and_sort(loaded_template)
            file_contents = json.dumps(sorted_template, indent=4,
                                       sort_keys=True)

        # smash the output into a temporary file, so we can call vimdiff on it
        temp_file = tempfile.NamedTemporaryFile(delete=False,
                                                suffix=fname.replace('/', '_'))
        temp_file.write(file_contents.encode("UTF-8"))
        temp_file.close()

        return temp_file.name

    def _walk_and_sort(self, dictionary):
        if isinstance(dictionary, dict):
            for key, item in dictionary.items():
                if isinstance(item, dict):
                    self._walk_and_sort(item)
                elif isinstance(item, list):
                    dict_key = list(item[0].keys())[0]
                    sorted(item, key = lambda t: t[dict_key])

        return dictionary

    def diff(self):
        subprocess.call(['vimdiff', self._load_file(self.f_name1),
            self._load_file(self.f_name2)])


class CfnAwsCliOperations(object):
    """
    Wrapper around awscli tool
    """
    def __init__(self, kwargs):
        self.profile = kwargs['<profile_name>']
        self.cfn_templates = Helpers._find_all_files('*.json')
        self.yaml_fname = kwargs['<yaml_fname>']

        try:
            with open(self.yaml_fname, 'r') as vars_file:
                self.config = yaml.load(vars_file)
        except (IOError, OSError) as e:
            raise Exception(e)

        self.awscli_args = ['aws', '--region', self.config['cfn_region'],
                            '--profile', self.profile]
        self.template_url_part = 'https://s3.amazonaws.com/' + \
                                 self.config['cfn_bucket'] + '/'

    def _upload_templates(self):
        bucket_url = 's3://' + self.config['cfn_bucket'] + '/'
        for cfn_templ in self.cfn_templates:
            try:
                subprocess.call(self.awscli_args +
                                ['s3', 'cp', cfn_templ, bucket_url])
            except OSError as e:
                Exception(e)

    def validate(self):
        self._upload_templates()
        for f_name in Helpers._find_all_files('*.json'):
            template_url = self.template_url_part + os.path.basename(f_name)
            subprocess.call(self.awscli_args +
                            ['cloudformation', 'validate-template',
                             '--template-url', template_url])

    def action(self, action):
        self.validate()
        template_url = self.template_url_part + 'root.json'
        params_fname = self.config['cfn_environment'] + '.json'
        for root, dirs, files in os.walk('.'):
            if params_fname in files:
                params_file = os.path.join(root, params_fname)

        subprocess.call(self.awscli_args +
                        ['cloudformation', action,
                         '--template-url', template_url,
                         '--capabilities', 'CAPABILITY_IAM',
                         '--stack-name', self.config['cfn_environment'],
                         '--parameters', params_file])
