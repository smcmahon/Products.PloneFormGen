from Products.Five import BrowserView


class FormConditional(BrowserView):
    """
    Support for determining which fields are available, and how
    they should be sorted.
    """

    def displayFields(self, mset, type):
        """
        mset is a set of fields or adapters
        type = 'Field' | 'Adapter'

        Returns a list of fields or adapters; if 'Field' then
        returns prioritized first
        """

        priorityFields = {
            'FormBooleanField': 1,
            'FormDateField': 1,
            'FormMultiSelectionField': 1,
            'FormSelectionField': 1,
            'FormStringField': 1,
            'FormTextField': 1,
            'FormIntegerField': 1,
        }

        displayPriorityFields = []
        displayTheRest = []
        displayAdapters = []
        for field in mset:
            if field['id'] in priorityFields:
                displayPriorityFields.append(field)
            elif field['title'].find("Field") != -1:
                displayTheRest.append(field)
            elif field['title'].find("Adapter") != -1:
                displayAdapters.append(field)

        if type == "Field":
            return displayPriorityFields + displayTheRest
        elif type == "Adapter":
            return displayAdapters
