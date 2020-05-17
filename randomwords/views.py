from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import datetime
from django.db.models import Q
from django.urls import resolve
import hashlib
import secrets
import time
import random

from .forms import Registrazione, Login, Pubblica, Approva, Cerca, Commentoform
from .models import Utente, Contenuto, Like, Sessione, Commento, Categoria, Giorno

# Create your views here.


def cookies(request):
    if request.COOKIES.get('sessione'):
        cookies=request.COOKIES.get('sessione')
        query=Sessione.objects.filter(Cod_Sessio=cookies)
        if len(query)==0:
            return -1
        if query[0].Cod_Utente.nickname=="Anonimo":
            return 0
        elif query[0].Cod_Utente.permesso==0:
            return 1
        elif query[0].Cod_Utente.permesso==1:
            return 2
        elif query[0].Cod_Utente.permesso==2:
            return 3
    else:
        return 0


def logout(request):
    if request.COOKIES.get('sessione'):
        cookies=request.COOKIES.get('sessione')
        query=Sessione.objects.filter(Cod_Sessio=cookies)
        a=Utente.objects.filter(nickname="Anonimo")
        agg=query[0]
        agg.Cod_Utente=a[0]
        agg.save()
        messages.success(request, 'Logout effettuato correttamente!')
    return redirect('/')


def sceltecategorie():
    scelte=[]
    query=Categoria.objects.all()
    i=0
    for i in range(len(query)):
        if query[i].nomecategoria!="Nessuna":
            info = {
                "id": str(query[i].Cod_Cate),
                "nome": query[i].nomecategoria,
            }
            scelte.append(info)

    return scelte
        

def listeindex(query,limite,request,login):
    recenti=[]
    i=0
    for i in range(len(query)):
        conta=Like.objects.filter(Cod_Cont=query[i])
        if query[i].Cod_Utente.nickname!="Anonimo":
            link="/profilo/"+str(query[i].Cod_Utente.Cod_Utente)+"/1"
            booleanlink=True
        else:
            link=""
            booleanlink=False
        ap=True
        if query[i].approvato==1:
            ap=False 

        like=True
        likelink=""
        if login==True:
            cooki=request.COOKIES.get('sessione')
            queryc=Sessione.objects.filter(Cod_Sessio=cooki)
            utente=queryc[0].Cod_Utente
            cerca=Like.objects.filter(Cod_Utente=utente,Cod_Cont=query[i])
            if len(cerca)==0:
                like=True
                likelink="/like/"+str(query[i].Cod_Cont)+"/0"
            else:
                like=False
                likelink="/like/"+str(query[i].Cod_Cont)+"/1"

        info = {
            "titolo": query[i].titolo,
            "autore": query[i].Cod_Utente.nickname,
            "frase": query[i].testo,
            "data": str(query[i].data.day)+"/"+str(query[i].data.month)+"/"+str(query[i].data.year),
            "categoria": "("+query[i].Cod_Cate.nomecategoria+")",
            "commenta": "/contenuto/"+str(query[i].Cod_Cont),
            "like": str(len(conta)),
            "autorelink": link,
            "booleanlink": booleanlink,
            "approvato": ap,
            "likeb": like,
            "likelink": likelink
        }
        recenti.append(info)
        if i>=limite:
            break
    
    return recenti


def estrazione(request,login):
    cerca=Giorno.objects.all()
    i=0
    check=0
    for i in range(len(cerca)):
        if cerca[i].data.date()==datetime.datetime.now().date():
            estratto=cerca[i].Cod_Cont
            check=1
            break
    if check==0:
        query=Contenuto.objects.filter(approvato=1).order_by("estrazioni")
        estratto=query[0]
        a=Giorno(Cod_Cont=estratto)
        a.save()
        estratto.estrazioni=estratto.estrazioni+1
        estratto.save()

    dare=listeindex([estratto],2,request,login)
    return dare[0]



