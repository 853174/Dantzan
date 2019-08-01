from django.shortcuts import render, render_to_response
from django.template import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from dantza.models import *
from django.contrib.auth.decorators import login_required
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
import os

import timeit

# Create your views here.

MEDIA_ROOT = 'mysite/static/'

def handler404(request, exception):
	return render(request,'dantza/index.html', {'err':'Bilatu duzun orria ez da existitzen, barkatu.'})


def index(request):
	if 'd' in request.GET:
		delete = request.GET['id']
		Oharra.objects.get(pk=delete).delete()
		return HttpResponseRedirect('/')

	if request.user.is_authenticated:
		if Dantzaria.objects.filter(user=request.user).exists():
			d = Dantzaria.objects.get(user=request.user)
			o_list = Oharra.objects.all()
			return render(request,'dantza/index.html', {'mezuak':o_list})
		else:
			return render(request,'dantza/index.html', {'err':'Ez duzu erregistroa amaitu, sakatu <a href="/signup_end">hemen</a> amaitzeko'})
	return render(request,'dantza/index.html', {})

def login_bista(request):
	if request.method == 'POST':
		erab = request.POST['username']
		passwd = request.POST['password']
		user = authenticate(username=erab, password= passwd)
		if user is not None:
			if user.is_active:
				login(request, user)
				if 'next' in request.GET:
					return HttpResponseRedirect(request.GET['next'])
				else:
					return HttpResponseRedirect('/')
			else:
				return render(request, 'dantza/login.html', {'log_err':'Kontua desaktibatuta dago'})
		else:
			return render(request, 'dantza/login.html', {'log_err':'Login desegokia'})
	else:
		return render(request, 'dantza/login.html', {})
	

def signup_bista(request):
	if request.method == 'POST':
		erab = request.POST['username']
		if erab == "":
			return render(request, 'dantza/signup.html', {'signup_err':'Erabiltzaile izena ezin du hutsa izan'})
		if User.objects.filter(username=erab).exists() :
			return render(request, 'dantza/signup.html', {'signup_err':'Erabiltzaile hori existitzen da jada, aukeratu beste izen bat'})
	
		pass1 = request.POST['password']
		pass2 = request.POST['password2']
		if pass1 == pass2 and pass1 != "":
			# Zuzen
			user = User(username=erab)
			user.save()
			user.set_password(pass1)
			user.save()
			login(request, user)
			return render(request, 'dantza/signup.html',{'step':2})
		else:	
			# pasahitz okerrak!
			return render(request, 'dantza/signup.html', {'signup_err':'Pasahitzak ez dira berdinak'})

	else:
		return render(request,'dantza/signup.html', {})

	
def signup_amaitu(request):
	if request.method == 'POST':
		
		izen = request.POST['izena']
		abizen = request.POST['abizenak']
		jaio_dat = request.POST['jaio']
		emaila = request.POST['email']
		tel = request.POST['tel']

		dtz = Dantzaria(user=request.user, izena=izen, abizenak=abizen,jaiotze_data=jaio_dat,email=emaila)
		dtz.save()
		
		telefono = Telefono(zenbakia=tel, dantzari=dtz)
		telefono.save()

		mezua = izen + " " + abizen + " dantzaria erregistratu da."
		o = Oharra(mezua=mezua,hartzailea='AD',data=datetime.datetime.today())
		o.save()
		
		return HttpResponseRedirect('/')
	
	else:
		if request.user.is_authenticated:
			return render(request, 'dantza/signup.html',{'step':2})
		else:
			return HttpResponseRedirect('/signup')
	
def logout_bista(request):
	logout(request)
	return HttpResponseRedirect('/')

@login_required(login_url='/login')
def dashboard(request):
	dantzari_list = Dantzaria.objects.all()
	maileguak = Mailegua.objects.filter(itzulita=False)
	if request.method == 'POST':
		if 'm' in request.POST:
			mezua = request.POST['m']
			if mezua == '':
				return render(request,'dantza/dashboard.html',{'d_list':dantzari_list, 'mail_list':maileguak, 'h_list': HARTZAILEA, 'err':'Mezuak ezin du hutsa izan.'})
			else:
				hart = request.POST['r']
				o = Oharra(mezua=mezua,hartzailea=hart,data=datetime.datetime.today())
				o.save()

	return render(request,'dantza/dashboard.html',{'d_list':dantzari_list, 'mail_list':maileguak, 'h_list': HARTZAILEA})

