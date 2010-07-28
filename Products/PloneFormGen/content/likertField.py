__author__ = """Titus Anderson <titus.anderson@louisville.edu>"""
__docformat__ = 'plaintext'

# Copyright (c) 2007 by Copyright (c) 2007 Titus Anderson
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

from Products.Archetypes.public import *
from Products.Archetypes.utils import shasattr

from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.configuration import zconf

from Products.Archetypes.Field import ObjectField

from Products.Archetypes.Registry import registerField
from Products.PloneFormGen.widgets import LikertWidget

from Products.PloneFormGen import PloneFormGenMessageFactory as _

from AccessControl import ClassSecurityInfo


class LikertField(ObjectField):
    __implements__ = (getattr(ObjectField, '__implements__', ()),)

    _properties = ObjectField._properties.copy()
    _properties.update({
        'type' : 'likert',
        'widget' : LikertWidget(),
        'answerSet' : (),
        'questionSet' : (),
    })

    security = ClassSecurityInfo()

    security.declarePublic('get')
    def get(self, instance, **kwargs):
        """ Return LikertField Data
            Result is a tuple of responses
        """

        value = ObjectField.get(self, instance, **kwargs)
        if not value:
            return tuple()
        else:
            return value

    security.declarePublic('set')
    def set(self, instance, value, **kwargs):
        """ Set the LikertField data """

        if type(value) in (str, unicode):
            value = [v.strip() for v in value.split(',')]
        ObjectField.set(self, instance, value, **kwargs)

    security.declarePublic('getQuestionSet')
    def getQuestionSet(self):
        return self.questionSet

    security.declarePublic('getAnswerSet')
    def getAnswerSet(self):
        return self.answerSet

    def validate_required(self, instance, value, errors):
        for index in range(self.questionSet):
            if not value[index]:
                label = self.widget.Label(instance)
                name = self.getName()
                error = 'Answers to all questions of %s are required, please correct' % label
                errors[name] = error
                return error
        return None

    def validate(self, value, instance, errors=None, **kwargs):
        error = _(u'pfg_allRequired', u'An answer is required for each question.')
        if not self.required:
            return None
        for index in range(len(self.questionSet)):
            if (index > len(value)) or not value[index]:
                fname = self.getName()
                if fname not in errors:
                    errors[fname] = error
                return error
        return None

registerField(LikertField,
              title='Likert Field',
              description='Used for collecting Likert survey answers'
)
