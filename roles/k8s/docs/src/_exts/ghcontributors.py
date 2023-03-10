#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Copyright kubeinit contributors.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

MIT License

Copyright (c) 2018 David Garcia
Original from: https://github.com/dgarcia360/sphinx-contributors
"""

from docutils import nodes
from docutils.parsers.rst import Directive, directives

import requests


class Contributor:
    """Main class for the contributors atributes."""

    def __init__(self, login, url, contributions=0):
        """Initialize atributes."""
        self.contributions = contributions
        self.login = login
        self.url = url
        self.contributions = contributions

    def build(self):
        """Build contributor details."""
        node_contributor = nodes.paragraph()
        node_contributor += nodes.reference(text=self.login, refuri=self.url)
        node_contributor += nodes.Text(' - ' + str(self.contributions) + ' ' +
                                       ('contributions' if self.contributions != 1 else 'contribution'))
        return node_contributor


class ContributorsRepository:
    """Main class for repo atributes."""

    def __init__(self, contributors, reverse=True, limit=10, exclude=None):
        """Initialize repo details."""
        self.contributors = sorted([c for c in contributors if c.login not in exclude],
                                   key=lambda c: c.contributions,
                                   reverse=reverse)[:limit]

    def build(self):
        """Build contributors repo details."""
        node_list = nodes.bullet_list()
        for contributor in self.contributors:
            node_contributor = nodes.list_item()
            node_contributor += contributor.build()
            node_list += node_contributor
        return node_list


class ContributorsDirective(Directive):
    """Main class for the contributors directive."""

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'limit': directives.positive_int,
        'order': directives.unchanged,
        'exclude': directives.unchanged,
    }

    def run(self):
        """Run the plugin."""
        limit = self.options.get('limit', 10)
        order = self.options.get('order', 'DESC') == 'DESC'
        exclude = self.options.get('exclude', '').split(",")

        r = requests.get('https://api.github.com/repos/' + self.arguments[0] + '/contributors?per_page=100')
        if type(r.json()) == dict:
            raise ValueError('The repository ' + self.arguments[0] + ' does not exist.')
        contributors = list(map(lambda c: Contributor(c.get('login'),
                                                      c.get('html_url'),
                                                      c.get('contributions')), r.json()))
        return [ContributorsRepository(contributors, reverse=order, limit=limit, exclude=exclude).build()]


def setup(app):
    """Configure the plugin."""
    app.add_directive('ghcontributors', ContributorsDirective)

    return {'version': '0.1'}
