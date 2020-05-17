from django.contrib import admin

from .models import Utente, Contenuto, Like, Sessione, Commento, Categoria, Giorno

# Register your models here.

admin.site.register(Utente)
admin.site.register(Contenuto)
admin.site.register(Like)
admin.site.register(Commento)
admin.site.register(Sessione)
admin.site.register(Categoria)
admin.site.register(Giorno)
