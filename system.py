import string
import pandas as pd
from fuzzywuzzy import fuzz
import numpy as np



def getRelevantData():                                                      #funkcija koja pretvara raw csv fajl u fajl sa svim potrebnim podacima
    print("Започињем одређивање матрице коначних података...")              #takodje, racuna se popularnost i prosecna ocena
    popularity=getRatings('rating.csv')
    
    movies=pd.read_csv('maingenre.csv')                                   #df maingenre sadrzi editovanu matricu zanrova, algoritam pravi df sa kolonama svih zanrova
                                                                        #i puni element matrice 1 ako film pripada tom zanru 
    titles=pd.read_csv("movie.csv")

    relevance=movies
    popularity=popularity.reset_index(drop=True)                        #resetujemo indeks

    relevance['popularityScore']=0                                      #inicijalizacija kolone popularnosti, stavljena na 0
    
    relevance.index=relevance['movieId']                                #stavljamo obe matrice da imaju indeks movieId kako bismo ih uskladili da mogu medjusobno
    popularity.index=popularity['movieId']                              #da razmene elemente po redosledu koji odgovara
    
    relevance['popularityScore']=popularity['frequency']                #popularityScore->zapravo broj ljudi koji je ocenio odredjeni film
    relevance['ratingScore']=popularity['rating']                       #ratingsScore->prosecna ocena svakog filma
    popularity=popularity.reset_index(drop=True)                        #vracamo kolonu indeksa na regularne 0--->n indekse
    relevance=relevance.reset_index(drop=True)                          #takodje i ovde
    relevance['title']=titles['title']                                              #imena filmova...
    relevance['ratingScore'] = relevance['ratingScore'].fillna(0)                       #svi filmovi koji nemaju ni jednu ocenu dobice ocenu 0, kako ne bismo imalo
    relevance['popularityScore'] = relevance['popularityScore'].fillna(0)                       #NaN vrednosti u df
    relevance=relevance.drop(['(no genres listed)'], axis=1)                                #postoje filmovi koji imaju kao zanr vrednost no g.r., to nam nije potrebno
    relevance.to_csv('relevantData.csv')                                                        #pravimo csv gde imamo sve neophodne obradjene podatke
    print("Одређивање матрице коначних података завршено!")
    #relevance=relevance.sort_values(by=['popularityScore'],ascending=False)                      
    
def getRatings(ratings_path):                                                           #u ovoj funkciji racunamo rejtinge i popularnost svakog filma
    print("Започињем филтрирање по популарности...")
    df=pd.read_csv(ratings_path) 
    ratingsData=df[df.columns[0:len(df.columns)-1]]                                     #izbacujemo timestamp kolonu, nije relevantna za nas algoritam
    popularity=pd.DataFrame()

    popularity['frequency']=(ratingsData['movieId'].value_counts())                     #brojimo koliko puta je koji film ocenjen redom
    popularity=popularity.sort_index()                                                  #sortiramo indekse redom
    
    popularity['movieId']=popularity.index;                                             #posto indeksi imaju vrednosti id svakog filma, mozemo da ih sacuvamo ovako
                                                                                        #los nacin, stvara se indeks 0 ali kasnije ispravljeno
    means=pd.DataFrame()
    means['rating'] = ratingsData.groupby(['movieId'])['rating'].mean()                     #grupisemo po movieId i racunamo prosecan rating za svaki
    
    popularity['rating']=means['rating']                                                        #pakujemo rating-e
    
    movieDf=pd.read_csv('movie.csv')
    popularity=popularity.reset_index(drop=True)                                            #reset indeksa, nepotrebno doduse
    popularity['title']=movieDf['title']                                                    #...
    popularity=popularity.sort_values(by=['frequency'],ascending=False)                       #opadajuce po broju ljudi koji su ocenili film
    popularity.to_csv('ratingsFiltered.csv') 
    
    print("Филтрирање по популарности завршено!")
    
    return popularity
   
    