def index(request):

    b=cookies(request)
    if b==0:
        login=False
        op=False
    elif b==1:
        login=True
        op=False
    elif (b==2) or (b==3):
        login=True
        op=True
    elif b==-1:
        response=render(request, 'index.html',{'login': False,'op':False})
        response.set_cookie(key='sessione',value='a',max_age=0)
        return response

    estratta=estrazione(request,login)

    query=Contenuto.objects.order_by('-data') \
        .filter(approvato=1)

    scelte=sceltecategorie()

    recenti=listeindex(query,2,request,login)

    l=Like.objects.all()
    c=Contenuto.objects.filter(approvato=1).order_by('-data')
    conto=[]
    contenuti=[]
    i=0
    for i in range(len(c)):
        cont=0
        j=0
        for j in range(len(l)):
            if l[j].Cod_Cont.Cod_Cont==c[i].Cod_Cont:
                cont=cont+1
        conto.append(cont)
        contenuti.append(c[i])
    #print(conto)
    j=0
    for j in range(len(conto)-1):
        i=0
        for i in range(len(conto)-1):
            if conto[i]<conto[i+1]:
                conto[i], conto[i+1]=conto[i+1], conto[i]
                contenuti[i], contenuti[i+1]=contenuti[i+1], contenuti[i]
    #print(conto)
    piulike=listeindex(contenuti,2,request,login)


    return render(request, 'index.html',{'login': login,'op':op,'recenti':recenti,'piulike':piulike,'scelte':scelte,'estratta':estratta})

def cerca(request):
    form = Cerca(request.POST)
    if (form.is_valid()):
        testo=form.cleaned_data['testo']
        categoria=form.cleaned_data['categoria']

        parametro=testo+"-"+str(categoria)
    else:
        print(form.errors)
        return redirect("/")

    return redirect("/pagina/"+parametro+"/1")

