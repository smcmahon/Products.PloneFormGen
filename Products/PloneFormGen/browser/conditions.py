from Products.Five import BrowserView
import pdb
class FormConditional(BrowserView):
    def displayFields(self, mset, type):
        priorityFields = ['String Field', "Text Field", "Whole Number Field", "Checkbox Field", "Date/Time Field", "File Field", "Password Field"]
        displayPriorityFields = []
        displayTheRest = []
        displayAdapters = []
        for field in mset:
          if field['title'] in priorityFields:
            displayPriorityFields.append(field)
          elif field['title'].find("Field") != -1:
            displayTheRest.append(field)
          elif field['title'].find("Adapter") != -1:
            displayAdapters.append(field)
        if type == "Field":
          return displayPriorityFields + displayTheRest
        elif type == "Adapter":
          return displayAdapters