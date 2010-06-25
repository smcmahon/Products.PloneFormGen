from Products.Five import BrowserView

class FormConditional(BrowserView):
	def fieldBelongsToSet(self, mset, fieldName):
		if mset.find(fieldName)!=-1:
			return True
		else:
			return False