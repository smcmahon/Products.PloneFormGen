from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget
from AccessControl import ClassSecurityInfo


class CaptchaWidget(TypesWidget):
    """ Archetypes widget wrapping collective.captcha or collective.recaptcha
    """

    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro' : 'widget_captcha',
        'size' : '30',
        'maxlength' : '255',
        'blurrable' : True,
        'postback' : False,
        })

    security = ClassSecurityInfo()

# Register the widget with Archetypes
registerWidget(CaptchaWidget,
               title = 'Captcha widget',
               description= ('Renders a captcha image and a text input box.',),
               used_for = ('Products.Archetypes.Field.StringField',)
               )
