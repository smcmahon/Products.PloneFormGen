"""validationMessages -- cleanup Archetypes/validation messages"""

__author__ = 'Steve McMahon <steve@dcn.org>'
__docformat__ = 'plaintext'

# Messages taken from godchap's gotcha-validation-i18n branch of
# archetypes validation

from Products.CMFCore.utils import getToolByName

import re
from types import StringTypes

verrorRE = re.compile(r".+fails tests of ([^.]+)")
verror2RE = re.compile(r"Validation failed\((.+?)\):.+")
enrMessageRE = re.compile("Validation failed\(inExNumericRange\): could not convert '(.+)' to number")
enrSmallMessageRE = re.compile("Validation failed\(inExNumericRange\): '(.+?)' is too small. Must be at least (.+).")
enrLargeMessageRE = re.compile("Validation failed\(inExNumericRange\): '(.+?)' is too large. Must be no greater than (.+).")
mlTooLongRE = re.compile("Validation failed\(isNotTooLong\): '.+?' is too long. Must be no longer than (.+) characters.")


from Products.PloneFormGen import PloneFormGenMessageFactory as _

# The commented out messages are now part of the general purpose RE validator.
# See config.py for initial values.
newMessages = {
    'isDecimal': _(u'pfg_isDecimal', u'This field requires a decimal value.'),
    'isInt': _(u'pfg_isInt', u'This field requires an integer value.'),
    'isPrintable': _(u'pfg_isPrintable', u'This value contains unprintable characters.'),
    'isSSN': _(u'pfg_isSSN', u'This is not a well formed SSN.'),
    # 'isUSPhoneNumber': _(u'pfg_isUSPhoneNumber', u'This is not a valid us phone number.'),
    # 'isInternationalPhoneNumber': _(u'pfg_isInternationalPhoneNumber', u'This is not a valid international phone number.'),
    # 'isZipCode': _(u'pfg_isZipCode', u'This is not a valid zip code.'),
    # 'isURL': _(u'pfg_isURL', u'This is not a valid url.'),
    # 'isEmail': _(u'pfg_isEmail', u'This is not a valid email address.'),
    'isMailto': _(u'pfg_isMailto', u'This is not a valid mailto: url.'),
    'isUnixLikeName': _(u'pfg_isUnixLikeName', u'This name is not a valid identifier.'),
    'isChecked': _(u'pfg_isChecked', u'This box must be checked.'),
    'isUnchecked': _(u'pfg_isUnchecked', u'This box must be unchecked.'),
    'isValidDate': _(u'pfg_isValidDate', u'The date entered was invalid.'),
    'isNotLinkSpam': _(u'pfg_isnotlinkspam', u'This text appears to contain links.'),
    }

newRequiredMessage = _(u'pfg_isRequired', u'This field is required.')


def cleanupMessage(original, context, instance):
    """ Where original is the message from the Archetypes validator,
        return an improved, translatable message if available.
    """

    if type(original) in StringTypes:
        if original.find('is required, please correct.') > 0:
            return newRequiredMessage

        mo = verrorRE.match(original)
        if mo:
            term = mo.groups()[0]
            if term.find('pfgv_') == 0:
                # this is one of the customizable pfg tool validators
                fgt = getToolByName(instance, 'formgen_tool')
                sv = fgt.stringValidators.get(term[5:])
                if sv:
                    # this is already a messagestr
                    return sv['errmsg']

        mo = verror2RE.match(original)
        if mo:
            term = mo.groups()[0]

            nm = newMessages.get(term)
            if nm:
                # this is one of the simple messages for which we have a replacement
                return nm

            if term == 'inExNumericRange':
                mo = enrMessageRE.match(original)
                if mo:
                    return _(u'pfg_not_number', u'Please enter a number here.')
                mo = enrSmallMessageRE.match(original)
                if mo:
                    groups = mo.groups()
                    return _(u'pfg_number_too_small',
                             u"'${value}' is too small. Must be at least ${min}.",
                             mapping={'value': groups[0], 'min': groups[1]})
                mo = enrLargeMessageRE.match(original)
                if mo:
                    groups = mo.groups()
                    return _(u'pfg_number_too_large',
                             u"'${value}' is too large. Must be no greater than ${max}.",
                             mapping={'value': groups[0], 'max': groups[1]})
            elif term == 'isNotTooLong':
                mo = mlTooLongRE.match(original)
                if mo:
                    groups = mo.groups()
                    return _(u'pfg_too_long',
                             u"'Entry too long. It should be no more than ${max} characters.",
                             mapping={'max': groups[0]})

    return original
