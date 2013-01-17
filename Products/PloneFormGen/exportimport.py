from csv import reader
from csv import writer
from ConfigParser import ConfigParser
from StringIO import StringIO

from zope.interface import implements

from Products.GenericSetup.interfaces import IFilesystemExporter
from Products.GenericSetup.interfaces import IFilesystemImporter
from Products.CMFCore.exportimport.content import StructureFolderWalkingAdapter

from Products.CMFCore.utils import getToolByName

from Products.Archetypes.utils import mapply
#
#   Filesystem export/import adapters
#
class FormFolderWalkingAdapter(StructureFolderWalkingAdapter):
    """
    """
    implements(IFilesystemExporter, IFilesystemImporter)

    def export(self, export_context, subdir, root=False):
        """ See IFilesystemExporter.
        """
        # Enumerate exportable children
        exportable = self.context.contentItems()
        exportable = [x + (IFilesystemExporter(x, None),) for x in exportable]
        exportable = [x for x in exportable if x[1] is not None]

        stream = StringIO()
        csv_writer = writer(stream)

        for object_id, object, ignored in exportable:
            csv_writer.writerow((object_id, object.getPortalTypeName()))

        if not root:
            subdir = '%s/%s' % (subdir, self.context.getId())

        export_context.writeDataFile('.objects',
                                     text=stream.getvalue(),
                                     content_type='text/comma-separated-values',
                                     subdir=subdir,
                                    )

        marshaller = self.context.Schema().getLayerImpl('marshall')
        ctype, length, got = marshaller.marshall(self.context)

        export_context.writeDataFile('.properties',
                                    text=got,
                                    content_type=ctype,
                                    subdir=subdir,
                                    )

        for id, object in self.context.objectItems():

            adapter = IFilesystemExporter(object, None)

            if adapter is not None:
                adapter.export(export_context, subdir)

    def _makeInstance(self, id, portal_type, subdir, import_context):
        context = self.context
        properties = import_context.readDataFile('.properties',
                                                 '%s/%s' % (subdir, id))
        tool = getToolByName(context, 'portal_types')

        try:
            tool.constructContent(portal_type, context, id)
        except ValueError: # invalid type
            return None

        content = context._getOb(id)

        if properties is not None:
            # Marshall the data
            marshaller = content.Schema().getLayerImpl('marshall')
            marshaller.demarshall(content, properties)

        return content


