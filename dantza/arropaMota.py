from dantza.models import ArropaMota

class ArropaMotaLoader:

	arropaMota_zerrenda = None

	def __init__(self):
		self.arropaMota_zerrenda = ArropaMota.objects.all().order_by("mota")
		print("--> ArropaMotaLoader kargatu da <--")

	def get_arropaMota(self):
		return self.arropaMota_zerrenda