def getMovies(movies_path):                                     #ova funkcija obradjuje matricu zanrova i vraca u formi koja nam je potrebna
    
    print("Започињем одређивање матрице сличности...")
    
    df = pd.read_csv(movies_path)
    
    genres=df['genres'].str.split('|',expand=True)                  #prvo splitujemo zanrove svakog filma u niz po "|"
    movies=df['title']
    movieIds=df['movieId']
    movieData = pd.DataFrame(columns=['movieId','title'])           
    
    movieData['movieId']=movieIds               #ovde dodati i zanrove
    movieData['title']=movies
    
                        #ovde izvukao sve unique zanrove
    tmp=""                                                          #string koji ce da cuva sve unique zanrove koje kasnije treba rasporediti kao kolone u novom df
    final="movieId "                                #zadnja kolona
    for col in genres:
                                                                                         #ovo broji posebne vrednost iz svake kolone, stavi u neki array ili string
        for element in genres[col].unique():                                            #i onda opet nadji unique vrednosti
           if element is not None:                                                          #desava se da neki film ima none zanr, ili jednostavno prazan element
               if element != '(no genres listed)':                                          #kao i ovo, moze se resiti pomocu fillna(genre) ali ovo je zanimljiviji pristup
                    tmp+=element+" "
    tempArray=tmp.split()                                                               #kada splitujemo konacni niz zanrova imamo sve potrebne kolone
     
    genres['movieId']=df["movieId"]
     
     
    for el in np.unique(tempArray):                                     #moguce je da se neka vrednost u tempArr ponavlja, jer jedna vrednost moze biti unique u vise kolona
        final+=el+" "
    genreArray=final.split()             #provera                       ovaj niz definitivno sadrzi samo unique zanrove
    genreData = pd.DataFrame(columns=genreArray)                        #lako napravimo novi df mogocu genreArray
    
    genreData['movieId']=df['movieId']

    progress=0
    for col in genres:                                              #idemo kolonu po kolonu 
        ind=0
        #i=genres.loc[genres['movieId'],'movieId']
        print("Читам базу података:",round(progress/len(genres.columns)*100),"%")
        progress+=1
        for element in genres[col]:                                             #genres sadrzi zanrove svih filmova, string
            i=genres.loc[ind,'movieId']                                         #lociramo movieId koji odgovara movieId-ju

            if element is not None and isinstance(element,str):             #ako je neki element genres zapravo kolona u genreData dodaj 1 kod njega

                genreData.loc[genreData['movieId'] == i, element] = 1       #idemo redom po elementima svake kolone i proveravamo da li string zanrova filma sadrzi dati zanr

            ind+=1                                                          #pomeramo indeks kad zavrsimo sa jednim filmom
    
    genreData=genreData.fillna(0)                           #nepraktican algoritam, postoji bolji nacin uradjen za 'TAG' deo programa. Ovaj nacin uradjen cisto radi eksperimentacije
                                                        #sa pandas Dataframe-om i resavanja problema iterativno. Svaki pandas problem se moze resiti bez iterativnog algoritma
    
    
    mixedData = genreData[genreData.columns[1:len(genreData.columns)-1]]    #dodaj rowove sem id-ja
    #mixedData.index=genreData['movieId']
    mixedData=mixedData.dot(mixedData.T)                                    #nalazimo slicnost svakog filma sa svakim, najbitniji deo ove sekcije
    mixedData['movieId']=genreData['movieId']                       #umesto tradicionalnog pristupa nalazenja rastojanja izmedju elemenata df, moj predlog resenja je sledeci:
                                                                #srediti elemente genre da imaju vrednosti Boolean, 1->film ima taj zanr,0->film nema taj zanr,
    genreData.to_csv('maingenre.csv',index=False)               #nakon toga uraditi prostu a.dot(a.T) kako bismo nasli odnos svakog filma sa svakim drugim
                                                                #rezultat je ogroman dataframe sa 790M elemenata, koji je tesko zapisati, ali sadrzi SVE potrebne podatke
    #mixedData.to_csv('genrelikeliness.csv',index=False)        na osnovu kojih mozemo doneti zakljucak da li je film dobar za predlog korisniku
    
    return mixedData                                            #genredata cuvamo kao matricu koju cemo koristiti kasnije dok mixedData vracamo
     
     

     
