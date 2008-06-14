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

import cgi

from Products.Archetypes.public import *
from Products.Archetypes.utils import shasattr

from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.configuration import zconf

from Products.CMFCore.permissions import View, ModifyPortalContent

from Products.CMFPlone.utils import safe_hasattr

from AccessControl import ClassSecurityInfo

from Products.PloneFormGen.content import fieldsBase

from Products.PloneFormGen.content.likertField import LikertField
from Products.PloneFormGen.config import PROJECTNAME

StringTypes = (type(''), type(u''))

class FormLikertField(fieldsBase.BaseFormField):
    """ A Likert form entry """

    security = ClassSecurityInfo()

    schema = fieldsBase.BaseFieldSchema.copy() + Schema((
        LinesField('likertAnswers',
            searchable=0,
            required=1,
            widget=LinesWidget(label='Answers',
                description = """List of possible answers for each of the questions""",
            ),
        ),
        LinesField('likertQuestions',
            searchable=0,
            required=1,
            widget=LinesWidget(label='Questions',
                description = """List of the questions""",
            ),
        ),
    ))

    finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

    portal_type = meta_type = "FormLikertField"
    archetype_name = "Likert Field"
    typeDescription = "A Likert Question Set"

    def __init__(self, oid, **kwargs):
        """ Initialize Class """

        fieldsBase.BaseFormField.__init__(self, oid, **kwargs)

        self.fgField = LikertField('fg_likert_field',
            searchable = 0,
            required = 0,
            write_permission = View,
            questionSet = ('Rate this field type',),
            answerSet = ('1', '2', '3', '4', '5'),
        )

    security.declareProtected(ModifyPortalContent, 'setLikertAnswers')
    def setLikertAnswers(self, value, **kwargs):
        if value in StringTypes:
            self.fgField.answerSet = tuple([a.strip() for a in value.split(',')])
        else:
            self.fgField.answerSet = tuple(value)

        self.likertAnswers = value

    security.declareProtected(ModifyPortalContent, 'setLikertQuestions')
    def setLikertQuestions(self, value, **kwargs):
        if value in StringTypes:
            self.fgField.questionSet = tuple([q.strip() for q in value.split(',')])
        else:
            self.fgField.questionSet = tuple(value)

        self.likertQuestions = value

    def htmlValue(self, REQUEST):
        """ return from REQUEST, this field's value, rendered as XHTML.
            In this case, a definition list.
        """

        value = REQUEST.form.get(self.__name__, 'No Input')
        if not safe_hasattr(value, '__getitem__'):
            return fieldsBase.BaseFormField.htmlValue(self, REQUEST)
        
        res = "<dl>\n"
        for i in range(len(value)):
            label = self.fgField.questionSet[i]
            response = value.get(str(i+1), '')
            res = "%s<dt>%s</dt><dd>%s</dd>\n" % (res, cgi.escape(label), cgi.escape(response))
        return "%s</dl>\n" % res


registerType(FormLikertField, PROJECTNAME)
