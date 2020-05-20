from django.db import models
import datetime
from django.utils import timezone

# Create your models here.

class Utente(models.Model):
    def __str__(self):
        return self.nickname
    Cod_Utente=models.AutoField(primary_key=True)
    nickname=models.CharField(max_length=30)
    password=models.CharField(max_length=70)
    email=models.CharField(max_length=30)
    descrizione=models.CharField(max_length=200)
    permesso=models.IntegerField()

class Categoria(models.Model):
    def __str__(self):
        return self.nomecategoria
    Cod_Cate=models.AutoField(primary_key=True)
    nomecategoria=models.CharField(max_length=20)

class Contenuto(models.Model):
    def __str__(self):
        return self.testo
    Cod_Cont=models.AutoField(primary_key=True)
    testo=models.CharField(max_length=500)
    titolo=models.CharField(max_length=50,default="")
    data=models.DateTimeField(auto_now_add=True)
    approvato=models.IntegerField()
    estrazioni=models.IntegerField()
    Cod_Utente = models.ForeignKey(Utente, on_delete=models.CASCADE)
    Cod_Cate=models.ForeignKey(Categoria, on_delete=models.CASCADE)
    

class Sessione(models.Model):
    def __str__(self):
        return self.Cod_Sessio
    Cod_Sessio=models.CharField(max_length=20,primary_key=True)
    ip=models.CharField(max_length=20,default="")
    timestamp_post=models.IntegerField()
    timestamp_commento=models.IntegerField(default=0)
    Cod_Utente = models.ForeignKey(Utente, on_delete=models.CASCADE)

class Like(models.Model):
    def __str__(self):
        return str(self.Cod_Like)
    Cod_Like=models.AutoField(primary_key=True)
    Cod_Utente = models.ForeignKey(Utente, on_delete=models.CASCADE)
    Cod_Cont = models.ForeignKey(Contenuto, on_delete=models.CASCADE)

class Commento(models.Model):
    def __str__(self):
        return self.testo
    Cod_Com=models.AutoField(primary_key=True)
    testo=models.CharField(max_length=500)
    data=models.DateTimeField(auto_now_add=True)
    Cod_Utente = models.ForeignKey(Utente, on_delete=models.CASCADE)
    Cod_Cont = models.ForeignKey(Contenuto, on_delete=models.CASCADE)

class Giorno(models.Model):
    def __str__(self):
        return str(self.data)
    Cod_Estrazione=models.AutoField(primary_key=True)
    data=models.DateTimeField(auto_now_add=True)
    Cod_Cont = models.ForeignKey(Contenuto, on_delete=models.CASCADE)