def getUserPref():                                              #jednostavna funkcija za UI u terminalu
    pd.set_option("display.max_colwidth", None)                 #ako stavimo da je ograniceno, cut-ujemo stringove imena filmova i imamo problem u programu arr->(str1)==df->(str2)==false
    pd.set_option('display.max_rows', None)                     #omoguciti siri prikaz
    
    print("Да ли желите да ажурирате матрицу релевантности? (Y)/(било шта друго)")
    y=input()
    if y.lower()=='y':                                                  #upit u slucaju da postoje nove informacije 
        getRelevantData()
    print("Читам матрицу релевантности...")
    relevance=pd.read_csv('relevantData.csv',index_col=[0]) 
    

    relevance=relevance.drop(index=0)                                           
    relevance=relevance.sort_values(by=['popularityScore'],ascending=False)     #korisniku prikazujemo samo filmove za koje su najvece sanse da ih moze oceniti
    relevance=relevance.reset_index(drop=True)                                  #postavljamo da je ovo default izgled tj. resetujemo indekse da pokazuju mostpop,...,leastpop
    

    bl=True
    ctr=0
    user=pd.DataFrame(columns=["movieId","rating"])
    
    while bl:                                                                   #petlja za user input
        for thing in range(len(relevance)):
            temp=relevance.loc[relevance.index==thing,'title']                  #thing je fakticki svaki indeks pojedinacno iz relevance, da bi korisnik ocenjivao jedan po jedan 
            print("(1-5 | било шта друго ако нисте гледали овај филм)")         #film
            print(temp.to_string(index=False))                                  #.to_string()->resava problem konverzije--->df->(temp)==index,temp,-||-.to_string(i=F)=='temp'
            
            i=1
            while(i==1):
                ocena=int(input())
                if ocena>0 and ocena<6:                                         #provera za korisnicki unos
                    i=0
                else:
                    continue    
            #idm=relevance.loc[relevance['title']==temp.to_string(index=False),'movieId'].to_string(index=False)
            idm=relevance.loc[relevance.index==thing,'movieId'].to_string(index=False)              #gore objasnjeno, ovo vraca id ocenjenog filma
            row={'movieId': idm,'rating': ocena}
            user=user.append(row, ignore_index = True)                                              #dodajemo novi row u user df
            ctr+=1
            
            if ctr%5==0:                                                                        #nakon svakog petog filma pitamo korisnika da li zeli da ocenjuje jos
                print("Да ли желите оцените још филмова? (Y)/(било шта друго)")
                z=input()
                if z.lower()!='y':
                    bl=False
                    break
    
    user.to_csv('userPreferred.csv',index=False)                                    #cuvamo korisnicki unos
    
    
