#
# Test PloneFormGen initialisation and set-up
#

from Products.PloneFormGen.tests import pfgtc

from Products.PloneFormGen.content import validationMessages
from Products.validation import validation


class TestCustomValidators(pfgtc.PloneFormGenTestCase):
    """ test our validators """

    def test_inExNumericRange(self):
        v = validation.validatorFor('inExNumericRange')
        self.failUnlessEqual(v(10, minval=1, maxval=20), 1)
        self.failUnlessEqual(v('10', minval=1, maxval=20), 1)
        self.failUnlessEqual(v('1', minval=1, maxval=20), 1)
        self.failUnlessEqual(v('20', minval=1, maxval=20), 1)
        self.failUnlessEqual(v('2.1', minval=1, maxval=20), 1)
        self.failUnlessEqual(v('2,1', minval=1, maxval=20), 1)
        self.failIfEqual(v(0, minval=1, maxval=5), 1)
        self.failIfEqual(v(6, minval=1, maxval=5), 1)
        self.failIfEqual(v(4, minval=5, maxval=3), 1)
        self.failIfEqual(v('2.1', minval=1, maxval=2), 1)
        self.failIfEqual(v('2,1', minval=1, maxval=2), 1)

    def test_isNotTooLong(self):
        v = validation.validatorFor('isNotTooLong')
        self.failUnlessEqual(v('', maxlength=20), 1)
        self.failUnlessEqual(v('1234567890', maxlength=20), 1)
        self.failUnlessEqual(v('1234567890', maxlength=10), 1)
        self.failUnlessEqual(v('1234567890', maxlength=0), 1)
        self.failIfEqual(v('1234567890', maxlength=9), 1)
        self.failIfEqual(v('1234567890', maxlength=1), 1)
        self.failUnlessEqual(v('cons\xc3\xa9quence', maxlength=11), 1)

    def test_isChecked(self):
        v = validation.validatorFor('isChecked')
        self.failUnlessEqual(v('1'), 1)
        self.failIfEqual(v('0'), 1)

    def test_isUnchecked(self):
        v = validation.validatorFor('isUnchecked')
        self.failUnlessEqual(v('0'), 1)
        self.failIfEqual(v('1'), 1)

    def test_isNotLinkSpam(self):
        v = validation.validatorFor('isNotLinkSpam')
        good = """I am link free and proud of it"""
        bad1 = """<a href="mylink">Bad.</a>"""
        bad2 = """http://bad.com"""
        bad3 = """www.Bad.com"""
        bad = (bad1,bad2,bad3)
        class Mock(object):
            validate_no_link_spam = 1
        mock = Mock()
        kw = {'field':mock}
        self.failUnlessEqual(v(good, **kw), 1)
        for b in bad:
            self.failIfEqual(v(b, **kw), 1,
                             '"%s" should be considered a link.' % b)


    def test_isNotTooLong2(self):
        v = validation.validatorFor('isNotTooLong')
        v.maxlength = 10
        self.failUnlessEqual(v('abc'), 1)
        self.failIfEqual(v('abcdefghijklmnopqrstuvwxyz'), 1)

        # there was a bug where widget.maxlength could possibly be defined as
        # '' which means calling int(widget.maxlength) would fail

        class Mock(object):
            pass
        field = Mock()
        field.widget = Mock()
        field.widget.maxlength = ''

        self.failUnlessEqual(v('abc', field=field), 1)

    def test_isEmail(self):
        v = validation.validatorFor('isEmail')
        self.failUnlessEqual(v('hi@there.com'), 1)
        self.failUnlessEqual(v('one@u.washington.edu'), 1)
        self.failIfEqual(v('@there.com'), 1)

    def test_isCommaSeparatedEmails(self):
        v = validation.validatorFor('pfgv_isCommaSeparatedEmails')
        self.failUnlessEqual(v('hi@there.com,another@two.com'), 1)
        self.failUnlessEqual(v('one@u.washington.edu,  two@u.washington.edu'), 1)
        self.failIfEqual(v('abc@plone.org; xyz@plone.org'), 1)


class TestCustomValidatorMessages(pfgtc.PloneFormGenTestCase):
    """ Test friendlier validation framework """

    def test_messageMassage(self):

        # s = "Validation failed(isUnixLikeName): something is not a valid identifier."
        # self.failUnlessEqual(validationMessages.cleanupMessage(s, self, self), u'pfg_isUnixLikeName')

        s = "Something is required, please correct."
        self.failUnlessEqual(validationMessages.cleanupMessage(s, self, self), u'pfg_isRequired')

        s = "Validation failed(isNotTooLong): 'something' is too long. Must be no longer than some characters."
        response = validationMessages.cleanupMessage(s, self, self)
        self.failUnlessEqual(response, u'pfg_too_long')


    def test_stringValidators(self):
        """ Test string validation
        """

        from Products.validation.exceptions import UnknowValidatorError
        from Products.validation import validation as v

        self.assertRaises(UnknowValidatorError, v.validate, 'noValidator', 'test')

        self.failIfEqual( v.validate('pfgv_isEmail', 'test'), 1 )

        self.failUnlessEqual( v.validate('pfgv_isEmail', 'test@test.com'), 1 )

        self.failUnlessEqual( v.validate('pfgv_isZipCode', '12345'), 1 )
        self.failUnlessEqual( v.validate('pfgv_isZipCode', '12345-1234'), 1 )
        # Canadian zip codes
        self.failUnlessEqual( v.validate('pfgv_isZipCode', 'T2X 1V4'), 1)
        self.failUnlessEqual( v.validate('pfgv_isZipCode', 'T2X1V4'), 1)
        self.failUnlessEqual( v.validate('pfgv_isZipCode', 't2x 1v4'), 1)
