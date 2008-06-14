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

from Products.Archetypes.Widget import TypesWidget

from Products.Archetypes.Registry import registerWidget

from Products.CMFCore.permissions import View, ModifyPortalContent

from AccessControl import ClassSecurityInfo

class LikertWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro' : 'widget_likert'
    })

    def process_form(self, instance, field, form, empty_marker=None, emptyReturnsMarker=False):

        fieldName = field.getName()
        questions = field.getQuestionSet()

        answers = []

        frec = form.get(fieldName, {})
        for index in range(len(questions)):
            value = frec.get(str(index + 1), empty_marker)
            answers.append(value)

        return answers, {}
        
registerWidget(LikertWidget,
               title='Likert Widget',
               description='Renders a Likert question and answer box',
               used_for=('Products.PloneFormGen.content.likertField.LikertField',),
)
