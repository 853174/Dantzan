from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Dantzariak

class Dantzaria(models.Model):
	# Login egiteko
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	
	#Gure atributuak
	izena = models.CharField(max_length=50)
	abizenak = models.CharField(max_length=200)
	jaiotze_data = models.DateTimeField('jaiotze data')
	email = models.CharField(max_length=100)
	
	def __str__(self):
		return self.izena + ' ' + self.abizenak
	
	def adina(self):
		today = date.today()
		return today.year - self.jaiotze_data.year - ((today.month, today.day) < (self.jaiotze_data.month, self.jaiotze_data.day))
	
	def telefonoak(self):
		t_list = Telefono.objects.filter(dantzari=self)				
		return ', '.join(str(e.zenbakia) for e in t_list)
	
	def mailegu_lista(self):
		return Mailegua.objects.filter(dantzari=self)
	
	def is_materialArduraduna(self):
		return self.user.groups.filter(name='material_arduradunak').exists()
	
	def is_arropaArduraduna(self):
		return self.user.groups.filter(name='arropa_arduradunak').exists()
		
	
class Telefono(models.Model):
	zenbakia = models.IntegerField()
	dantzari = models.ForeignKey(Dantzaria, on_delete=models.CASCADE)
	
	def __str__(self):
		return str(self.zenbakia)


HARTZAILEA = (
	('MA', 'Material arduraduna'),
	('AA', 'Arropa arduraduna'),
	('DT', 'Dantzaria'),
	('AD', 'Administratzailea'),
)

# Arduradunen oharrak
class Oharra(models.Model):
	mezua = models.CharField(max_length=200)
	igorlea = models.CharField(max_length=100, default="auto")
	hartzailea = models.CharField(max_length=10, choices = HARTZAILEA)
	data = models.DateTimeField('Oharraren data')

	def __str__(self):
		return "[" + self.igorlea + "] " + self.mezua 

	def is_forMaterialArduraduna(self):
		return (self.hartzailea == 'MA')

	def is_forArropaArduraduna(self):
		return (self.hartzailea == 'MA')

	def is_forDantzari(self):
		return (self.hartzailea == 'DT')


# Materiala

class Materiala(models.Model):
	mota = models.CharField(max_length=50)
	
	def __str__(self):
		return self.mota
	
	def get_mailegatu_gabeko_tresna(self):
		for t in Tresna.objects.filter(material_mota=self,mailegatua=False):
			return t
		return None
	
	def tresna_kop(self):
		return len(Tresna.objects.filter(material_mota=self))
	
	def mailegatu_kop(self):
		kop = 0
		for t in Tresna.objects.filter(material_mota=self,mailegatua=True):
			kop +=1
		return kop

	def libre_kop(self):
		return self.tresna_kop() - self.mailegatu_kop()

	def armairua_du(self):
		ar_list = Armairua.objects.all()
		for ar in ar_list:
			if ar.materiala.filter(pk=self.pk).exists():
				return True
		return False

	def armairu_id(self):
		ar_list = Armairua.objects.all()
		for ar in ar_list:
			if ar.materiala.filter(pk=self.pk).exists():
				return ar.pk, ar.zbk
		return None
	
class Tresna(models.Model):
	material_mota = models.ForeignKey(Materiala, on_delete=models.CASCADE)

	mailegatua = models.BooleanField(default=False)
	
	def __str__(self):
		return self.material_mota.mota

# Arropa

class ArropaMota(models.Model):
	mota = models.CharField(max_length=100)
	
	def __str__(self):
		return self.mota
	
	def get_mailegatu_gabeko_arropa(self):
		for a in Arropa.objects.filter(mota=self,mailegatua=False):
			return a
		return None
	
	def arropa_kop(self):
		return len(Arropa.objects.filter(mota=self))
	
	def mailegatu_kop(self):
		i = 0
		for a in Arropa.objects.filter(mota=self,mailegatua=True):
			i += 1
		return i

	def armairua_du(self):
		ar_list = Armairua.objects.all()
		for ar in ar_list:
			if ar.arropa.filter(pk=self.pk).exists():
				return True
		return False

	def armairu_id(self):
		ar_list = Armairua.objects.all()
		for ar in ar_list:
			if ar.arropa.filter(pk=self.pk).exists():
				return ar.pk, ar.zbk
		return None

