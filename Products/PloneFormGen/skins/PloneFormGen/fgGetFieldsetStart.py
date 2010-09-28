## Script (Python) "fgGetFieldsetStart"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=field, widget, edit=True
##title=
##
if edit:
    html = '<fieldset class="PFGFieldsetWidget" id="pfg-fieldsetname-%s>"'
    html = html % field.getName()
    if widget.show_legend:
        html = html + '<legend><span>%s</span></legend>'
        html = html % widget.Label(context)
else:
    html = '<fieldset>'
return html

