# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from zope.component import getUtility

from transmogrifier.blueprints import Blueprint
from transmogrifier.interfaces import ISection
from transmogrifier.interfaces import ISectionBlueprint
from transmogrifier.utils import get_lines


class Pipeline(Blueprint):

    def create_pipeline(self, sections, previous):
        pipeline = []
        for section_id in sections:
            if not section_id or section_id == self.name:
                continue

            blueprint_id = self.transmogrifier[section_id]['blueprint']
            blueprint = getUtility(ISectionBlueprint, blueprint_id)

            if not pipeline:
                pipeline = blueprint(self.transmogrifier, section_id,
                                     self.transmogrifier[section_id], previous)
            else:
                pipeline = blueprint(self.transmogrifier, section_id,
                                     self.transmogrifier[section_id], pipeline)

            if not ISection.providedBy(pipeline):
                raise ValueError('Blueprint %s for section %s did not return '
                                 'an ISection' % (blueprint_id, section_id))

        return iter(pipeline)

    def __iter__(self):
        assert not self.options.get('condition'), \
            'Support for conditional pipelines has been removed'

        sections = get_lines(self.options.get('pipeline'))
        if sections:
            previous = self.create_pipeline(sections, self.previous)
        else:
            previous = self.previous
        for item in previous:
            yield item
