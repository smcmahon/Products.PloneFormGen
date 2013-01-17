import unittest
try:
    from collective.funkload import testcase
    haveFunkload = True
except ImportError:
    haveFunkload = False
    print "collective.funkload is unavailable. Ignoring load tests."


if haveFunkload:
    class PFGLoadTest(testcase.FLTestCase):
        """Let's see how the saved data adapter performs under load..."""

        def setUp(self):
            self.logd("setUp")
            self.label = 'PFG load test'
            self.server_url = self.conf_get('main', 'url')

        def test_submitForm(self):
            self.get(self.server_url + '/testform',
                     description = 'Load form')

            self.post(
                self.server_url + '/testform',
                params = [
                    ['replyto', 'test@example.com'],
                    ['topic', 'test'],
                    ['comments', 'test'],
                    ['form.submitted', 1],
                    ],
                description = 'Submit form'
                )

        def tearDown(self):
            self.logd('tearDown')


def test_suite():
    if haveFunkload:
        return unittest.makeSuite(PFGLoadTest)
    return unittest.TestSuite()

additional_tests = test_suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
