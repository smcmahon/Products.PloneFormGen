A minor bug in Archetypes 1.5.0 (part of Plone 3.0, fixed by Archetypes 1.5.2
in Plone 3.0.1) prevents use of the PloneFormGen Selection and multi-selection
form fields by users without content modification rights.

To work around this problem, you need to either:

 * Upgrade Plone 3.0 to Plone 3.0.1; or,

 * Check out a fixed copy of the Archetypes 1.5 branch from svn,
   https://svn.plone.org/svn/archetypes/Archetypes/branches/1.5/ ;
   or,
   
 * Apply to Products/Archetypes/branches/1.5/browser/configure.zcml
   the changes below (two lines in one file):
   

Index: configure.zcml
===================================================================
--- configure.zcml      (revision 8563)
+++ configure.zcml      (revision 8565)
@@ -30,7 +30,7 @@
       for="*"
       name="at_selection_widget"
       class=".widgets.SelectionWidget"
-      permission="cmf.ModifyPortalContent"
+      permission="zope.Public"
       allowed_attributes="getSelected"
       />
 
@@ -38,7 +38,7 @@
       for="*"
       name="at_textarea_widget"
       class=".widgets.TextareaWidget"
-      permission="cmf.ModifyPortalContent"
+      permission="zope2.View"
       allowed_attributes="getSelected lookupMime"
       />