def getSimilarMoviesByGenre():                                      #finalna funkcija za odredjivanje content-based slicnosti
    likeliness=getMovies(movies_path="movie.csv")                   #slicnost svakog filma sa svakim

    
    getUserPref()                                                   #unos...
    user=pd.read_csv('userPreferred.csv')
    user=user.sort_values(by=['rating'],ascending=False)                        #sortiramo po rejtingu korisnika, filmovi koji imaju ocenu 5 su filmovi cije slicne trazimo
    favourite=user.loc[user.index==0,'movieId'].to_string(index=False)          #prvi film ocenjen sa 5, nepotreban string 
    #print(favourite)
    mostRated=pd.DataFrame()
    mostRated['movieId']=user.loc[user['rating']==5,'movieId']                  #ako ocena 5 dodaj
    mostRated=mostRated.reset_index(drop=True)                                  #kada izvucemo samo 5-ice resetujemo df

    arrayOfRated=mostRated['movieId'].to_numpy()                                #niz omiljenih filmova zarad iteracija nad njima

    favourite=int(favourite)
    recommended=pd.DataFrame()
    for element in arrayOfRated:                                            
        item=likeliness.loc[likeliness['movieId']==int(element)]            #proveravamo za svaki film iz likeliness da li je njegov id jednak nekom od omiljenih 
        recommended=recommended.append(item, ignore_index = True)           #ako jeste dodajemo u recommend

    tempDf=pd.read_csv('maingenre.csv')
    tempId=recommended['movieId']
    recommended=recommended.drop(['movieId'], axis=1)                       #brisemo movieId kolonu kako bismo promenili kolone recommended

    recommended.columns=tempDf['movieId']                                   #izmena kolona da predstavljaju odnos omiljenih filmova sa svim ostalim
    recommended['movieId']=tempId                                           #postoji dosta brze resenje, ali zarad razumevanja algoritma i objasnjavanja korak po korak uradjeno ovako
    #recommended.columns =recommended.columns+1
    

    relevance=pd.read_csv('relevantData.csv')

    recommended.index=arrayOfRated
    recommended=recommended.T                                               #transponujemo recommended, sada imena kolona su id-jevi omiljenih,a indeksi id-jevi ostalih filmova
    
    
    #recommended['popularityScore']=relevance['popularityScore']
    for element in arrayOfRated:                                            
        recommended=recommended.drop(int(element), axis=0)           #brisemo indekse(movieId) koji su isti kao neki od omiljenih, jer ne zelimo da vidimo odnos filma sa samim sobom
        

    recommended['movieId']=recommended.index                        #nova kolona movieId da bismo cuvali id-jeve ostalih filmova
    recommended=recommended.reset_index(drop=True)                  #reset indeksa

    maxSimilarity=pd.DataFrame()
    similarity=pd.DataFrame()
    
    x=int(input("Колико сличних филмова желите?"))                  #petlja za racunanje najvece slicnosti, resenje preko .max() identicno ili preko loc where max, ali samo 1 film na prikazu
    recommended.index=recommended['movieId']
    for el in recommended.columns:
        if el!='movieId' and el!='popularityScore':                 #ignorisemo ove kolone jer nam ne treba max za njih
            maxSimilarity=recommended.nlargest(x+1,el)                          #random bug koji radi??? NE DIRATI  tesko za objasniti...
            similarity=similarity.append(maxSimilarity[el], ignore_index=True)      #max x elemenata za odredjeni film se prebacuje u similarity
 
    similarity = similarity.fillna(-1)                                           #sva prazna polja u redovima inicijalizujemo sa -1 jer ona nisu relevantna za odredjeni film
    similarity=similarity.astype('int32')               #castujemo u int kako nam slicnost ne bi bila flaot
    helper=0
    rc=0
    idArr=np.zeros((len(similarity),x ))                #niz koji ce sadrzati najslicnije filmove tj. id-jeve
    #similarity['movieId']=arrayOfRated
    for index, row in similarity.iterrows():            #niz po niz...
        print("Креирање матрице сличних филмова...")
        helper=0
        counter=0
        for element in row:                                                 #za svaki element u redu...
            if element!=-1 and (not isinstance(row.index[helper], str)):    #ako je relevantan i nije string(gore smo castovali sve potrebne u int)
                idArr[rc][counter]=int(row.index[helper])                   #dodajemo u matricu
                counter+=1
            helper+=1
        rc+=1
    print("Креирање матрице сличних филмова завршено!")

    relevant=pd.read_csv('ratingsFiltered.csv',index_col=0)

    relevant=relevant.sort_index()                                  #ratingsFiltered je sortiran po popularnosti, vracamo u index-sorted kako bi lakse 'uporedili'
                                                                    #sa neobradjenim df movieDf
    movieDf=pd.read_csv('movie.csv')
    movieDf['popularity']=relevant['frequency']                         #dodajemo kolonu popularnosti
    movieDf['average_score']=round(relevant['rating'],2)                #takodje i kolonu rejtinga cije vrednosti zaokruzujemo na dve decimale
    
    print("Филмови слични по жанру филмовима које сте означили да Вам се највише свиђају:")
    for i in range(len(idArr)):
        print("=============================================================================================================")
        print(movieDf.loc[movieDf['movieId']==int(arrayOfRated[i])],":")
        print("=============================================================================================================")
        for j in range(len(idArr[0])):
            print(movieDf.loc[movieDf['movieId']==idArr[i][j]])     #trazimo po nizu (i=const)[j++] id-jeve, uz pomoc kojih print-ujemo...
            print("-------------------------------------------------------------------------------------------------------------")



def getMostPopular():
    pd.set_option('display.max_rows', 500) #vraca najpopularnije filmove, popularity-based recommendation
    pd.set_option('display.max_columns', 5)
    pd.set_option("display.max_colwidth", None)
    output=pd.read_csv('ratingsFiltered.csv',index_col=0)
    genres=pd.read_csv('movie.csv')
    output['genres']=genres['genres']
    output['rating']=round(output['rating'],2)
    x=int(input('Колико најгледанијих филмова желите да видите?'))
    print(output.head(x))
    

