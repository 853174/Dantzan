from django.urls import path
from django.conf.urls import url
from dantza import views

app_name = 'dantza'
urlpatterns = [
	path('', views.index, name = 'index'),
	
	# Erabiltzaileen url-ak
	path('login', views.login_bista, name = 'login'),
	path('logout', views.logout_bista, name = 'logout'),
	path('signup', views.signup_bista, name = 'signup'),
	path('signup_end', views.signup_amaitu, name = 'signup_end'),
	path('profile', views.profile_v2, name = 'profile'),
	
	# Administratzaileen url-ak
	path('dashboard', views.dashboard, name = 'dashboard'),
	path(r'dantzari/<int:dtz_id>/', views.profile, name='profile'),

	# Maileguak
	path('maileguak', views.maileguak, name = 'maileguak'),
	path('maileguak/berria', views.mailegua_egin, name = 'mailegua_egin'),
	
	# Materiala
	path('materiala', views.materiala, name = 'materiala'),
	path(r'materiala/<int:m_id>/', views.material_info, name='material_info'),
	
	# Arropa
	path('arropa', views.arropa, name = 'arropa'),
	path(r'arropa/<int:a_id>/', views.arropa_info, name='arropa_info'),

	# Armairuak
	path('inbentarioa',views.inbentario, name = 'inbentarioa'),
	path(r'inbentarioa/<int:ar_id>/',views.armairua, name = 'armairua'),

	# Ekitaldiak
	path('ekitaldiak',views.ekitaldiak, name = 'ekitaldiak'),
	path(r'ekitaldiak/<int:e_id>/', views.ekitaldi, name = 'ekitaldi'),

	# Dantzak
	path('dantzak',views.dantzak, name = 'dantzak'),
	path(r'dantzak/<int:d_id>/',views.dantza, name = 'dantza'),
]