@login_required(login_url='/login')
def profile_v2(request):
	d = Dantzaria.objects.get(user=request.user)
	return HttpResponseRedirect('/dantzari/'+str(d.pk))
	
	

@login_required(login_url='/login')
def profile(request, dtz_id):
	d = Dantzaria.objects.get(pk=dtz_id)
	if request.method == 'POST':
		if 'izena' in request.POST:
			newU = request.POST['izena']
			d.izena = newU

			newA = request.POST['abizenak']
			d.abizenak = newA

			newD = request.POST['jaio']
			d.jaiotze_data = newD

			newE = request.POST['email']
			d.email = newE

			d.save()
			
		elif 'tel' in request.POST:
			newT = request.POST['tel']
			telefono = Telefono(zenbakia=newT, dantzari=d)
			telefono.save()
			
		return HttpResponseRedirect('/dantzari/'+ str(dtz_id))
	
	else:
		if 'ma' in request.GET:
			# ma = MaterialArduraduna(dantzari=d,haste_data=datetime.datetime.today(),oharrak='')
			# ma.save()
			
			# Baimenak eman
			user = User.objects.get(username=d.user.username)
			group = Group.objects.get(name='material_arduradunak')
			user.groups.add(group)
			
			return HttpResponseRedirect('/dantzari/'+ str(dtz_id))
			
		elif 'n_ma' in request.GET:
			# MaterialArduraduna.objects.filter(dantzari=d).delete()
			
			# Baimenak kendu
			user = User.objects.get(username=d.user.username)
			group = Group.objects.get(name='material_arduradunak')
			group.user_set.remove(user)
			
			return HttpResponseRedirect('/dantzari/'+ str(dtz_id))
			
		elif 'aa' in request.GET:
			# aa = ArropaArduraduna(dantzari=d,haste_data=datetime.datetime.today(),oharrak='')
			# aa.save()
			
			# Baimenak eman
			user = User.objects.get(username=d.user.username)
			group = Group.objects.get(name='arropa_arduradunak')
			user.groups.add(group)
			
			return HttpResponseRedirect('/dantzari/'+ str(dtz_id))
				
		elif 'n_aa' in request.GET:
			# ArropaArduraduna.objects.filter(dantzari=d).delete()
			
			# Baimenak kendu
			user = User.objects.get(username=d.user.username)
			group = Group.objects.get(name='arropa_arduradunak')
			group.user_set.remove(user)
			return HttpResponseRedirect('/dantzari/'+ str(dtz_id))
		
		elif 'del' in request.GET:
			User.objects.filter(username=d.user.username).delete()
			return HttpResponseRedirect('/')
	
	return render(request,'dantza/profile.html',{'d':d})

# MAILEGUAK
# Admin, material arduradunak edo arropa arduradunak

@login_required(login_url='/login')
def maileguak(request):
	if not request.user.groups.filter(name='arropa_arduradunak').exists() and not request.user.is_superuser and not request.user.groups.filter(name='material_arduradunak').exists():
		return HttpResponseRedirect('/')
	
	maileguak = Mailegua.objects.filter(itzulita=False)

	if 'return_success' in request.GET:
		return render(request,'dantza/maileguak.html',{'mail_list':maileguak,'success': 'Mailegua itzuli da.'})		
			
	elif 'return' in request.GET:
		m = Mailegua.objects.get(pk=request.GET['id'])
		m.itzulita = True
		for arr in m.arropa.all():
			arr.mailegatua = False
			arr.save()
		for mat in m.materiala.all():
			mat.mailegatua = False
			mat.save()
		m.save()

		return HttpResponseRedirect('/maileguak?return_success')
	return render(request,'dantza/maileguak.html',{'mail_list':maileguak})

