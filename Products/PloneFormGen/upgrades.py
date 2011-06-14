from Products.CMFCore.utils import getToolByName

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
