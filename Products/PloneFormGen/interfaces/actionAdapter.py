from zope.interface import Interface, Attribute

# This is just a marker inteface; PFG identifies adapters by asking
# contained objects if they provide this interface.
#
# Note that marking an object type with this interface 
# does not automatically put it on the "add" menu. That
# needs to be done via portal_types.

class IPloneFormGenActionAdapter(Interface):
    """actionAdapter interface
    """
    
    meta_type = Attribute("archetypes meta type")
    """
    Must match GS type declaration.
    """

    def onSuccess(fields, REQUEST=None):
        """
        Called by form to invoke custom success processing.
        return None (or don't use "return" at all) if processing is
        error-free.
        
        Return a dictionary like {'field_id':'Error Message'}
        and PFG will stop processing action adapters and
        return back to the form to display your error messages
        for the matching field(s).

        You may also use Products.PloneFormGen.config.FORM_ERROR_MARKER
        as a marker for a message to replace the top-of-the-form error
        message.

        For example, to set a message for the whole form, but not an
        individual field:

        {FORM_ERROR_MARKER:'Yuck! You will need to submit again.'}

        For both a field and form error:

        {FORM_ERROR_MARKER:'Yuck! You will need to submit again.',
         'field_id':'Error Message for field.'}
        
        Messages may be string types or zope.i18nmessageid objects.                
        """

    execCondition = Attribute("Execution Condition")
    """
    If this attribute exists, the form folder will
    use getRawExecCondition.
    """

    def getRawExecCondition():
        """
        Optional.
        
        Should return a TALES expession that will be evaluated
        in the context of the object to determine whether or not
        to execute an action adapter's onSuccess method.
        """
