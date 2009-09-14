import string
from Acquisition import aq_inner, aq_chain
from zope import component, interface

from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView

from Products.PloneFormGen.interfaces import IPloneFormGenField, IPloneFormGenFieldset,\
                            IPloneFormGenActionAdapter, IPloneFormGenThanksPage
from Products.PloneFormGen.browser.formbuild.interfaces import IPFGFormBuildView

class PFGFormBuildView(BrowserView):
    """A custom edit form for pfg form that support ajaxtified form build
    """
    interface.implements(IPFGFormBuildView)
    template = ViewPageTemplateFile('formbuild_view.pt')

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    @property
    @memoize
    def fgfields(self):
        filters = {"object_provides": {"query":[IPloneFormGenField.__identifier__, IPloneFormGenFieldset.__identifier__], "operator": "or"}}
        return [b.getObject() for b in self.context.getFolderContents(filters)]

    @property
    @memoize
    def fgfield_renderers(self):
        return [field.restrictedTraverse('fieldrenderer') 
                for field in self.fgfields]

    @memoize
    def helperjs(self):
        """Return list of helper js-es those are needed to render the field
        """
        result = set()
        for fieldrenderer in self.fgfield_renderers:
            result.update(fieldrenderer.helperjs())
        return result

    @memoize
    def helpercss(self):
        """Return list of helper css-es those are needed to render the field
        """
        result = set()
        for fieldrenderer in self.fgfield_renderers:
            result.update(fieldrenderer.helpercss())
        return result

    def __call__(self):
        return self.template()

    def jsapp(self):
        """Initialize js to start the formbuild
        """
        ptt = getToolByName(self.context, 'portal_types')
        att = getToolByName(self.context, 'archetype_tool')
        metatypes = [ct.content_meta_type for ct in ptt.listTypeInfo()]
        installed_types = [ttype for ttype in att.listTypes() if ttype.meta_type in metatypes]

        field_layout = string.Template("jq(\"#addableItem-$typeid\").addClass(\"addableItem-$fgtype\");")
        fields = [ttype.meta_type for ttype in installed_types
                  if IPloneFormGenField.implementedBy(ttype)]
        fieldsets = [ttype.meta_type for ttype in installed_types
                     if IPloneFormGenFieldset.implementedBy(ttype)]
        fields_js = " ".join([field_layout.substitute({'typeid':atype, 'fgtype': 'fgfield'})
                               for atype in fields + fieldsets]) 
        adapters = [ttype.meta_type for ttype in installed_types
                    if IPloneFormGenActionAdapter.implementedBy(ttype)]
        adapters_js = " ".join([field_layout.substitute({'typeid':atype, 'fgtype': 'fgadapter'})
                               for atype in fields + fieldsets]) 
        thankers = [ttype.meta_type for ttype in installed_types
                    if IPloneFormGenThanksPage.implementedBy(ttype)]
        thankers_js = " ".join([field_layout.substitute({'typeid':atype, 'fgtype': 'fgthanker'})
                               for atype in fields + fieldsets]) 

        js_layout = string.Template("pfgFormBuild.getJs(\"$js\");")
        helperjs = " ".join([js_layout.substitute({'js': js}) 
                            for js in self.helperjs()])

        css_layout = string.Template("pfgFormBuild.getCss(\"$css\");")
        helpercss = " ".join([css_layout.substitute({'css': css}) 
                            for css in self.helpercss()])
        
        baseurl = getToolByName(self.context, 'portal_url')()

        return """
            // App code
            jq(document).ready(function() {

                //Initialize the form build manager
                pfgFormBuild.initialize()
                pfgFormBuild.baseURL = \"%(baseurl)s\"
                
                //Register existed helperjs and css
                %(helperjs)s
                %(helpercss)s
                
                //Add more style to portal message
                jq("#kssPortalMessage").addClass("ajax-portalmessage");
                
                //Add class to addable types
                %(fields_js)s
                %(adapters_js)s
                %(thanksers_js)s
                
                //Make addable types dragable 
                jq(".addableItem").draggable({
                    helper: "clone"
                });
                
            })
        """ % {'baseurl': baseurl,
               'helperjs': helperjs,
               'helpercss': helpercss,
               'fields_js': fields_js, 
               'adapters_js': adapters_js, 
               'thanksers_js': thankers_js}