def getChoices():                         #da korisnik ima opciju da mu se prikaze odredjeni zanr sortiran da odredjeni nacin

    x=int(input("(1)  Најпопуларнији...\n(било који други број)  Најбоље оцењени..."))   
    z=True
    choices=['','Action','Adventure','Animation','Children','Comedy','Crime','Documentary','Drama','Fantasy','Horror','Mystery','Romance','Sci-Fi','Thriller','War','Western']
    while(z): 
        y=int(input("(1)  Акциони\n(2)  Авантуристички\n(3)  Анимирани\n(4)  Дечији\n(5)  Комедија\n(6)  Крими\n(7)  Документарац\n(8)  Драма\n(9)  Фантастика\n(0)  Наредна страна..."))
        if(y==0):
            y=int(input("\n(10)  Хорор\n(11)  Мистерија\n(12)  Романтични\n(13)  Научна фантастика\n(14)  Трилер\n(15)  Ратни\n(16)  Каубојски\n(20)  Наредна страна..."))
        else:
            z=False
        if(y!=20):
            z=False         #dodaj da mozes sam da biras sort i type!
            
    type=choices[y]
    
    movieDf=pd.read_csv('relevantData.csv',index_col=0)
    
    spec=movieDf.loc[movieDf[type]==1]
    
    if x==1:
        spec=spec.sort_values(by=['popularityScore'],ascending=False) 
    else:
        m = spec['popularityScore'].quantile(0.75)                #ova linija trazi vrednost popularityScore vecu od 75% svih vrednosti, tj. uz pomoc ovoga odvajamo samo 25% najpopularnijih filmova 
        spec=spec.loc[spec['popularityScore']>=m]                 #vraca top 25% najpopularnijih filmova
        spec=spec.sort_values(by=['ratingScore'],ascending=False)   #sortiramo po ocenama
        
    spec['ratingScore']=round(spec['ratingScore'],2)                                    #zaokruzimo rejting...
    print("Постоји ",len(spec.index)," филмова који спадају у дати критеријум.")
    qu=int(input("Колико филмова желите приказати?..."))
    print(spec.head(qu))
    
    
    
def IMDBeq(x):                                  #u ovoj funkciji primenjujemo IMDBeq formulu za rejting filmova
    v = x['popularityScore']
    R = x['ratingScore']
    m = x['popularityScore'].quantile(0.90)
    C = x['ratingScore'].mean()
    
    return (v/(v+m) * R) + (m/(m+v) * C)
    
    
def getIMDBScoreSorted():
    pd.set_option('display.max_rows', 500)
    dfMovie=pd.read_csv('relevantData.csv',index_col=0)

    C = dfMovie['ratingScore'].mean()
    m = dfMovie['popularityScore'].quantile(0.90)
    dfMovie = dfMovie.loc[dfMovie['popularityScore'] >= m]
    
    
    dfMovie['IMDBScore']=IMDBeq(dfMovie)

    dfMovie = dfMovie.sort_values('IMDBScore', ascending=False)                     #prikazujemo top 'broj' filmova po IMDB oceni
    broj=int(input("Унети број филмова које желите да вам се прикажу..."))
    print(dfMovie.head(broj))
    
    
def getSimilarByTag():                                                     #ova funkcija je za nalazenje slicnih filmova po tagovima korisnika
    pd.set_option('display.max_rows', 500)
    tags=pd.read_csv('tag.csv')
    tags=tags.sort_values(by=['movieId'],ascending=True)

    getUserPref()
    user=pd.read_csv('userPreferred.csv')
    
    idm=user.loc[user['rating']==5,'movieId']
    idm=idm.to_numpy()                                              #izdvajamo filmove ocenjene sa 5...
    #novo
    tags['Status']=tags['movieId'].isin(idm)                        #status oznacava filmove koji su ocenjeni sa 5

    tagged=tags.loc[tags['Status'],'tag']
    taggedArray=tagged.to_numpy()                                   #niz tagova kod kojih je status==True, tj. filmova koji su najvecom ocenom ocenjeni od strane korisnika
           #novo
    tags['isSimilar']=tags['tag'].isin(taggedArray)                 #True ako se tag filma poklapa sa bilo kojim tagom prothodno ocenjenih filmova
    final=tags.groupby(['movieId'])['isSimilar'].sum()              #sabiramo koliko slicnih tagova svaki film ima sa -||-
    final=final.sort_values(ascending=False)                        #sortiramo seriju tako da je film sa najvise tagova prikazan prvi

    final=final.drop(final.loc[final.index.isin(idm)].index)     #posto ce svaki prethodno ocenjeni da ima najvise slicnih tagova sam sa sobom, moramo ih eliminisati
    
    x=int(input("Колико сличних филмова по ознака желите да видите?..."))
    recommend=final.head(x)
    rec=pd.DataFrame()                  #series--->dataframe
    rec['movieId']=recommend.index
    rec['value']=recommend.values
    stuff=pd.read_csv('movie.csv')
    
    stuff['recommendable']=stuff['movieId'].isin(rec['movieId'])                #ako movieId postoji u rec znaci da se treba preporuciti
    #stuff['recommendableScore']=rec.loc[rec['movieId'].isin(stuff['movieId']),'value']  #recommendable score je zapravo broj slicnih tagova
    stuff=stuff.loc[stuff['recommendable']==True]                                           #uzmemo samo filmove koji su za preporuku
    new_df = stuff.merge(rec[["movieId","value"]], on="movieId", how="left")                #spojimo matricu preporucljivih sa matricom koja sadrzi score svakog filma
    new_df["recommendableScore"] = new_df["value"].fillna(0)                                #ako nema ni jedan slican tag sa nacim filmom punimo sa 0
    new_df=new_df.drop(columns=['value'])                                           #value kolona nam je sada nepotrebna 
    
    movies=pd.read_csv('ratingsFiltered.csv',index_col=0)
    
    movies.index=movies['movieId']                                          #menjamo indeks kako bismo lakse stavili vrednosti iz movies u new_df
    new_df.index=new_df['movieId']
    
    new_df['rating']=movies['rating']                                       #lakse uz merge, ali smo vec zamenili indekse i slozili vrednosti gde treba da budu
    new_df['popularity']=movies['frequency']
    new_df=new_df.reset_index(drop=True)
    
    new_df=new_df.sort_values(by=['recommendableScore'],ascending=False)        #od prvog najpreporucljivijeg do 'x'-tog 
    print("\n\n\nФилмови налик онима који Вам се свиђају, на основу корисничких ознака")
    print("=============================================================================================================")
    print(new_df)           
    print("=============================================================================================================")


