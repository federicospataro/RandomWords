from django import forms
from .models import Categoria

class Registrazione(forms.Form):
    nickname=forms.CharField(label='nickname', max_length=20,required=True)
    email=forms.EmailField(required=True)
    password=forms.CharField(widget=forms.PasswordInput(),required=True)
    confermapassword=forms.CharField(widget=forms.PasswordInput())

class Login(forms.Form):
    email=forms.EmailField(required=True)
    password=forms.CharField(widget=forms.PasswordInput(),required=True)

class Pubblica(forms.Form):
    scelte = (
        (1, 'Roba'),
        (2, 'Anonimo'),
    )

    autore=forms.ChoiceField(choices=scelte,required=True)
    titolo=forms.CharField(label='Titolo',required=True)
    contenuto=forms.CharField(label='Frase',required=True)

class Approva(forms.Form):
    scelte=[]
    query=Categoria.objects.all()
    i=0
    for i in range(len(query)):
        info=[int(query[i].Cod_Cate),query[i].nomecategoria]
        scelte.append(info)
    scelte.append([-1,"-"])

    cate=forms.ChoiceField(choices=scelte,required=True)

class Cerca(forms.Form):

    scelte=[]
    query=Categoria.objects.all()
    i=0
    for i in range(len(query)):
        info=[int(query[i].Cod_Cate),query[i].nomecategoria]
        scelte.append(info)
    scelte.append([100,"Qualunque Categoria"])

    testo=forms.CharField(label='Titolo',required=False)
    categoria=forms.ChoiceField(choices=scelte,required=True)

class Commentoform(forms.Form):
    testo=forms.CharField(label='Testo',required=True,max_length=100)

class Modifica(forms.Form):
    descrizione=forms.CharField(label='descrizione',required=True,max_length=200)
    nickname=forms.CharField(label='descrizione',required=True,max_length=30)