@login_required(login_url='/login')
def mailegua_egin(request):
	if not request.user.groups.filter(name='arropa_arduradunak').exists() and not request.user.is_superuser and not request.user.groups.filter(name='material_arduradunak').exists():
		return HttpResponseRedirect('/')
	
	dantzari_list = Dantzaria.objects.all()
	maileguak = Mailegua.objects.filter(itzulita=False)

	m_list = [m for m in Materiala.objects.all() if m.mailegatu_kop() != m.tresna_kop()]
	a_list = Arropa.objects.filter(mailegatua=False)

	if request.method == 'POST':
		if 'd' in request.POST:

			if request.POST['d'] == '-1':
				return render(request,'dantza/mailegu_berria.html',{'d_list':dantzari_list, 'mail_list':maileguak, 
																   'materiala':m_list, 'arropa':a_list, 'err': 'Ezin da dantzaririk gabeko mailegurik egin.'})
			
			m_lista = []
			for m in request.POST.getlist('materialak'):

				if m == '-1':
					continue
				mat = Materiala.objects.get(pk=m)
				ts = mat.get_mailegatu_gabeko_tresna(request.POST.getlist('materialak').count(m))
				if len(ts) != 0:
					for t in ts:
						m_lista.append(t)
				else:
					return render(request,'dantza/mailegu_berria.html',{'d_list':dantzari_list, 'mail_list':maileguak, 
																   'materiala':m_list, 'arropa':a_list, 'err': 'Aukeratutako ' + str(mat) + ' ez dago eskuragai.'})
			
			arr_lista = []
			for i in request.POST.getlist('arropa'):
				if i == '-1':
					continue
				a = Arropa.objects.get(pk=i)
				if a is not None:
					arr_lista.append(a)
				else:
					return render(request,'dantza/mailegu_berria.html',{'d_list':dantzari_list, 'mail_list':maileguak, 
																   'materiala':m_list, 'arropa':a_list, 'err': 'Aukeratutako ' + a + ' ez dago eskuragai.'})
			
			if len(m_lista) == 0 and len(arr_lista) == 0:
				return render(request,'dantza/mailegu_berria.html',{'d_list':dantzari_list, 'mail_list':maileguak, 
							'materiala':m_list, 'arropa':a_list, 'err': 'Gutxienez material edo arropa bat hautatu behar da.'})
			
			if request.POST['d'] == '-2':
				# Kanpoko taldeari mailegua
				d = Dantzaria.objects.get(user=request.user)
				dt = request.POST['kanpo_talde']
				if dt == "":
					return render(request,'dantza/mailegu_berria.html',{'d_list':dantzari_list, 'mail_list':maileguak,
							'materiala':m_list, 'arropa':a_list, 'err': 'Dantza taldearen izena adierazi behar da.'})
				mail = Mailegua(dantzari=d,mailegatze_data=datetime.datetime.today(),itzulita=False,dantza_taldea=dt)
			else:
				# Taldeko kideari mailegua
				d = Dantzaria.objects.get(pk=request.POST['d'])
				mail = Mailegua(dantzari=d,mailegatze_data=datetime.datetime.today(),itzulita=False)

			
			mail.save()
			mail.arropa.set(arr_lista)
			mail.materiala.set(m_lista)
			mail.save()

			# Mailegatutako tresnak eta arropak "mailegatu" bezala markatu

			for x in arr_lista + m_lista:
				x.mailegatua = True
				x.save()
			
			return HttpResponseRedirect('/maileguak/berria?new_success')

	else:
		if 'new_success' in request.GET:
			return render(request,'dantza/mailegu_berria.html',{'d_list':dantzari_list, 'mail_list':maileguak, 
															'materiala':m_list, 'arropa':a_list, 'success': 'Mailegu berria zuzen sortu da.'})
		elif 'return_success' in request.GET:
			return render(request,'dantza/mailegu_berria.html',{'d_list':dantzari_list, 'mail_list':maileguak, 'materiala':m_list, 'arropa':a_list, 'arropa':a_list, 'success': 'Mailegua itzuli da.'})		
				
		elif 'return' in request.GET:
			m = Mailegua.objects.get(pk=request.GET['id'])
			m.itzulita = True
			for arr in m.arropa.all():
				arr.mailegatua = False
				arr.save()
			for mat in m.materiala.all():
				mat.mailegatua = False
				mat.save()
			m.save()

			return HttpResponseRedirect('/maileguak?return_success')
		return render(request,'dantza/mailegu_berria.html',{'d_list':dantzari_list,'mail_list':maileguak,'materiala':m_list,'arropa':a_list})


# MATERIALA
# Material arduradunek bakarrik

