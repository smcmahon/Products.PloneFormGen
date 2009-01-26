## Script (Python) "prefs_pfg_savedata_set"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Update pfg savedata
##

from Products.CMFCore.utils import getToolByName

request = context.REQUEST

fgt = getToolByName(context, 'formgen_tool')

delimiter = request.form.get('csv_delimiter')
if delimiter is not None:
    fgt.setDefault('csv_delimiter', delimiter)

state.setKwargs( {'portal_status_message':'Updated PloneFormGen Save Data Defaults'} )

return state
