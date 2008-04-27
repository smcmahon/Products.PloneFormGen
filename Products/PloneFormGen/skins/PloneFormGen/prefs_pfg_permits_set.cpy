## Script (Python) "prefs_pfg_permits_set"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Update pfg permissions
##

from Products.CMFCore.utils import getToolByName

fgt = getToolByName(context, 'formgen_tool')

fgt.setRolePermits(context.REQUEST)

state.setKwargs( {'portal_status_message':'Updated PloneFormGen Permissions'} )

return state
