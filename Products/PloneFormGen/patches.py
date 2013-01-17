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


patch_portlet_error_handling()