EGOERA = (
	('ONA','Ona'),
	('TXARRA','Txarra'),
)

class Arropa(models.Model):
	mota = models.ForeignKey(ArropaMota, on_delete=models.CASCADE)
	egoera = models.CharField(max_length=100, choices = EGOERA)
	deskribapena = models.CharField(max_length=200, blank=True)

	mailegatua = models.BooleanField(default=False)
	
	def __str__(self):
		if self.deskribapena != '':
			return self.mota.mota + ' (' + self.deskribapena + ')'
		else:
			return self.mota.mota
	
	def aldatuEgoera(self):
		if self.egoera == 'Ona':
			self.egoera = 'Txarra'
		else:
			self.egoera = 'Ona'

	def get_mailegua(self):
		if self.mailegatua:
			for m in Mailegua.objects.filter(itzulita=False):
				if m.arropa.filter(pk=self.pk).exists():
					return m	
		else:
			return None
	
	
# Maileguak

class Mailegua(models.Model):
	# Nori
	dantzari = models.ForeignKey(Dantzaria, on_delete=models.CASCADE)
	# Zer
	materiala = models.ManyToManyField(Tresna, blank=True)
	arropa = models.ManyToManyField(Arropa, blank=True)
	# Noiz
	mailegatze_data = models.DateTimeField('mailegatze data')
	# Itzulita dago?
	itzulita = models.BooleanField(default=False)


	# Baina kanpoko talde batentzat mailegua bada?
	# dantzari atributua nork egin duen mailegua adieraziko du... +
	dantza_taldea = models.CharField(max_length=200, blank=True)
	
	
# ###################################################################

# Inbentarioaren kudeaketarako

class Armairua(models.Model):
	zbk = models.CharField(max_length=100)
	zehaztapenak = models.CharField(max_length=200, blank=True)
	materiala = models.ManyToManyField(Materiala, blank=True)
	arropa = models.ManyToManyField(ArropaMota, blank=True)

	def __str__(self):
		return self.zbk

	def gorde_arropa(self,a):
		self.arropa.add(a)

	def gorde_materiala(self,m):
		self.materiala.add(m)

	def atera_arropa(self,a):
		self.arropa.remove(a)

	def atera_materiala(self,m):
		self.materiala.remove(m)
	


#Dantzak
class Dantza(models.Model):
	izena = models.CharField(max_length=100)
	deskr = models.CharField(max_length=200, blank=True)
	iraupena = models.IntegerField()

	def __str__(self):
		return self.izena

	def dokumentazioa(self):
		return DantzaDock.objects.filter(dantza=self)

	def dokumentu_kopurua(self):
		return len(self.dokumentazioa())

# Dantzen dokumentuak
class DantzaDock(models.Model):
	dantza = models.ForeignKey(Dantza,on_delete=models.CASCADE)
	dock = models.CharField(max_length=500)

	def __str__(self):
		return self.dock.split('/')[-1]

	def get_static(self):
		d_split = self.dock.split('/')
		return '/'.join(d_split[-3:])

# Dantza saioak
class Ekitaldia(models.Model):
	izena = models.CharField(max_length=200)
	data = models.DateTimeField('aktuazio data')
	lekua = models.CharField(max_length=100)

	dirua = models.IntegerField(blank=True)
	beste_info = models.CharField(max_length=500, blank=True)

	dantzariak = models.ManyToManyField(Dantzaria, blank=True)

	dantzak = models.ManyToManyField(Dantza, blank=True)

	def __str__(self):
		return self.izena

	def is_partehartzaile(self,d):
		return (d in self.dantzariak.all())

	def dantzaria_gehitu(self,d):
		self.dantzariak.add(d)

	def dantzaria_kendu(self,d):
		self.dantzariak.remove(d)

	def has_dantza(self,d):
		return (d in self.dantzak.all())

	def dantza_gehitu(self,d):
		self.dantzak.add(d)

	def dantza_kendu(self,d):
		self.dantzak.remove(d)

	def aktuazio_denbora(self):
		temp = 0
		for d in self.dantzak.all():
			temp += d.iraupena
		return temp



