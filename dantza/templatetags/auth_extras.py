from django import template
from dantza.models import *

register = template.Library()

@register.filter(name='has_group') 
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter(name='get')
def get(request,get_tag):
	return request.get(get_tag)

@register.filter(name='is_partehartzaile')
def is_partehartzaile(ekitaldi,dantzari):
	return ekitaldi.is_partehartzaile(dantzari)

@register.filter(name='has_dantza')
def has_dantza(ekitaldi,dantza):
	return ekitaldi.has_dantza(dantza)

@register.filter(name='get_dantzari')
def get_dantzari(user):
	return Dantzaria.objects.get(user=user)

@register.filter(name='split')
def split(str,char):
	return str.split(char)

@register.filter(name='messages_for')
def message_for(list,p):
	return list.filter(hartzailea=p)

