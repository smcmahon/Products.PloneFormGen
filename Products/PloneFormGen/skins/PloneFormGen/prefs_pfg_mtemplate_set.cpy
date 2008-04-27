## Script (Python) "prefs_pfg_mtemplate_set"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Update pfg mtemplate
##

from Products.CMFCore.utils import getToolByName

request = context.REQUEST

fgt = getToolByName(context, 'formgen_tool')

body = request.form.get('body')
if body is not None:
	fgt.setDefault('mail_template', body)

body_type = request.form.get('body_type')
if body_type is not None:
	fgt.setDefault('mail_body_type', body_type)

state.setKwargs( {'portal_status_message':'Updated PloneFormGen Mail Template'} )

return state
