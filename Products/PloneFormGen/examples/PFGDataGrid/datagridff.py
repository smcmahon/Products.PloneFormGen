"""DataGridFF -- a PloneFormGen form field built on DataGridField"""

__author__  = 'Steve McMahon <steve@dcn.org>'
__docformat__ = 'plaintext'

import cgi

from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import View, ModifyPortalContent

from Products.Archetypes.public import *

from Products.ATContentTypes.content.base import ATCTContent, ATContentTypeSchema
from Products.ATContentTypes.content.folder import finalizeATCTSchema

from Products.PFGDataGrid.config import *

from Products.PloneFormGen.content import fieldsBase

from Products.DataGridField import \
    DataGridField, DataGridWidget, Column


class FormDataGridField(fieldsBase.BaseFormField):
    """
        A PloneFormGen Form Field
    """

    security  = ClassSecurityInfo()


    #######################
    # We could derive our schema from several schema defined in
    # fieldsBase. In general, choose by which has a matching data
    # type for the default field value.
    #
    # DataGridField won't match any, so we'll use the BaseFieldSchema,
    # which has no default, and provide a getFgDefault method to make
    # up for it.

    schema = fieldsBase.BaseFieldSchema.copy() + Schema((

        # We'll make DataGridField eat its own dog food by using it
        # to get our column definitions and defaults.
        DataGridField('columnDefs',
            searchable = False,
            required = True,
            columns=('columnId','columnTitle','columnDefault'),                
            default = [ {'columnId':'column1', 'columnTitle':'Column One', 'columnDefault':''}, ],
            widget = DataGridWidget(
                label = 'Column Definitions',
                i18n_domain = "pfgdatagrid",
                label_msgid = "label_column_defs_text",
                description = """
                    Specify a unique identifier and a title for each column
                    you wish to appear in the datagrid. The default value
                    is optional.
                """,
                description_msgid = "help_column_defs_text",
                columns={
                    'columnId':Column('Column Id'),
                    'columnTitle':Column('Column Title'),
                    'columnDefault':Column('Default Value'),
                },
            ),
        ),
        # A few DFG-specific fields. We'll need to provide
        # mutator and accessor methods that tie these
        # to values in the widget
        BooleanField('allowDelete',
            searchable = False,
            default = '1',
            widget = BooleanWidget(
                label = 'Allow Row Deletion',
                i18n_domain = "pfgdatagrid",
                label_msgid = "label_allow_delete_text",
            ),
        ),
        BooleanField('allowInsert',
            searchable = False,
            default = '1',
            widget = BooleanWidget(
                label = 'Allow Row Insertion',
                i18n_domain = "pfgdatagrid",
                label_msgid = "label_allow_insert_text",
            ),
        ),
        BooleanField('allowReorder',
            searchable = False,
            default = '1',
            widget = BooleanWidget(
                label = 'Allow Row Reordering',
                i18n_domain = "pfgdatagrid",
                label_msgid = "label_allow_reorder_text",
            ),
        ),

    ))
    finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

    content_icon   = 'BasicField.gif'

    meta_type      = \
    portal_type    = 'FormDataGridField'
    archetype_name = 'DataGrid Field'

    typeDescription= 'A flexible datagrid field.'
    typeDescMsgId  = 'datagridformfield_description'


    #######################
    # Every form field must have an fgField attribute that is a field
    # definition created outside of the normal schema.
    # Since this needs to be an instance attribute, we'll set it up
    # in the __init__ method.
    
    def __init__(self, oid, **kwargs):
        """ initialize class """

        fieldsBase.BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = DataGridField('fg_datagrid_field',
            searchable=False,
            required=False,
            write_permission = View,
            widget = DataGridWidget(),
            columns=('column1','column2','The third'),                
            allow_delete = True,
            allow_insert = True,
            allow_reorder = True,
            )



    #######################
    # Mutators and accessors that tie items in the form field's
    # schema to attributes of the fgField field.
    # Most are simple.
    # setColumnDefs is more complex because it's translating the
    # data from the columnDefs DataGrid for multiple uses.


    security.declareProtected(ModifyPortalContent, 'setColumnDefs')
    def setColumnDefs(self, value, **kwa):
        """ mutator for columnDefs """

        myval = [col for col in value if col.get('columnId')]        
        self.columnDefs = myval
        self.fgField.columns = [col['columnId'] for col in myval]
        
        res = {}
        for col in myval:
            res[ col['columnId'] ] = Column( col['columnTitle'], default=col['columnDefault'] )
        self.fgField.widget.columns = res
        

    security.declareProtected(ModifyPortalContent, 'setAllowDelete')
    def setAllowDelete(self, value, **kwa):
        """ set allow_delete flag for field """

        # Note: booleans come in the request as '0' or '1';
        # we need to translate them into True or False.
        self.fgField.allow_delete = value == '1'


    security.declareProtected(View, 'getAllowDelete')
    def getAllowDelete(self, **kw):
        """ get allow_delete flag for field """

        return self.fgField.allow_delete


    security.declareProtected(ModifyPortalContent, 'setAllowInsert')
    def setAllowInsert(self, value, **kwa):
        """ set allow_insert flag for field """

        self.fgField.allow_insert = value == '1'


    security.declareProtected(View, 'getAllowInsert')
    def getAllowInsert(self, **kw):
        """ get allow_insert flag for field """

        return self.fgField.allow_insert


    security.declareProtected(ModifyPortalContent, 'setAllowReorder')
    def setAllowReorder(self, value, **kwa):
        """ set allow_reorder flag for field """

        self.fgField.allow_reorder = value == '1'


    security.declareProtected(View, 'getAllowReorder')
    def getAllowReorder(self, **kw):
        """ get allow_reorder flag for field """

        return self.fgField.allow_reorder


    #######################
    # Due to the very-specific nature of the DataGridField
    # default, we're going to provide it via an accessor method.
    # If the data structure was common, we could have done it in
    # the form field schema with an fgDefault field.

    def getFgDefault(self, **kwargs):
        """
         supply defaults for fgField datagrid as a list
         with a single dictionary 
        """

        res = {}
        for col in self.columnDefs:
            if col.get('columnId'):
                res[col['columnId']] = col['columnDefault']
        return [res]
    

    #######################
    # The string representation of the DataGridField value isn't suitable
    # for public consumption. So, let's massage it by overriding
    # the htmlValue method

    def htmlValue(self, REQUEST):
        """ return from REQUEST, this field's value in html.
        """

        # get column titles
        titles = {}
        for col in self.columnDefs:
            titles[col['columnId']] = col['columnTitle']

        value = REQUEST.form.get(self.__name__, 'No Input')
        
        res = "<dl>"
        for adict in value:
            if adict.get('orderindex_', '') != 'template_row_marker':
                for akey in adict.keys():
                    if akey != 'orderindex_':
                        res = "%s\n<dt>%s</dt>\n<dd>%s<dd>" % \
                         (res, cgi.escape(titles[akey]), cgi.escape(adict[akey]))
        return "%s</dl>" % res
    

    
registerType(FormDataGridField, PROJECTNAME)