@login_required(login_url='/login')
def materiala(request):
	if not request.user.groups.filter(name='material_arduradunak').exists():
		return HttpResponseRedirect('/')
	m = Materiala.objects.all()
	
	if request.method == 'POST':

		if 'kop' in request.POST:
			if request.POST['type'] == '-1':
				if request.POST['newType'] == "":
					return render(request,'dantza/materiala.html',{'m_list':m, 'err':'Mota berria gehitu nahi baduzu, ezin du hutsa izan.'})
				else:
					mt = Materiala(mota=request.POST['newType'])
					mt.save()
					
			else:
				mt = Materiala.objects.get(pk=request.POST['type'])
			for x in range(0, int(request.POST['kop'])):
				t = Tresna(material_mota=mt)
				t.save()
	
	return render(request,'dantza/materiala.html',{'m_list':m})

@login_required(login_url='/login')
def material_info(request,m_id):
	if not request.user.groups.filter(name='material_arduradunak').exists():
		return HttpResponseRedirect('/')
	
	m_list = Tresna.objects.filter(material_mota=Materiala.objects.get(pk=m_id))
	
	if 'delete' in request.GET:
		t = Tresna.objects.get(pk=request.GET['id'])
		if t.material_mota.tresna_kop() == 1:
			t.material_mota.delete()
			return HttpResponseRedirect('/materiala')
		else:
			t.delete()
			if 'page' in request.GET:
				return HttpResponseRedirect('/materiala/' + str(m_id) + '/?page=' + request.GET['page'])
			
			return HttpResponseRedirect('/materiala/' + str(m_id))
	
	paginator = Paginator(m_list, 5)
	page = request.GET.get('page')
	try:
		tresnak = paginator.page(page)
	except PageNotAnInteger:
		tresnak = paginator.page(1)
	except EmptyPage:
		tresnak = paginator.page(paginator.num_pages)	
		
	return render(request,'dantza/material_info.html',{'a_list':tresnak})

# ARROPA
# Arropa aduradunek bakarrik

@login_required(login_url='/login')
def arropa(request):
	if not request.user.groups.filter(name='arropa_arduradunak').exists():
		return HttpResponseRedirect('/')
	

	a_list = ArropaMota.objects.all().order_by("mota")

	paginator = Paginator(a_list, 10)
	page = request.GET.get('page')
	try:
		arropa = paginator.page(page)
	except PageNotAnInteger:
		arropa = paginator.page(1)
	except EmptyPage:
		arropa = paginator.page(paginator.num_pages)	

	if request.method == 'POST':
		if 'kop' in request.POST:
			k = request.POST['kop']
			m = request.POST['type']
			if m == '-1':
				if request.POST['newType'] == "":
					return render(request,'dantza/arropa.html',{'err':'Mota berria gehitu nahi baduzu, ezin du hutsa izan.','a_list':arropa,'a_osoa':a_list})
				
				m = ArropaMota(mota=request.POST['newType'])
				m.save()
			else:
				m = ArropaMota.objects.get(pk=m)
			
			d = request.POST['desk']

			for x in range(0,int(k)):
				a = Arropa(mota=m,egoera='Ona',deskribapena=d)
				a.save()

			a_list = ArropaMota.objects.all().order_by("mota")

			paginator = Paginator(a_list, 10)
			page = request.GET.get('page')
			try:
				arropa = paginator.page(page)
			except PageNotAnInteger:
				arropa = paginator.page(1)
			except EmptyPage:
				arropa = paginator.page(paginator.num_pages)

			return render(request,'dantza/arropa.html',{'success':'Zerrenda eguneratu egin da.','a_list':arropa,'a_osoa':a_list})

	return render(request,'dantza/arropa.html',{'a_list':arropa,'a_osoa':a_list})