def stringIsSimilar(element,s2):
    s1=str(element['tag'])
    if fuzz.ratio(s1, s2)>0.75:
        return True
    else:
        return False


def getMoviesByTagInput():                                                                              #funkcija za pretragu filmova slicnih po tagu
    print("Унесите неку карактеристичну реч за филм-име глумца, режисера, мотив филма...")
    q=str(input(" нпр: 007, marvel, scary, horror, plot twist, Quentin Tarantino, Leonardo DiCaprio..."))

    tagDf=pd.read_csv('tag.csv')
    moviesDf=pd.read_csv('movie.csv')
    #tagDf['worthy'] = tagDf.apply(lambda x: stringIsSimilar(tagDf,q), axis=1)
    tagDf=tagDf.loc[tagDf['tag'].str.lower()==q.lower()]                                        #kastujemo u lowercase pa proveravamo i menjamo tagDf
    tagDf=tagDf.sort_values(by='movieId',ascending=True)                                        #sortiramo po movieId-ju
    tagDf=tagDf.groupby(['movieId'])['tag'].count()                                             #koliko se puta pojavljuje prethodno uneseni tag ce predstavljati Score
    #tagDf=tagDf.sort_values(ascending=False)
    print("Нађено ",len(tagDf.index)," филмова са датом ознаком")
    x=int(input("Колико таквих филмова желите да прикажете?..."))
                              
    printable=moviesDf.loc[moviesDf['movieId'].isin(tagDf.index)]                               #novi df koji ce imati vrednosti iz neobradjenog csv fajla movie.csv ali samo
    printable.index=printable['movieId']                                                        #id-jeve koji se nalaze u tagDf
    printable['tagScore']=tagDf.values                                                          #gornja linija, menjamo indeks sa movieId kako bismo uporedili tagDf i printable
    printable=printable.reset_index(drop=True)                                                  #vracamo indeks
    printable=printable.sort_values('tagScore',ascending=False)                             
    print(printable.head(x))
    
def main():
    t=True
    while(t):
        print("(1)  Прикажи најгледајније филмове\n(2)  Оцени филмове и прикажи најсличније по жанру\n(3)  Оцени филмове и прикажи најсличније по ознакама корисника\n(4)  Слободан избор параметара и сортирања\n(5)  Применити IMDB формулу за рецензију филмова и приказати IMDB топ листу\n(6)  Унесите кључну реч и на основу ње пронађите филм\n(0)  Излаз из програма")
        choice=int(input())
        if choice==2:
            getSimilarMoviesByGenre()
        elif choice==1:
            getMostPopular()
        elif choice==3:
            getSimilarByTag()
        elif choice==4:
            getChoices()       
        elif choice==5:
            getIMDBScoreSorted()
        elif choice==6:
            getMoviesByTagInput()
        elif choice==0:
            t=False
        else:
            print("Унесите валидан избор!")
            continue
if __name__ == '__main__':                                              
    main()