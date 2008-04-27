
PROJECTNAME = "PFGDataGrid"

DEFAULT_ADD_CONTENT_PERMISSION = "PloneFormGen: Add Content"

GLOBALS = globals()

try:
    from Products.PloneFormGen.content import fieldsBase
    HAVE_PFG = True
except ImportError:
    HAVE_PFG = False
