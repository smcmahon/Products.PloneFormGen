"""
A form action adapter that saves form submissions as content in a folder.
"""

__author__ = 'Ross Patterson <me@rpatterson.net>'
__docformat__ = 'plaintext'

import copy
import logging

from zope import interface
from zope import component

from plone.i18n.normalizer import interfaces as norm_ifaces

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.CMFCore import WorkflowCore
from Products.CMFCore.utils import getToolByName

from archetypes.schemaextender import interfaces as extender_ifaces
from archetypes.schemaextender import extender
from Products.Archetypes import BaseObject
from Products.Archetypes import ClassGen
from Products.Archetypes import public
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import folder

from Products.PloneFormGen import config
from Products.PloneFormGen import PloneFormGenMessageFactory as _
from Products.PloneFormGen.content import saveDataAdapter

logger = logging.getLogger("PloneFormGen")


class IFormSubmission(interface.Interface):
    """
    A saved form submission whose schema is extended with the form schema.
    """


class FormSubmissionFolderAdapter(
        folder.ATFolder, saveDataAdapter.FormSaveDataAdapter):
    """
    A form action adapter that saves form submissions as content in a folder.
    """

    schema = folder.ATFolder.schema.copy(
    ) + public.Schema((
        saveDataAdapter.FormSaveDataAdapter.schema['showFields'].copy(),
        public.StringField(
            'titleField',
            vocabulary='allFieldDisplayList',
            default_method='getDefaultTitleField',
            required=0,
            searchable=0,
            widget=public.SelectionWidget(
                label=_(u'label_titlefield_text', default=u"Title Field"),
                description=_(
                    u'help_titlefield_text', default=u"""\
You may select a form field to be used as the submissions Plone title.  If left
empty, the title will be left blank."""))),
        public.StringField(
            'submissionType',
            required=0,
            searchable=0,
            default='Document',
            vocabulary='getFolderAddableTypes',
            widget=public.SelectionWidget(
                label=_(u'label_submissiontype_text',
                        default=u"Submission Type"),
                description=_(
                    u'help_submissiontype_text', default=u"""\
You may select another content type to create for form submissions.  Note that
the content type's schema will be overridden by the schema defined by the form,
so choosing a non-default content type will only work as much as the form
schema matches the content type's schema"""))),
        public.ReferenceField(
            'submissionFolder',
            relationship='submissionFolder',
            allowed_types_method='getFolderishTypes',
            default_method='getSubmissionFolderDefault',
            required=0,
            searchable=0,
            widget=public.ReferenceWidget(
                label=_(u'label_submissionfolder_text',
                        default=u"Submission Folder"),
                description=_(
                    u'help_submissionfolder_text', default=u"""\
You may select a folder in which submissions will be saved.  If left blank,
submissions will be saved inside this adapter."""))),
        public.LinesField(
            'submissionTransitions',
            vocabulary='getAvilableSubmissionTransitions',
            widget=public.PicklistWidget(
                label=_(u'label_submissiontransitions_text',
                        default='Submission Workflow Transitions'),
                description=_(u'help_submissiontransitions_text', default=u"""\
Select a sequence of workflow transitions to be applied on the newly created
submission object.  If the Submission Type workflow doesn't start out in a
private state, it is important to choose the right transitons to keep form
submissions from being publicly available."""))),
    ))

    meta_type      = 'FormSubmissionFolderAdapter'
    portal_type    = 'FormSubmissionFolderAdapter'
    archetype_name = 'Submission Folder Adapter'

    immediate_view = default_view = 'folder_listing'
    suppl_views    = ('folder_contents', )

    security       = ClassSecurityInfo()

    security.declarePrivate('onSuccess')
    def onSuccess(self, fields, REQUEST, loopstop=False):
        """
        Add a Form Submission object to the folder on success.

        Manually check if the user has permission.  If anonymous users have
        permissions to add submissions, then make sure the submission is owned
        by the adapter owner to prevent security issues such as various
        anonymous users accessing each others submissions.
        """
        folder = self.getSubmissionFolder()
        portal_type = self.getSubmissionType()
        types = getToolByName(self, 'portal_types')
        allowed = types[portal_type].isConstructionAllowed(folder)
        
        membership = getToolByName(self, 'portal_membership')
        user = getSecurityManager().getUser()
        owner = self.getWrappedOwner()
        is_anon = membership.isAnonymousUser()
        try:
            if not allowed or is_anon:
                newSecurityManager(REQUEST, owner)
            submission, changed = self.addSubmission(
                REQUEST, folder, portal_type)
        finally:
            if not allowed or is_anon:
                newSecurityManager(REQUEST, user)

        if not allowed and not is_anon:
            submission.changeOwnership(user, recursive=1)
            submission.manage_setLocalRoles(user.getId(), ('Owner', ))
        
        if 'controller_state' in REQUEST:
            # Record the submission object where the CMFFormController
            # machinery can get at it.
            REQUEST['controller_state'].kwargs.update(**changed)
            REQUEST['form_submission'] = '/'.join(submission.getPhysicalPath())

    def addSubmission(self, REQUEST, folder, portal_type):
        """
        Perform content operations as the appropriate user.
        """
        form = aq_parent(aq_inner(self))
        if folder is None:
            folder = self
        order = folder.getOrdering()
        if not hasattr(order, '__contains__'):
            order = folder.contentIds()

        title_field_name = self.getTitleField() or 'title'
        changed = {}
        if title_field_name in form:
            # Get the title from a form field in the submission
            title_field = form[title_field_name]
            title, kwargs = title_field.fgField.widget.process_form(
                title_field, title_field.fgField, REQUEST.form)
            changed[title_field_name] = title
        else:
            # Generate a title from the form title
            title = '{0} Submission'.format(form.Title())

        # Generate an id from the title, adding a suffix if existing
        id_ = str(norm_ifaces.IUserPreferredURLNormalizer(
            REQUEST).normalize(title))
        if id_ in order:
            # Exising objects have the id, find the next index suffix
            order_idx = len(folder) - 1
            base_id = id_
            idx = 0
            while id_ in order:
                while order_idx >= 0:
                    # Start at the end to try and find the highest index
                    order_id = order[order_idx]
                    if order_id.startswith(base_id + '-'):
                        idx = int(order_id[len(base_id + '-'):])
                        break
                    order_idx -= 1
                id_ = '{0}-{1}'.format(base_id, (idx + 1))

        new_id = folder.invokeFactory(portal_type, id_, title=title)
        submission = folder[new_id]
        submission.addReference(self, relationship='submissionFolderAdapter')

        # Mark the item as a form submission so the schema is extended with the
        # form schema
        interface.alsoProvides(submission, IFormSubmission)
        # Set the submission field values now that the extender applies
        extender.disableCache(REQUEST)
        schema = submission.Schema()
        for field in schema.fields():
            if field.__name__ in ('id', 'title'):
                # skip factory arguments
                continue
            result = field.widget.process_form(
                submission, field, REQUEST.form,
                empty_marker=BaseObject._marker,
                validating=False)
            if result is BaseObject._marker or result is None:
                continue
            changed[field.__name__] = result[0]
            if field.__name__ in ('id', 'title'):
                # already set in the factory
                continue
            field.set(submission, result[0], **result[1])

        # Apply workflow transitions
        workflow = getToolByName(submission, 'portal_workflow')
        for transition in self.getSubmissionTransitions():
            try:
                workflow.doActionFor(submission, transition)
            except WorkflowCore.WorkflowException:
                logger.exception(
                    'Workflow transition {0!r} failed on form submission: {1}'
                    .format(transition, self.absolute_url))

        submission.setLayout('base_view')

        return submission, changed
                
    security.declarePrivate('setDefaults')
    def getDefaultTitleField(self):
        """
        Use the first form field as the default title field.
        """
        form = aq_parent(aq_inner(self))
        return form.fgFields()[0].__name__

    security.declarePrivate('setDefaults')
    def getSubmissionFolderDefault(self):
        """
        Use the adapter itself as the default submission folder.
        """
        return self

    # TODO Currently there is a chicken and egg between finding out which types
    # can be added to the submission folder before we select the submission
    # folder and also which workflow transitions are available for the type.
    # In the future it would be nice to have AJAX support for updating the
    # other when one changes.

    security.declarePrivate('setDefaults')
    def getFolderishTypes(self, instance):
        """
        List all portal types that allow creating the submission type.
        """
        types = getToolByName(self, 'portal_types')
        return [self.getPortalTypeName()] + [
            typeinfo.getId() for typeinfo in types.objectValues()
            if typeinfo.global_allow and not typeinfo.filter_content_types]
    
    security.declarePrivate('setDefaults')
    def getFolderAddableTypes(self):
        """
        Return the allowed form submission types.
        """
        # TODO See above
        # return self.getSubmissionFolder().allowedContentTypes()

        types = getToolByName(self, 'portal_types')
        return [
            (typeinfo.getId(), typeinfo.title_or_id())
            for typeinfo in types.objectValues() if typeinfo.global_allow]

    security.declarePrivate('setDefaults')
    def getAvilableSubmissionTransitions(self):
        """
        List all the possible transitions for the submission type's workflow.
        """
        workflow = getToolByName(self, 'portal_workflow')

        workflows = set()
        workflows.update(*[
            workflow.getChainForPortalType(portal_type)
            for portal_type in self.Vocabulary('submissionType')[0].keys()])

        # TODO See above
        # workflows = workflow.getChainForPortalType(self.getSubmissionType())

        transitions = {}
        for workflow_id in workflows:
            workflow_obj = workflow[workflow_id]
            for state in workflow_obj.states.objectValues():
                for transition in workflow_obj.transitions.objectValues():
                    transitions[transition.getId()] = (
                        transition.actbox_name or transition.title_or_id())
        return transitions.items()
        

