import logging

def patch_portlet_error_handling():
    """
    Add 'Retry' to the exceptions that the portlet machinery doesn't
    catch for displaying a "broken portlet" message.
    """
    logger = logging.getLogger('PloneFormGen')
    logger.info('Patching plone.app.portlets ColumnPortletManagerRenderer to not catch Retry exceptions')
    
    import sys
    from Acquisition import aq_acquire
    from ZODB.POSException import ConflictError
    from ZPublisher.Publish import Retry

    from plone.app.portlets.manager import ColumnPortletManagerRenderer, logger

    def safe_render(self, portlet_renderer):
        try:
            return portlet_renderer.render()
        except (ConflictError, Retry):
            raise
        except Exception:
            logger.exception('Error while rendering %r' % (self,))
            aq_acquire(self, 'error_log').raising(sys.exc_info())
            return self.error_message()

    ColumnPortletManagerRenderer.safe_render = safe_render


def patch_publisher_exception_handling():
    # # The following code is taken verbatim from Plone 3's plone.app.linkintegrity.
    # We need it for its modification of Retry exception handling.
    logger = logging.getLogger('PloneFormGen')
    logger.info('Patching Zope publisher to support retries')

    from zope.component import queryMultiAdapter
    from Zope2.App.startup import zpublisher_exception_hook
    from ZPublisher.Publish import Retry

    def zpublisher_exception_hook_wrapper(published, REQUEST, t, v, traceback):
        """ wrapper around the zope2 zpublisher's error hook """
        try:
            # if we got a retry exception, we just propagate it instead of
            # trying to log it (like FiveException does)
            if t is Retry:
                v.reraise()
            # first we try to find a view/adapter for the current exception and
            # let the original function try to handle the exception if we can't
            # find one...
            view = queryMultiAdapter((v, REQUEST), name='index.html', default=None)
            if view is None:
                zpublisher_exception_hook(published, REQUEST, t, v, traceback)
            else:
                # otherwise render the view and raise the rendered string like
                # raise_standardErrorMessage does...
                view = view.__of__(published)
                message = view()
                if isinstance(message, unicode):
                    message = message.encode('utf-8')
                raise t, message, traceback
        finally:
            traceback = None


    from ZPublisher.Publish import get_module_info
    def proxy_get_module_info(*args, **kwargs):
        results = list(get_module_info(*args, **kwargs))
        if results[5] is zpublisher_exception_hook:
            results[5] = zpublisher_exception_hook_wrapper
        return tuple(results)


    def installExceptionHook():
        import ZPublisher.Publish
        ZPublisher.Publish.get_module_info = proxy_get_module_info


    def retry(self):
        """ re-initialize a response object to be used in a retry attempt """
        # this implementation changes the original one so that the response
        # instance is reused instead of replaced with a new one (after a Retry
        # exception was raised);  this fixes a bug in zopedoctests' http()
        # function (Testing/ZopeTestCase/zopedoctest/functional.py:113);
        # the doctest code assumes that the HTTPResponse instance passed to
        # publish_module() (line 177) is used to handle to complete request, so
        # it can be used to get the status, headers etc later on (lines 183-186);
        # normally this is okay, but raising a Retry will create a new response
        # instance, which will then hold that data (relevant for evaluating the
        # doctest) while the original (passed in) instance is still empty...
        #
        # so to fix this (quickly) retry() now cleans up and returns itself:
        self.__init__(stdout=self.stdout, stderr=self.stderr)
        return self

    from ZPublisher.HTTPResponse import HTTPResponse
    HTTPResponse.retry = retry

    installExceptionHook()


patch_portlet_error_handling()
