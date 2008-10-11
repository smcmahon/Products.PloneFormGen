from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Acquisition import aq_inner 
from plone.memoize.instance import memoize
from plone.memoize.compress import xhtml_compress
import interfaces
from plone.app.content.browser.foldercontents import FolderContentsView
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface import implements


class folderEditView(FolderContentsView):

    """
       A view that gives a list of edit links rather than view for folders
    """
    implements(IFolderContentsView)

    _template = ViewPageTemplateFile('templates/folder_edit_contents.pt')

    def __call__(self):
        return xhtml_compress(self._template())