base.registerATCT(FormSubmissionFolderAdapter, config.PROJECTNAME)


class FormSubmissionModifier(object):
    """
    Extend form submissions with 
    """

    interface.implements(extender_ifaces.ISchemaModifier)
    component.adapts(IFormSubmission)

    modes = copy.deepcopy(ClassGen._modes)
    modes['m']['attr'] = 'editAccessor'

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        if not hasattr(self.context, 'aq_base'):
            # Some permissions checks invoke the schema on an unwrapped object
            return

        try:
            adapters = self.context.getReferences(
                relationship='submissionFolderAdapter')
        except AttributeError:
            # Don't extend the schema when the reference isn't available
            # Such as when doing CMFEditions stuff
            return
        if not adapters:
            logger.error(
                'Missing submission form reference, '
                'cannot look up form schema')
            return
        elif len(adapters) != 1:
            logger.error(
                'Other than one submission form reference, '
                'looking up the form schema from the first one: {0}'.format(
                    adapters))
        form = aq_parent(aq_inner(adapters[0]))
        title_field = adapters[0].Schema()[
            'titleField'].get(adapters[0]) or 'title'
        showFields = adapters[0].Schema()['showFields'].get(adapters[0])
        visible = set()
        for fg_field in form.fgFields():
            if showFields and fg_field.__name__ not in showFields:
                continue
            field = fg_field.copy()
            if field.__name__ == title_field:
                field.__name__ = 'title'
            else:
                visible.add(field.__name__)
            schema[field.__name__] = field

            # Generate accessor/mutator methods for use in views
            for mode in self.modes.itervalues():
                attr = 'get{0}{1}'.format(
                    mode['attr'][0].capitalize(), mode['attr'][1:])
                method = getattr(field, attr)(self.context)
                if method:
                    continue

                def fieldMethod(instance, field=field, mode=mode, **kw):
                    """
                    Generate an AT field method.
                    """
                    if mode['attr'] == 'mutator':
                        def instanceMethod(
                                value, field=field, instance=instance,
                                mode=mode, **kw):
                            """
                            Work with an AT field value.
                            """
                            field_method = getattr(field, mode['prefix'])
                            return field_method(instance, value, **kw)
                    else:
                        def instanceMethod(
                                field=field, instance=instance, mode=mode,
                                **kw):
                            """
                            Work with an AT field value.
                            """
                            field_method = getattr(field, mode['prefix'])
                            return field_method(instance, **kw)
    
                    return instanceMethod
                setattr(field, attr, fieldMethod)

        for field in schema.filterFields(isMetadata=0):
            if field.__name__ in visible:
                continue
            if not isinstance(field.widget.visible, dict):
                field.widget.visible = dict()
            field.widget.visible['view'] = 'invisible'