@login_required(login_url='/login')
def arropa_info(request,a_id):
	if not request.user.groups.filter(name='arropa_arduradunak').exists():
		return HttpResponseRedirect('/')
	
	a_list = Arropa.objects.filter(mota=ArropaMota.objects.get(pk=a_id))
	
	if request.method == 'POST':
		if 'desk' in request.POST:
			a = Arropa.objects.get(pk=request.GET['id'])
			if request.POST['aldatuEgoera'] == '1':
				a.aldatuEgoera()
			
			a.deskribapena = request.POST['desk']
			a.save()

			if a.egoera == 'Txarra':
				mezua = str(a) + " egoera txarrean dago."
				o = Oharra(mezua=mezua,hartzailea='AA',data=datetime.datetime.today())
				o.save()

			if 'page' in request.GET:
				return HttpResponseRedirect('/arropa/' + str(a_id) + '/?page=' + request.GET['page'])
			
			return HttpResponseRedirect('/arropa/' + str(a_id))
	
	if 'delete' in request.GET:
		a = Arropa.objects.get(pk=request.GET['id'])
		if a.mota.arropa_kop() == 1:
			a.mota.delete()
			return HttpResponseRedirect('/arropa')
		else:
			a.delete()
			return HttpResponseRedirect('/arropa/' + str(a_id))
	
	paginator = Paginator(a_list, 5)
	page = request.GET.get('page')
	try:
		arropa = paginator.page(page)
	except PageNotAnInteger:
		arropa = paginator.page(1)
	except EmptyPage:
		arropa = paginator.page(paginator.num_pages)	
		
	return render(request,'dantza/arropa_info.html',{'a_list':arropa})


# Inbentarioaren kontsultak egiteko (erregistratutako edonork)
@login_required(login_url='/login')
def inbentario(request):
	ar_list = Armairua.objects.all().order_by('zbk')
	a_list = ArropaMota.objects.all()
	m_list = Materiala.objects.all()

	if request.method == 'POST':
		if 'm' in request.POST:
			mezua = request.POST['m']
			if mezua == '':
				return render(request,'dantza/materiala.html',{'m_list':m, 'err':'Mezuak ezin du hutsa izan.'})
			else:
				hart = request.POST['r']
				ig = Dantzaria.objects.get(user=request.user)
				o = Oharra(mezua=mezua,igorlea=ig,hartzailea=hart,data=datetime.datetime.today())
				o.save()

		if 'zbk' in request.POST:
			z = request.POST['zbk']
			if Armairua.objects.filter(zbk=z).exists():
				return render(request,'dantza/inbentario.html',{'armairuak':ar_list, 'arropa_list':a_list,'material_list':m_list, 'err':'Identifikadore hori duen armairua existitzen da jada.'})	
			else:
				if z == '':
					return render(request,'dantza/inbentario.html',{'armairuak':ar_list, 'arropa_list':a_list,'material_list':m_list, 'err':'Identifikadorea ezin du hutsa izan.'})	
				zh = request.POST['zehaztapenak']
				ar = Armairua(zbk=z,zehaztapenak=zh)
				ar.save()
				ar_list = Armairua.objects.all()

		if 'bilaketa' in request.POST:
			i = request.POST['bilaketa'][1:]
			if request.POST['bilaketa'][0] == 'A':
				am = ArropaMota.objects.get(pk=i)
				if am.armairua_du():
					aId,x = am.armairu_id()
					return HttpResponseRedirect('/inbentarioa/'+ str(aId) +'/')
				else:
					return render(request,'dantza/inbentario.html',{'armairuak':ar_list, 'arropa_list':a_list,'material_list':m_list, 'err':'Arropa honek ez du armairurik oraindik.'})	
			else:
				am = Materiala.objects.get(pk=i)
				if am.armairua_du():
					aId,x = am.armairu_id()
					return HttpResponseRedirect('/inbentarioa/'+ str(aId) +'/')
				else:
					return render(request,'dantza/inbentario.html',{'armairuak':ar_list, 'arropa_list':a_list,'material_list':m_list, 'err':'Material honek ez du armairurik oraindik.'})	

	return render(request,'dantza/inbentario.html',{'armairuak':ar_list, 'arropa_list':a_list,'material_list':m_list})	

@login_required(login_url='/login')
def armairua(request,ar_id):
	ar = Armairua.objects.get(pk=ar_id)

	if 'gordeA' in request.GET:
		a = ArropaMota.objects.get(pk=request.GET['id'])
		ar.gorde_arropa(a)
		ar.save()
		return HttpResponseRedirect('/inbentarioa/' + str(ar_id) + '/')

	if 'gordeM' in request.GET:
		m = Materiala.objects.get(pk=request.GET['id'])
		ar.gorde_materiala(m)
		ar.save()
		return HttpResponseRedirect('/inbentarioa/' + str(ar_id) + '/')

	if 'ateraA' in request.GET:
		a = ArropaMota.objects.get(pk=request.GET['id'])
		ar.atera_arropa(a)
		ar.save()
		return HttpResponseRedirect('/inbentarioa/' + str(ar_id) + '/')

	if 'ateraM' in request.GET:
		m = Materiala.objects.get(pk=request.GET['id'])
		ar.atera_materiala(m)
		ar.save()
		return HttpResponseRedirect('/inbentarioa/' + str(ar_id) + '/')

	a_list = []
	for a in ArropaMota.objects.all():
		if not a.armairua_du():
			a_list.append(a)

	m_list = []
	for m in Materiala.objects.all():
		if not m.armairua_du():
			m_list.append(m)

	ar = Armairua.objects.get(pk=ar_id)
	return render(request,'dantza/armairua.html',{'armairua':ar,'gordetzeke_arropa':a_list, 'gordetzeke_materiala':m_list})	