def pagina(request,parametro,page):

    b=cookies(request)
    if b==0:
        login=False
        op=False
    elif b==1:
        login=True
        op=False
    elif (b==2) or (b==3):
        login=True
        op=True
    elif b==-1:
        return redirect("/")

    scelte=sceltecategorie()

    testocerca=False

    if "-" in parametro:
        a=parametro.split("-")
        if (a[1]=="100") or (a[1]==""):
            query=Contenuto.objects.order_by('-data') \
            .filter(Q(testo__contains=a[0]) | Q(titolo__contains=a[0]))
            if a[0]!="":
                testocerca="Cerca '"+a[0]+"'"
            else:
                return redirect("/pagina/recenti/1")
        else:
            qu=Contenuto.objects.order_by('-data') \
            .filter(Q(testo__contains=a[0]) | Q(titolo__contains=a[0]))
            query=[]
            i=0
            for i in range(len(qu)):
                if int(qu[i].Cod_Cate.Cod_Cate)==int(a[1]):
                    query.append(qu[i])
            nomecate=Categoria.objects.get(Cod_Cate=int(a[1])).nomecategoria
            if a[0]!="":
                testocerca="Cerca '"+a[0]+"', Categoria: "+nomecate
            else:
                testocerca="Cerca Categoria: "+nomecate

        contenuti=listeindex(query,99999,request,login)
        titolo="Ricerca"
    elif parametro=="recenti":
        query=Contenuto.objects.order_by('-data') \
        .filter(approvato=1)

        contenuti=listeindex(query,99999,request,login)
        titolo="Recenti"
    elif parametro=="piulike":
        l=Like.objects.all()
        c=Contenuto.objects.filter(approvato=1).order_by('-data')
        conto=[]
        contenuti=[]
        i=0
        for i in range(len(c)):
            cont=0
            j=0
            for j in range(len(l)):
                if l[j].Cod_Cont.Cod_Cont==c[i].Cod_Cont:
                    cont=cont+1
            conto.append(cont)
            contenuti.append(c[i])
        #print(conto)
        j=0
        for j in range(len(conto)-1):
            i=0
            for i in range(len(conto)-1):
                if conto[i]<conto[i+1]:
                    conto[i], conto[i+1]=conto[i+1], conto[i]
                    contenuti[i], contenuti[i+1]=contenuti[i+1], contenuti[i]
        #print(conto)
        contenuti=listeindex(contenuti,9999,request,login)
        titolo="Più Like"
    else:
        return redirect("/")

    if len(contenuti)==0:
        messages.success(request, 'La ricerca non ha portato risultati')
        return redirect("/")

    pagina=(len(contenuti)//10)
    if (len(contenuti)%10)!=0:
        pagina=pagina+1
    i=0
    check=0
    listapag=[]
    for i in range(pagina):
        if (i+1)==page:
            attuale=True
            check=1
        else:
            attuale=False
        info = {
            "pag": str(i+1),
            "attuale": attuale
        }
        listapag.append(info)

    if check==0:
        return redirect("/pagina/"+parametro+"/1")
    
    if int(page)==int(listapag[0]['pag']):
        inizio=False
    else:
        inizio=str(page-1)

    if int(page)==int(listapag[len(listapag)-1]['pag']):
        fine=False
    else:
        fine=str(page+1)

    contenuti=contenuti[(page-1)*10:((page*10))]

    return render(request, 'pagina.html',{'login': login,'op':op,'contenuti':contenuti,'titolo':titolo,'listapag':listapag,'inizio':inizio,'fine':fine,'parametro':parametro,'scelte':scelte,'testocerca':testocerca})


def like(request,cod,p):
    try:
        pre=request.META['HTTP_REFERER']
    except:
        return redirect("/")

    query2=Contenuto.objects.filter(Cod_Cont=cod)
    b=cookies(request)
    if (b<=0) or (len(query2)==0):
        print("VIA")
        return redirect(pre)

    cooki=request.COOKIES.get('sessione')
    query=Sessione.objects.filter(Cod_Sessio=cooki)
    utente=query[0].Cod_Utente

    if p==0:
        query3=Like.objects.filter(Cod_Utente=utente,Cod_Cont=cod)
        print("INIZIO")
        if len(query3)==0:
            cont=query2[0]
            a=Like(Cod_Utente=utente,Cod_Cont=cont)
            a.save()
            print("OKOKOK")
    else:
        query3=Like.objects.filter(Cod_Utente=utente,Cod_Cont=cod)
        if len(query3)!=0:
            a=query3[0]
            a.delete()
    
    return redirect(pre)
        


def contenuto(request,cod):
    b=cookies(request)
    if b==0:
        login=False
        op=False
    elif b==1:
        login=True
        op=False
    elif (b==2) or (b==3):
        login=True
        op=True
    elif b==-1:
        return redirect("/")

    try:
        pre=request.META['HTTP_REFERER']
        if pre==request.build_absolute_uri():
            pre=False
    except:
        pre=False

    forminvio=Commento()

    scelte=sceltecategorie()

    query=Contenuto.objects.filter(Cod_Cont=int(cod))

    conte=listeindex(query,2,request,login)[0]

    admin=False
    if login==True:
        cooki=request.COOKIES.get('sessione')
        utente=Sessione.objects.filter(Cod_Sessio=cooki)[0].Cod_Utente
        if utente.permesso==2:
            admin=True

    if (request.method == 'POST'):
        if 'delete' in request.POST.keys():
            print(request.POST['delete'])
            a=Commento.objects.filter(Cod_Com=int(request.POST['delete']))[0]
            if login==True:
                cooki=request.COOKIES.get('sessione')
                utente=Sessione.objects.filter(Cod_Sessio=cooki)[0].Cod_Utente
            if (op==True) or (a.Cod_Utente.Cod_Utente==utente.Cod_Utente):
                a.delete()
        else:
            form = Commentoform(request.POST)
            if (form.is_valid()):
                testo=form.cleaned_data['testo']
                if login==False:
                    messages.success(request, 'Per commentare devi essere autenticato')
                else:
                    check=0
                    cooki=request.COOKIES.get('sessione')
                    query=Sessione.objects.filter(Cod_Sessio=cooki)
                    tempo=query[0].timestamp_commento
                    calc=int(time.time())-tempo
                    minuti=int(int(calc)/60)
                    print(minuti)
                    if minuti<2:
                        messages.success(request, 'Puoi inviare un commento al minuto!')
                        check=1

                    if check==0:
                        post=Contenuto.objects.filter(Cod_Cont=int(cod))[0]
                        cooki=request.COOKIES.get('sessione')
                        utente=Sessione.objects.filter(Cod_Sessio=cooki)[0].Cod_Utente

                        s=Commento(testo=testo,Cod_Utente=utente,Cod_Cont=post)
                        s.save()
                        a=Sessione.objects.filter(Cod_Sessio=cooki)[0]
                        timestamp=time.time()
                        a.timestamp_commento=int(timestamp)
                        a.save()
            else:
                messages.success(request, 'Inserisci il testo del commento')

    query=Commento.objects.filter(Cod_Cont=int(cod)).order_by('-data')
    commenti=[]

    i=0
    for i in range(len(query)):
        booleandel=False
        if login==True:
            cooki=request.COOKIES.get('sessione')
            utente=Sessione.objects.filter(Cod_Sessio=cooki)[0].Cod_Utente
            if (query[i].Cod_Utente.Cod_Utente==utente.Cod_Utente) or (op==True):
                booleandel=True
            
        info = {
            "autore": query[i].Cod_Utente.nickname,
            "testo": query[i].testo,
            "data": str(query[i].data.day)+"/"+str(query[i].data.month)+"/"+str(query[i].data.year),
            "autorelink": "/profilo/"+str(query[i].Cod_Utente.Cod_Utente)+"/1",
            "booleandel": booleandel,
            "delname": str(query[i].Cod_Com)
        }
        commenti.append(info)


    return render(request, 'contenuto.html',{'login': login,'op':op,'form':forminvio,'scelte':scelte,'conte':conte,'commenti':commenti,'pre':pre})
    


def profilo(request,codice,page):
    b=cookies(request)
    if b==0:
        login=False
        op=False
    elif b==1:
        login=True
        op=False
    elif (b==2) or (b==3):
        login=True
        op=True
    elif b==-1:
        return redirect("/")

    scelte=sceltecategorie()

    try:
        pre=request.META['HTTP_REFERER']
        if pre==request.build_absolute_uri():
            pre=False
    except:
        pre=False

    query=Utente.objects.filter(Cod_Utente=int(codice))

    if query[0].permesso==0:
        pex="Utente"
    elif query[0].permesso==1:
        pex="Moderatore"
    else:
        pex="Admin"

    if query[0].descrizione=="":
        desc="(Non impostata)"
    else:
        desc=query[0].descrizione
    
    utente = {
            "nickname": query[0].nickname,
            "email": query[0].email,
            "ruolo": pex,
            "descrizione": desc,
        }

    proprio=False
    if login==True:
        cooki=request.COOKIES.get('sessione')
        query=Sessione.objects.filter(Cod_Sessio=cooki)
        if query[0].Cod_Utente.Cod_Utente==int(codice):
            proprio=True

    if proprio==True:
        query=Contenuto.objects.order_by('-data')
    else:
        query=Contenuto.objects.order_by('-data') \
        .filter(approvato=1)

    i=0
    lista=[]
    for i in range(len(query)):
        if query[i].Cod_Utente.Cod_Utente==int(codice):    
            lista.append(query[i])

    contenuti=listeindex(lista,99999,request,login)

    pagina=(len(contenuti)//10)
    if (len(contenuti)%10)!=0:
        pagina=pagina+1
    i=0
    check=0
    listapag=[]
    for i in range(pagina):
        if (i+1)==page:
            attuale=True
            check=1
        else:
            attuale=False
        info = {
            "pag": str(i+1),
            "attuale": attuale
        }
        listapag.append(info)

    if (check==0) and (len(listapag)!=0):
        return redirect("/profilo/"+str(codice)+"/1")


    if len(listapag)==0:
        pieno=False
        inizio=False
        fine=False
    else:
        pieno=True
        if int(page)==int(listapag[0]['pag']):
            inizio=False
        else:
            inizio=str(page-1)

        if int(page)==int(listapag[len(listapag)-1]['pag']):
            fine=False
        else:
            fine=str(page+1)

    contenuti=contenuti[(page-1)*10:((page*10))]


    return render(request, 'profilo.html',{'login': login,'op':op,'scelte':scelte,'contenuti':contenuti,'utente':utente,'proprio':proprio,'inizio':inizio,'fine':fine,'parametro':str(codice),'listapag':listapag,'pieno':pieno,'pre':pre})

def mioprofilo(request):
    if request.COOKIES.get('sessione'):
        cookies=request.COOKIES.get('sessione')
        query=Sessione.objects.filter(Cod_Sessio=cookies)
        if (len(query)==0) or (query[0].Cod_Utente.nickname=="Anonimo"):
            return redirect("/")

        codice=query[0].Cod_Utente.Cod_Utente
        return redirect("/profilo/"+str(codice)+"/1/")
    else:
        return redirect("/")

def approva(request):
    if request.COOKIES.get('sessione'):
        cook=request.COOKIES.get('sessione')
        query=Sessione.objects.filter(Cod_Sessio=cook)
        if query[0].Cod_Utente.nickname=="Anonimo":
            return redirect("/")
        elif query[0].Cod_Utente.permesso==0:
            return redirect("/")
    else:
        redirect("/")

    forminvio=Approva()

    b=cookies(request)
    if b==0:
        login=False
        op=False
    elif b==1:
        login=True
        op=False
    elif (b==2) or (b==3):
        login=True
        op=True
    elif b==-1:
        return redirect("/")

    
    scelte=[]
    query=Categoria.objects.all()
    i=0
    for i in range(len(query)):
        if query[i].nomecategoria!="Nessuna":
            info = {
                "id": str(query[i].Cod_Cate),
                "nome": query[i].nomecategoria,
            }
            scelte.append(info)

    if request.method == 'POST':
        form = Approva(request.POST)
        if (form.is_valid()):
            cate=form.cleaned_data['cate']
            p=request.POST.keys()
            if 'approva' in request.POST:
                if int(form.cleaned_data['cate'])!=-1:
                    id=int(request.POST['approva'])
                    cercacate=Categoria.objects.filter(Cod_Cate=int(cate))
                    query=Contenuto.objects.filter(Cod_Cont=id)
                    a=query[0]
                    a.approvato=1
                    a.Cod_Cate=cercacate[0]
                    a.save()
                else:
                    messages.success(request, 'Seleziona la categoria')
            else:
                id=int(request.POST['rifiuta'])
                query=Contenuto.objects.filter(Cod_Cont=id)[0]
                query.delete()
        else:
            messages.success(request, 'Seleziona la categoria')

    query=Contenuto.objects.filter(approvato=0)
    frasi=[]
    i=0
    for i in range(len(query)):
        info = {
            "id": str(query[i].Cod_Cont),
            "titolo": query[i].titolo,
            "autore": query[i].Cod_Utente.nickname,
            "frase":  query[i].testo,
        }
        frasi.append(info)

    return render(request, 'approva.html',{'form':forminvio,'login':login,'op': op,'frasi':frasi,'scelte':scelte})


def pubblica(request):
    forminvio=Pubblica()

    b=cookies(request)
    if b==0:
        login=False
        op=False
    elif b==1:
        login=True
        op=False
    elif (b==2) or (b==3):
        login=True
        op=True
    elif b==-1:
        return redirect("/")

    scelte=sceltecategorie()

    if request.COOKIES.get('sessione'):
        c=request.COOKIES.get('sessione')
        query=Sessione.objects.filter(Cod_Sessio=c)
        if query[0].Cod_Utente.nickname=="Anonimo":
            nome=False
        else:
            nome=query[0].Cod_Utente.nickname

        tempo=query[0].timestamp_post
        calc=int(time.time())-tempo
        minuti=int(int(calc)/60)
        if minuti<30:
            messages.success(request, 'Puoi inviare una frase ogni 30 minuti! Mancano '+str(30-minuti)+' minuti.')
            scadenza=True
        else:
            scadenza=False        
    else:
        nome=False
        scadenza=False

    if (request.method == 'POST') and (scadenza==False):
        check=0 #per controllare se ha il cookies così dopo gli viene messo con il timestamp
        form = Pubblica(request.POST)
        if form.is_valid():
            contenuto=form.cleaned_data['contenuto']
            titolo=form.cleaned_data['titolo']
            autore=int(form.cleaned_data['autore'])
            if request.COOKIES.get('sessione'):
                if autore==1:
                    utente=query[0].Cod_Utente
                else:
                    cerca=Utente.objects.filter(nickname="Anonimo")
                    utente=cerca[0]
            else:
                query=Utente.objects.filter(nickname="Anonimo")
                utente=query[0]
                check=1 #per controllare se ha il cookies così dopo gli viene messo con il timestamp

            q=Categoria.objects.filter(nomecategoria="Nessuna")
            cate=q[0]
            s=Contenuto(testo=contenuto,titolo=titolo,approvato=0,estrazioni=0,Cod_Cate=cate,Cod_Utente=utente)
            s.save()

            timestamp=time.time()
            if check==0:
                c=request.COOKIES.get('sessione')
                query=Sessione.objects.filter(Cod_Sessio=c)
                a=query[0]
                a.timestamp_post=int(timestamp)
                a.save()
                messages.success(request, 'Contenuto inviato correttamente!')
                return redirect('/')
            else:
                while True:
                    cod=secrets.token_hex(8)
                    query=Sessione.objects.filter(Cod_Sessio=cod)
                    if len(query)==0:
                        break
                query=Utente.objects.filter(nickname="Anonimo")
                utente=query[0]
                s=Sessione(Cod_Sessio=cod,timestamp_post=int(timestamp),Cod_Utente=utente,timestamp_commento=0)
                s.save()
                messages.success(request, 'Contenuto inviato correttamente!')
                response=redirect('/')
                response.set_cookie(key='sessione',value=cod,max_age=365*24*60*60)
                return response
        else:
            messages.success(request, 'Inserisci tutti i campi richiesti')

    return render(request, 'pubblica.html',{'form': forminvio,'login':login,'op':op,'nome':nome,'scadenza':scadenza,'scelte':scelte})

def login(request):

    if cookies(request)!=0:
        return redirect('/')

    scelte=sceltecategorie()

    forminvio=Login()
    if request.method == 'POST':
        form = Login(request.POST)
        if form.is_valid():
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            p=hashlib.sha256(password.encode()).hexdigest()
            query = Utente.objects.filter( password=p ) & Utente.objects.filter( email=email )
            if len(query)!=1:
                messages.success(request, 'Email o password errati')
                return render(request, 'login.html', {'form': forminvio})
            codiceutente=query[0]
            if request.COOKIES.get('sessione'):
                c=request.COOKIES.get('sessione')
                query=Sessione.objects.filter(Cod_Sessio=c)
                a=query[0]
                a.Cod_Utente=codiceutente
                a.save()
                messages.success(request, 'Login effettuato correttamente!')
                return redirect('/')
            else:
                while True:
                    cod=secrets.token_hex(8)
                    query=Sessione.objects.filter(Cod_Sessio=cod)
                    if len(query)==0:
                        break
                s=Sessione(Cod_Sessio=cod,timestamp_post=0,Cod_Utente=codiceutente,timestamp_commento=0)
                s.save()
                messages.success(request, 'Login effettuato correttamente!')
                response=redirect('/')
                response.set_cookie(key='sessione',value=cod,max_age=365*24*60*60)
                return response

        else:
            messages.success(request, 'Inserisci tutti i campi richiesti')
            return render(request, 'login.html', {'form': forminvio})
        return render(request, 'login.html', {'form': forminvio})
    else:
        return render(request, 'login.html', {'form': forminvio,'scelte':scelte})

def registrati(request):

    if cookies(request)!=0:
        return redirect('/')

    scelte=sceltecategorie()

    forminvio=Registrazione()
    if request.method == 'POST':
        form = Registrazione(request.POST)
        if form.is_valid():
            email=form.cleaned_data['email']
            nickname=form.cleaned_data['nickname']
            password=form.cleaned_data['password']
            confermapassword=form.cleaned_data['confermapassword']
            
            if password!=confermapassword:
                messages.success(request, 'Password e Confermapassword devono essere uguali')
                return render(request, 'registrati.html', {'form': forminvio})
            elif len(password)<4:
                messages.success(request, 'La password deve essere di minimo 4 caratteri')
                return render(request, 'registrati.html', {'form': forminvio})
            else:
                query = Utente.objects.filter( nickname=nickname ) | Utente.objects.filter( email=email )
                if len(query)!=0:
                    messages.success(request, 'Email o nickname già in uso')
                    return render(request, 'registrati.html', {'form': forminvio})

                p=hashlib.sha256(password.encode()).hexdigest()
                u=Utente(nickname=nickname,email=email,password=p,permesso=0)
                u.save()
                messages.success(request, 'Registrazione effettuata, ora puoi fare il login!')
                return redirect('login')
        else:
            messages.success(request, 'Inserisci tutti i campi richiesti')
            return render(request, 'registrati.html', {'form': forminvio})

    else:
        return render(request, 'registrati.html', {'form': forminvio,'scelte':scelte})

