# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Widget import CalendarWidget
from Products.Archetypes import atapi
import logging


logger = logging.getLogger(__name__)


def null_upgrade_step(tool):
    """ This is a null upgrade, use it when nothing happens """
    pass

def upgrade_to_170(context):
    #apply the new dependency c.js.jqueryui
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile('profile-collective.js.jqueryui:default')

def upgrade_to_171(context):
    # just reload profile
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile('profile-Products.PloneFormGen:default')

def upgrade_to_190(context):
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type='FormDateField')
    for brain in brains:
        date_field = brain.getObject()
        widget = date_field.fgField.widget
        if isinstance(widget, CalendarWidget):
            logger.info('Migrating old CalendarWidget %s' % date_field.absolute_url_path())
            show_hm = widget.show_hm
            klass = atapi.DatetimeWidget if widget.show_hm else atapi.DateWidget
            date_field.fgField.widget = widget = klass()
            if show_hm:
                widget._properties['pattern_options']['time'] = widget.pattern_options['time'] = True
