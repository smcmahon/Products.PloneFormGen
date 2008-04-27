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

recipient_email = request.form.get('recipient_email')
if recipient_email is not None:
	fgt.setDefault('mail_recipient_email', recipient_email)

recipient_name = request.form.get('recipient_name')
if recipient_email is not None:
	fgt.setDefault('mail_recipient_name', recipient_name)

cc_recipients = request.form.get('cc_recipients')
if cc_recipients is not None:
	fgt.setDefault('mail_cc_recipients', cc_recipients.split('\n'))

bcc_recipients = request.form.get('bcc_recipients')
if bcc_recipients is not None:
	fgt.setDefault('mail_bcc_recipients', bcc_recipients.split('\n'))

state.setKwargs( {'portal_status_message':'Updated PloneFormGen Addressing Defaults'} )

return state