# Ekitaldiak
@login_required(login_url='/login')
def ekitaldiak(request):
	if request.method == "POST":
		if 'izena' in request.POST:
			izena = request.POST["izena"];
			lekua = request.POST["lekua"];
			data = request.POST["data"];
			data2 = request.POST["data2"]
			diru = request.POST["diru"];
			beste_info = request.POST["ohar"]
			data_ordua = data +" "+ data2
			e = Ekitaldia(izena=izena,data=data_ordua,lekua=lekua,dirua=diru,beste_info=beste_info)
			e.save()

	return render(request,'dantza/ekitaldiak.html',{'e_list':Ekitaldia.objects.all()})

@login_required(login_url='/login')
def ekitaldi(request,e_id):
	e = Ekitaldia.objects.get(pk=e_id)
	dantzariak = Dantzaria.objects.all()
	dantzak = Dantza.objects.all()

	if 'd_id' in request.GET:
		d = Dantzaria.objects.get(pk=request.GET['d_id'])
		if 'ph' in request.GET:
			e.dantzaria_gehitu(d)
			e.save()
		elif 'ep' in request.GET:
			e.dantzaria_kendu(d)
			e.save()
		return HttpResponseRedirect('/ekitaldiak/' + str(e_id) + '/')

	if 'dantza_id' in request.GET:
		d = Dantza.objects.get(pk=request.GET['dantza_id'])
		if 'db' in request.GET:
			e.dantza_gehitu(d)
			e.save()
		elif 'de' in request.GET:
			e.dantza_kendu(d)
			e.save()
		return HttpResponseRedirect('/ekitaldiak/' + str(e_id) + '/')


	return render(request,'dantza/ekitaldi.html',{'ekitaldi':e, 'd_list': dantzariak,'dantzak':dantzak})


@login_required(login_url='/login')
def dantzak(request):

	d_list = Dantza.objects.all()

	if request.method == 'POST':
		if 'izena' in request.POST:
			d = Dantza(izena=request.POST['izena'],deskr=request.POST['deskr'],iraupena=request.POST['iraupen'])
			d.save()

			if 'myfiles' in request.FILES:
				fs = FileSystemStorage()
				for f in request.FILES.getlist('myfiles'):
					filename = MEDIA_ROOT + 'dantza_dock/' + d.izena + '/' + f.name
					fs.save(filename, f)
					ddock = DantzaDock(dantza=d,dock=filename)
					ddock.save()

			return HttpResponseRedirect('/dantzak?success')

	if 'success' in request.GET:
		return render(request,'dantza/dantzak.html',{'dantzak':d_list, 'success':'Dantza zuzen sortu da.'})

	return render(request,'dantza/dantzak.html',{'dantzak':d_list})



@login_required(login_url='/login')
def dantza(request,d_id):
	d = Dantza.objects.get(pk=d_id)

	if 'd' in request.GET:
		doc = DantzaDock.objects.get(pk=request.GET['id'])
		#Ezabatu direktoriotik
		os.remove(doc.dock)
		# Azkenik, ezabatu datubasetik
		doc.delete()
		return HttpResponseRedirect("/dantzak/"+str(d_id)+"/")

	if request.method == 'POST':
		if 'myfiles' in request.FILES:
			fs = FileSystemStorage()
			for f in request.FILES.getlist('myfiles'):
				filename = MEDIA_ROOT + 'dantza_dock/' + d.izena + '/' + f.name
				fs.save(filename, f)
				ddock = DantzaDock(dantza=d,dock=filename)
				ddock.save()

		return HttpResponseRedirect('/dantzak/'+str(d_id)+'/')
	return render(request,'dantza/dantza.html',{'dantza':d})
