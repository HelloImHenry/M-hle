import tkinter
import math
import copy



import time

minmaxSuchtiefe = 0


spielfeld = [
[0,3,3,2,3,3,0],
[3,0,3,2,3,0,3],
[3,3,0,0,0,3,3],
[0,1,0,3,1,1,0],
[3,3,0,0,0,3,3],
[3,2,3,1,3,0,3],
[0,3,3,0,3,3,0]
]
sizeX,sizeY = 400,400

gameStateArray = [0,0]
platzierteFiguren = [3,3]
spielerAmZug = 1

ersterClick = True
geklickteErstePosition = []

minmaxZug = []

SPIELER = 1
KI = 2

root = tkinter.Tk()
root.geometry("400x400")
canvas = tkinter.Canvas(root,width = sizeX, height = sizeY, bg = "blue")
canvas.pack()

offset = 50


#Das Array in dem alle Dreierkombinationen gespeichert sind
dreierKombinationen = []
#Erstellt ein Array in dem alle Horizontalen Dreierkombinationen enthalten sind und returnt es
def generiereHorizontaleDreierKombinationen():


    leeresSpielfeld = [
    [0,3,3,0,3,3,0],
    [3,0,3,0,3,0,3],
    [3,3,0,0,0,3,3],
    [0,0,0,3,0,0,0],
    [3,3,0,0,0,3,3],
    [3,0,3,0,3,0,3],
    [0,3,3,0,3,3,0]
    ]
    Hcombinations = []
    currentCombination = []
    for y in range(7):
        for x in range(7):
            if leeresSpielfeld[y][x] == 0:
                currentCombination.append([y,x])
            print(len(currentCombination))
            if len(currentCombination) == 3:
                Hcombinations.append(copy.deepcopy(currentCombination))
                currentCombination.clear()
    return Hcombinations
#Testet ob eine gegebene Figur in einer dreierKombination ist.
def testeObInDreierKombination(position):
    #print("____________________")
    global spielfeld
    global dreierKombinationen
    #print("Das Feld hat eine: " + str(spielfeld[position[0]][position[1]]))
    ausgabe = False
    for x in dreierKombinationen:
        if str(position) in str(x):
            fehlerInDreierKombination = False
            for z in range(len(x)):
                #print(str(spielfeld[x[z][0]][x[z][1]]), " | ", spielfeld[position[0]][position[1]])
                if spielfeld[x[z][0]][x[z][1]] != spielfeld[position[0]][position[1]]:
                    fehlerInDreierKombination = True
                    #print(str(x))
            if fehlerInDreierKombination == False:
                ausgabe = True
                #print(str(x))
                break

    return ausgabe
#Erstellt ein Array in dem alle Vertikalen Dreierkombinationen enthalten sind und returnt es
def generiereVertikaleDreierKombinationen():
    leeresSpielfeld = [
    [0,3,3,0,3,3,0],
    [3,0,3,0,3,0,3],
    [3,3,0,0,0,3,3],
    [0,0,0,3,0,0,0],
    [3,3,0,0,0,3,3],
    [3,0,3,0,3,0,3],
    [0,3,3,0,3,3,0]
    ]
    Vcombinations = []
    for x in range(7):
        currentCombination = []
        for y in range(7):
            if leeresSpielfeld[y][x] == 0:
                currentCombination.append([y,x])
            if len(currentCombination) == 3:
                Vcombinations.append(copy.deepcopy(currentCombination))
                currentCombination.clear()
    return Vcombinations
#Erstellt ein Array in dem alle Dreierkombinationen enthalten sind.
def generiereDreierKombinationen():
    global dreierKombinationen
    combinationsHorizontal = generiereHorizontaleDreierKombinationen()
    combinationsVertical = generiereVertikaleDreierKombinationen()
    dreierKombinationen.extend(combinationsHorizontal)
    dreierKombinationen.extend(combinationsVertical)
    for x in dreierKombinationen:
        #print(str(x))
        pass
    #print("_____________________________________________")

#Gibt ALLE Spielfelder zurück die die Angegebene ID besitzen
def erhalteALLEFelderMitID(id):
    global spielfeld
    felder = []
    for y in range(7):
        for x in range(7):
            if spielfeld[y][x] == id:
                felder.append([y,x])
    return felder
#Gibt die Spielfelder einer ID zurück die in keiner Mühle verbaut sind
def erhalteFelderMitIDDieNICHTInMühleSind(id):
    figurenDieInKeinerMühleSind = []
    if id == 0:
        print("FEHLER! Die angegebene ID darf nicht 0 sein, da 0 keinem Spieler gehört und daher in keiner Mühle sein kann [erhalteFelderMitIDDieNICHTInMühleSind]")
    else:
        spielfigurenDesSpielers = erhalteALLEFelderMitID(id)
        for x in range(len(spielfigurenDesSpielers)):
            if testeObInDreierKombination(spielfigurenDesSpielers[x]) == False:
                figurenDieInKeinerMühleSind.append(spielfigurenDesSpielers[x])
    return figurenDieInKeinerMühleSind

#Alle Felder mit der ID 0 werden Returnt
def erhalteFreiePositionenGameState1():
    felder =  erhalteALLEFelderMitID(0)


def PlatziereFigur(position, spieler):
    global platzierteFiguren
    global spielfeld
    spielfeld[position[0]][position[1]] = spieler
    platzierteFiguren[(spieler-1)] +=1
    zeichneSpielfeld()


def erhalteBenachbarteFreieFelder(startFeld):
    global spielfeld
    #In dem Array werden die Freien Felder gespeichert.
    benachbarteFreieFelder = []
    #Wir vergrößern die Y Koodrinate also muss startFelf[1] konstant bleiben
    for y1 in range(1,6):
        #Test ob nächster Zug im erlaubten Spielfeld ist
        if (y1+ startFeld[0]) < 7:
            #print(str(y1), "," , str(startFeld[1]))
            #Die 3 Reihe muss immer gesondert betrachtet werden, da diese über die MITTE DES Spielfelds geht.
            if startFeld[1] == 3 and startFeld[0] <3 and (startFeld[0] + y1) >3:
                break
            #Das Feld ist frei und wird hinzugefügt
            if spielfeld[(startFeld[0]+y1)][startFeld[1]] == 0:
                benachbarteFreieFelder.append([(y1+startFeld[0]),startFeld[1]])
                break
            #Das Feld ist nicht frei. Die Schleife wird abgegrochen
            elif spielfeld[(startFeld[0]+y1)][startFeld[1]] == 1 or spielfeld[(startFeld[0]+y1)][startFeld[1]] == 2:
                break
    #print(str(benachbarteFreieFelder))
    #Wir verkleinern die Y Koodrinate also muss startFelf[1] konstant bleiben
    for y2 in range(1,6):
        #Test ob nächster Zug im erlaubten Spielfeld ist
        if (startFeld[0] - y2) >= 0:

            #Die 3 Reihe muss immer gesondert betrachtet werden, da diese über die MITTE DES Spielfelds geht.
            if startFeld[1] == 3 and startFeld[0] >3 and (startFeld[0] - y2) <3:
                break

            if spielfeld[(startFeld[0]-y2)][startFeld[1]] == 0:
                benachbarteFreieFelder.append([(startFeld[0]-y2),startFeld[1]])
                break
            elif spielfeld[(startFeld[0]-y2)][startFeld[1]] == 1 or spielfeld[(startFeld[0]-y2)][startFeld[1]] == 2:
                break
    #print(str(benachbarteFreieFelder))
    #Wir vergrößern die X Koodrinate also muss startFelf[0] konstant bleiben
    for x1 in range(1,6):
        #Test ob nächster Zug im erlaubten Spielfeld ist
        if (x1 + startFeld[1]) < 7:
            #Die 3 Reihe muss immer gesondert betrachtet werden, da diese über die MITTE DES Spielfelds geht.
            if startFeld[0] == 3 and startFeld[1] <3 and (startFeld[1] + x1) >3:
                break
            if spielfeld[startFeld[0]][(startFeld[1] + x1)] == 0:
                benachbarteFreieFelder.append([startFeld[0],(startFeld[1]+x1)])
                break
            elif spielfeld[startFeld[0]][(startFeld[1]+x1)] == 1 or spielfeld[startFeld[0]][(startFeld[1]+x1)] == 2:
                break
    #print(str(benachbarteFreieFelder))
    #Wir verkleinern die X Koodrinate also muss startFelf[0] konstant bleiben
    for x2 in range(1,6):
        #Test ob nächster Zug im erlaubten Spielfeld ist
        if (startFeld[1]-x2) >= 0:

            #Die 3 Reihe muss immer gesondert betrachtet werden, da diese über die MITTE DES Spielfelds geht.
            if startFeld[0] == 3 and startFeld[1] >3 and (startFeld[1] - x2) <3:
                break

            if spielfeld[startFeld[0]][(startFeld[1] - x2)] == 0:

                benachbarteFreieFelder.append([startFeld[0],(startFeld[1]-x2)])
                break
            elif spielfeld[startFeld[0]][(startFeld[1]-x2)] == 1 or spielfeld[startFeld[0]][(startFeld[1]-x2)] == 2:
                break
    #print(str(benachbarteFreieFelder))
    return benachbarteFreieFelder
def erhalteGeclicktesFeld(mousePosition):
    global offset
    global canvas
    global sizeX
    global sizeY
    feld = [99,99]
    feldXStep = (sizeX-(2*offset))/6
    feldYStep = (sizeY-(2*offset))/6
    for y in range(7):
        for x in range(7):
            posY = feldYStep*y + offset
            posX = feldXStep*x + offset
            entfernung = math.sqrt((posX-mousePosition[0])**2+(posY-mousePosition[1])**2)
            
            if entfernung <= 20:
                #Hier ist es x,y da die erste Koordinate ja immer y sein soll und die 2 x. Daher ist das hier evrtauscht damit dass einheitlich im Programm bleibt.
                feld = [x,y]
                #print(str(entfernung))
    return feld
startTime = 0
def wechsleSpieler():
    global startTime
    global minmaxZug
    global gameStateArray
    startTime = time.time()
    #Die Originalfunktion ist in Mühle2.py. Die hier ist abgeändert um Zeitsuche zu ermöglichen
    ermittleBestenZug(7)
    print(str(minmaxZug))
    if gameStateArray[(KI-1)] == 0:

        PlatziereFigur(minmaxZug[1], KI)
    else:
        BewegeFigur(minmaxZug[0], minmaxZug[1])
    if platzierteFiguren[(KI-1)] == 9:
        gameStateArray[(KI-1)] +=1
    print(str(minmaxZug))
    print("GenerierungsZeit:", str(time.time()-startTime))


def BewegeFigur(altePos, neuePos):
    global spielfeld
    spielfeld[neuePos[0]][neuePos[1]] = spielfeld[altePos[0]][altePos[1]]
    spielfeld[altePos[0]][altePos[1]] = 0
    zeichneSpielfeld()

def andererSpieler():
    global spielerAmZug
    ausgabe = 0
    if spielerAmZug == 1:
        ausgabe = 2
    else:
        ausgabe = 1

    if ausgabe == 0:
        print("Fehler es ist kein Spieler am Zug wie geht das?!")
    return ausgabe

def KlaueFigur(position):
    global spielfeld
    global gameStateArray
    spielfeld[position[0]][position[1]] = 0
    if gameStateArray[(andererSpieler()-1)] == 1 and len(erhalteALLEFelderMitID(andererSpieler())) ==3:
        gameStateArray[(andererSpieler()-1)] = 2
    if gameStateArray[(andererSpieler()-1)] == 2 and len(erhalteALLEFelderMitID(andererSpieler())) <3:
        print("Spieler 1 hat gewonnen!")
    print("Derzeitige gamestates:",str(gameStateArray))
    print("Anzahl der Figuren:", str(len(erhalteALLEFelderMitID(andererSpieler()))))
    print("Anzahl der Figuren:", str(len(erhalteALLEFelderMitID(andererSpieler()))))
    zeichneSpielfeld()



def click(event):
    global gameStateArray
    global geklickteErstePosition
    global ersterClick
    global platzierteFiguren
    global spielerAmZug
    posY = event.y
    posX = event.x
    geclicktesFeld =erhalteGeclicktesFeld([posY,posX])
    #print(str(gameStateArray))

    """
    Hier kommt die Gamestateaktualisierung um in die Sprungphase zu kommen.
    Ebenfalls findet hier die Prüfung darauf statt, ob das Spiel beendet ist.
    """
    #Test ob Spieler in 2 Phase kommen soll
    if gameStateArray[(spielerAmZug-1)] == 1 and erhalteALLEFelderMitID(spielerAmZug) == 3:
        gameStateArray[(spielerAmZug-1)] = 2
    #Test ob Spiel gewonnen da Spieler am Zug nur noch 2 figuren und andererSpieler noch mehr als 3 Figuren
    elif gameStateArray[(spielerAmZug-1)] == 2 and len(erhalteALLEFelderMitID(spielerAmZug)) <3:
        print("Spieler 2 hat gewonnen!")
    #Beide Spieler sind in Phase 2 also unentschieden
    elif gameStateArray[(spielerAmZug-1)] == 2 and gameStateArray[(andererSpieler()-1)] == 2:
        print("Unentschieden!")

    
    print(str(geclicktesFeld))
    #Gamestate 0 entspricht der Setzphase. In der Phase platziert der SPieler einfach nur Figuren auf auf freien feldern
    if gameStateArray[(spielerAmZug-1)] == 0:
        #Alle leeren Felder werden ermittelt
        leereFelder = erhalteALLEFelderMitID(0)
        #Es wird getestet ob es sich bei dem angeclickten Feld um ein Freies feld handelt.
        if geclicktesFeld in leereFelder:
            #Falls ja wird eine Figur platziert, die anzahl der platzierten Figuren erhöht (da bei 9 platzierten Figuren der gamestate gewechselt wird)
            PlatziereFigur(geclicktesFeld, spielerAmZug)
            #platzierteFiguren[(spielerAmZug-1)] +=1
            #Hier findet der Test statt, ob der Gamestate für den Spieler gewechselt werden sollte.
            if platzierteFiguren[((spielerAmZug-1))] == 9:
                gameStateArray[((spielerAmZug-1))] +=1
            #Auch in der Satzphase ist es möglich Mühlen zu erstellen um Figuren des gegners zu klauen.
            #Hier findet der Test statt, ob die neue Figur zu einer neuen Mühle führt
            if testeObInDreierKombination(geclicktesFeld) == True:
                #Falls ja dann wird das gamestate um 0.5 erhöht. Ein Gamestate mit 0.5 entspriht dem Figur klauen state.
                gameStateArray[(spielerAmZug-1)] +=0.5
                print("Klaue Figur...")
            else:
                wechsleSpieler()
    #Gamestate 0 entspricht der Zugphase. Der Spieler kann Figuren auf anliegende FREIE Felder bewegen.
    elif gameStateArray[(spielerAmZug-1)] == 1:
        #Der Click der die Figur auswählt die bewegt werden soll
        if ersterClick == True:
            spielerPositionen = erhalteALLEFelderMitID(spielerAmZug)
            if geclicktesFeld in spielerPositionen:

                geklickteErstePosition = geclicktesFeld
                print("Eine deiner Spielfiguren wurde angeclickt.")
                ersterClick = False
            else:
                print("Du kannst keine Figur deines Gegners auswählen du trottel")
        #Der Click der den Ort auswählt an den die Figur hinbewegt werden soll
        else:
            #Die Benachbarten freien felder werden zurückgegeben
            nachbarFelder = erhalteBenachbarteFreieFelder(geklickteErstePosition)
            #Test ob das angeclickte Feld ein möglicher Zug ist
            if geclicktesFeld in nachbarFelder:
                #Die Figur wird bewegt.
                BewegeFigur(geklickteErstePosition, geclicktesFeld)
                #Es wird getestet ob eine Mühle entsteht. Falls ja dann wird das gamestate um 0.5 erhöht. Ein Gamestate mit 0.5 entspriht dem Figur klauen state.
                if testeObInDreierKombination(geclicktesFeld) == True:
                    gameStateArray[((spielerAmZug-1))] +=0.5
                else:
                    wechsleSpieler()
                ersterClick = True
                print("Zug ausgeführt.")
            #Falls das angeclickte Feld kein möglicher Zug ist / das heißt es ist nicht frei
            else:
                #Der erste click wird als nächstes genommen. Das heißt das die startfigur neu gewählt wird.
                ersterClick = True
    elif gameStateArray[(spielerAmZug-1)] == 2:
        #Der Spieler wählt die Zu bewegende Figur aus
        if ersterClick == True:
            spielerPositionen = erhalteALLEFelderMitID(spielerAmZug)
            if geclicktesFeld in spielerPositionen:
                print("Ausgewählt")
                geklickteErstePosition = geclicktesFeld
                ersterClick = False
        #Der Spieler wählt die Zielposition aus.
        else:
            #In der Sprungphase darf die Figur auf alle freien Felder springen. Das heißt, dass jedes Freie feld auf dem Spielfeld ein mögliches ist.
            freiePositionen = erhalteALLEFelderMitID(0)
            #Es wird getestet ob das geclickte 2 feld ein freies Feld ist.
            if str(geclicktesFeld) in str(freiePositionen):
                #Die Figur wird bewegt.
                print("Figur bewegt")
                BewegeFigur(geklickteErstePosition, geclicktesFeld)
                #Es wird getestet ob eine Mühle entsteht. Falls ja dann wird das gamestate um 0.5 erhöht. Ein Gamestate mit 0.5 entspriht dem Figur klauen state.
                #Der Spieleramzug wird in diesem Fall noch nicht gewechselt, da der Spieler ja noch eine Figur klauen darf.
                if testeObInDreierKombination(geclicktesFeld) == True:
                    gameStateArray[(spielerAmZug-1)] += 0.5
                #Falls die neue Position der bewegten Figur in keiner Mühle ist dann wird einfach nur der Spieler am Zug gewechselt.
                else:
                    wechsleSpieler()
                ersterClick = True
            #Falls das angeclickte Feld kein möglicher Zug ist / das heißt es ist nicht frei
            else:
                #Der Startposition wird neu genommen. Das heißt das die startfigur neu gewählt wird.
                ersterClick = True
    
    #Die Klauphase
    elif ".5" in str(gameStateArray[(spielerAmZug-1)]):
        print("Versuche Figur zu klauen...")

        #Eine Liste mit allen feldern die in keiner Mühle sind wird erstellt.
        felderDieKlaubarSind = erhalteFelderMitIDDieNICHTInMühleSind(andererSpieler())
        #Es wird geprüft ob die Liste mit klaubaren feldern = 0 ist. Fals ja dann bedeutet das, dass sich alle Figuren des Gegners in Mühlen bedinfen.
        #In diesem Fall darf der Spieler auch Figuren aus Mühlen klauen
        if len(felderDieKlaubarSind) == 0:
            print("Nur Figuren in Mühlen übrig")
            #Die Liste wird neu gesetzt. Nun enthällt sie ALLE Figuren des Gegners. Auch die in Mühöen. Der Grund ist wir obig beschrieben.
            felderDieKlaubarSind = erhalteALLEFelderMitID(andererSpieler())
        print("Klaubare Felder:", str(felderDieKlaubarSind))
        if geclicktesFeld in felderDieKlaubarSind:
            print("Klau erfolgreich!")
            KlaueFigur(geclicktesFeld)
            #Nachdem die Figur nun geklaut wurde wird der Gamestate wieder um 0.5 verringert und nochmal zum int konvertiert
            gameStateArray[(spielerAmZug-1)] -=0.5
            gameStateArray[(spielerAmZug-1)] = int(gameStateArray[(spielerAmZug-1)])
            #Der Test ob der andere Spieler in den 2 Gamestate kommen soll oder nicht wird ganz oben bereits durchgeführt.
            #Deshalb muss hier nur der spieleramzug geändert werden.
            wechsleSpieler()
        else:
            print("Klau nicht erfolgreich")
    else:
        print("Kein Valider Gamestate")


def ermittleBestenZug(tiefe):
    global minmaxZug
    global minmaxSuchtiefe
    minmaxSuchtiefe = tiefe
    #Nur tum testen
    minmax = max(KI, tiefe, -9000000, +9000000)
    print(str(minmax))

    if str(minmaxZug) == "[]":
        print("Die KI findet keinen Zug.")

#Test ob der Spieler noch mögliche Züge hat. Ergebnis des Tests wird als bool zurückgegeben. True = Er har noch züge, false = er hat keine Mehr
#Eigentlich brauche ich für die gameSTates 0 und 2 keinen Test durchführen weil es IMMER freie felder auf dem Feld gibt aber ich mache es trotzdem um
#einen Test zu machen ob es irgendwo einen fehler gibt.
def hatNochMöglicheZüge(spieler):
    hatKeineMöglichenZügeMehr = False
    if gameStateArray[(spieler-1)] == 0 or gameStateArray[(spieler-1) == 2]:
        züge = erhalteALLEFelderMitID(0)
        if len(züge) != 0:
            hatKeineMöglichenZügeMehr = True
        else:
            print("FEHLER! Es gibt keine Freien Felder mehr xD?")
    elif gameStateArray[(spieler-1)] == 1:
        züge = []
        spielerFiguren = erhalteALLEFelderMitID(spieler)
        for x in range(spielerFiguren):
            züge.extend(erhalteBenachbarteFreieFelder(spielerFiguren[x]))
        if len(züge) != 0:
            hatKeineMöglichenZügeMehr = True
    return hatKeineMöglichenZügeMehr

"""
Die möglichen Züge werden in folgendem Layout gespeichert.

AltePosition, NeuePosition, ZuKlauendePosition

Falls das Spiel sich in der Setzphase befindet ist die alte Position gleich [99,99], da Sie nicht existiert.

Falls keine Mühle durch den Zug gebildet wird, wird der 3 Parameter einfach weggelassen.

"""
def generiereSpieleSituationsabhängigeMöglicheZüge(spieler):
    global gameStateArray
    global spielfeld
    """
    Das Spielfeld wird kopiert.
    Der Grund dafür liegt darin, dass für den Test ob eine 3er Kombination vorliegt die Figur erstmal platziert werden muss.
    Um unnötige Komplikationen vorzubeugen werden die Änderungen an einem unabhängigen Spielfeld durchgeführt.
    Performance tests stehen noch aus :D
    """
    kopiertesSpielfeld = copy.deepcopy(spielfeld)
    möglicheZügeKI = []
    #GameState 0 = Setzphase
    if gameStateArray[(spieler-1)] == 0:
        #In der Setzphase sind alle möglichen Züge einfach die Freien Felder.
        freieFelder = erhalteALLEFelderMitID(0)
        for x in range(len(freieFelder)):
            #platzieren einer Figur an der stelle um zu testen ob eine Neue Mühle entsteht.
            spielfeld[freieFelder[x][0]][freieFelder[x][1]] = spieler
            #Test ob durch Zug neue Mühle entsteht.
            if testeObInDreierKombination(freieFelder[x]) == True:
                #Falls ja wird jegliches geklaute Feld als individuelle Variation gespeichert.
                klaubarePositionen = []
                #Zuerst der Test ob die zu klauende Figur bei bedarf aus der gegnerischen Mühle sein darf. Dieser Fall tritt ein, falls es kein anderes klaubares Feld gibt.
                anzahlDerFigurenAußerhalbVonMühle = len(erhalteFelderMitIDDieNICHTInMühleSind(andererSpielerLokal(spieler)))
                if anzahlDerFigurenAußerhalbVonMühle == 0:
                    klaubarePositionen = erhalteALLEFelderMitID(andererSpielerLokal(spieler))
                elif anzahlDerFigurenAußerhalbVonMühle > 0:
                    klaubarePositionen = erhalteFelderMitIDDieNICHTInMühleSind(andererSpielerLokal(spieler))
                #Nun loopen durch alle Klaubaren Felder um die Variationen zu erzeugen.
                for z in range(len(klaubarePositionen)):
                    #Nun werden die 3 Variablen in das Richtige Format wie oben gegeben gebracht.
                    möglicheZügeKI.append([[99,99], freieFelder[x], klaubarePositionen[z]])
            #Die platzierte Figur führt zu keiner neuen Mühle.
            else:
                möglicheZügeKI.append([[99,99], freieFelder[x]])
            #Entfernen der Figur die zum Mühle-Test genutzt wurde.
            spielfeld[freieFelder[x][0]][freieFelder[x][1]] = 0
    elif gameStateArray[(spieler-1)] == 1:
        spielerPositionen = erhalteALLEFelderMitID(spieler)
        print("SpielerPositionen:",str(spielerPositionen))
        for x in range(len(spielerPositionen)):
            freieBenachbarteFelder = erhalteBenachbarteFreieFelder(spielerPositionen[x])
            print("Die " + str(len(freieBenachbarteFelder)) + " benachbarten Freien felder von " + str(spielerPositionen[x]) + " sind: " + str(freieBenachbarteFelder))
            for z in range(len(freieBenachbarteFelder)):
                print(str(z))
                #platzieren einer Figur an der stelle um zu testen ob eine Neue Mühle entsteht.
                spielfeld[freieBenachbarteFelder[z][0]][freieBenachbarteFelder[z][1]] = spieler
                #Die Startposition wird natürlich auch 0 gesetzt.
                spielfeld[spielerPositionen[x][0]][spielerPositionen[x][1]] = 0
                if testeObInDreierKombination(freieBenachbarteFelder[z]) == True:
                    print("Test-1")
                    #Falls ja wird jegliches geklaute Feld als individuelle Variation gespeichert.
                    klaubarePositionen = []
                    #Zuerst der Test ob die zu klauende Figur bei bedarf aus der gegnerischen Mühle sein darf. Dieser Fall tritt ein, falls es kein anderes klaubares Feld gibt.
                    anzahlDerFigurenAußerhalbVonMühle = len(erhalteFelderMitIDDieNICHTInMühleSind(andererSpielerLokal(spieler)))
                    if anzahlDerFigurenAußerhalbVonMühle == 0:
                        klaubarePositionen = erhalteALLEFelderMitID(andererSpielerLokal(spieler))
                    elif anzahlDerFigurenAußerhalbVonMühle > 0:
                        klaubarePositionen = erhalteFelderMitIDDieNICHTInMühleSind(andererSpielerLokal(spieler))
                    for klaubarePosition in range(len(klaubarePositionen)):
                        print("Test")
                        möglicheZügeKI.append([spielerPositionen[x], freieBenachbarteFelder[z], klaubarePositionen[klaubarePosition]])
                #Die platzierte Figur führt zu keiner neuen Mühle.
                else:
                    print("Test2")
                    möglicheZügeKI.append([spielerPositionen[x], freieBenachbarteFelder[z]])
                #Entfernen der Figur die zum Mühle-Test genutzt wurde.
                spielfeld[freieBenachbarteFelder[z][0]][freieBenachbarteFelder[z][1]] = 0
                #Platzieren der Figur auf der Originalposition
                spielfeld[spielerPositionen[x][0]][spielerPositionen[x][1]] = spieler
    elif gameStateArray[(spieler-1)] == 2:
        spielerPositionenGameState2 = erhalteALLEFelderMitID(spieler)
        for startPosition in range(len(spielerPositionenGameState2)):
            #In der Sprungphase sind alle möglichen Züge einfach die Freien Felder.
            freiePositionen = erhalteALLEFelderMitID(0)
            for endPosition in range(len(freiePositionen)):#
                #platzieren einer Figur an der stelle um zu testen ob eine Neue Mühle entsteht.
                spielfeld[freiePositionen[endPosition][0]][freiePositionen[endPosition][1]] = spieler
                #Test ob dadurch eine Mühle entsteht
                if testeObInDreierKombination(freiePositionen[endPosition]) == True:
                    #Falls ja wird jegliches geklaute Feld als individuelle Variation gespeichert.
                    klaubarePositionen = []
                    #Zuerst der Test ob die zu klauende Figur bei bedarf aus der gegnerischen Mühle sein darf. Dieser Fall tritt ein, falls es kein anderes klaubares Feld gibt.
                    anzahlDerFigurenAußerhalbVonMühle = len(erhalteFelderMitIDDieNICHTInMühleSind(andererSpielerLokal(spieler)))
                    if anzahlDerFigurenAußerhalbVonMühle == 0:
                        klaubarePositionen = erhalteALLEFelderMitID(andererSpielerLokal(spieler))
                    elif anzahlDerFigurenAußerhalbVonMühle > 0:
                        klaubarePositionen = erhalteFelderMitIDDieNICHTInMühleSind(andererSpielerLokal(spieler))
                    
                    for klaubarePosition in range(len(klaubarePositionen)):
                        möglicheZügeKI.append([spielerPositionenGameState2[startPosition], freiePositionen[endPosition], klaubarePositionen[klaubarePosition]])
                #Die Platzierte Figur führt zu keiner neuen Mühle.
                else:
                    möglicheZügeKI.append([spielerPositionenGameState2[startPosition],freiePositionen[endPosition]])
                #Entfernen der Figur die zum Mühle-Test genutzt wurde.
                spielfeld[freiePositionen[endPosition][0]][freiePositionen[endPosition][1]] = 0
    return möglicheZügeKI
speichere = False
def evaluiere():
    global speichere


    global platzierteFiguren
    global spielfeld
    global KI
    global SPIELER
    global gameStateArray
    wert = 0
    if gameStateArray[(KI-1)] == 0:
        wert -= abs(platzierteFiguren[(KI-1)]-len(erhalteALLEFelderMitID(KI)))*1000
        #print(str(wert) + "   |   " + str(spielfeld))
        #print("Platziert:",str(platzierteFiguren[(KI-1)]), "Vorhanden:", str(len(erhalteALLEFelderMitID(KI))))
        anzahlDerFreienFelderGesammt = 0
        kiPositionen = erhalteALLEFelderMitID(KI)
        for x in range(len(kiPositionen)):
            anzahlDerFreienFelderGesammt += len(erhalteBenachbarteFreieFelder(kiPositionen[x]))
        wert += anzahlDerFreienFelderGesammt*0

        wert += abs(platzierteFiguren[SPIELER-1]-len(erhalteALLEFelderMitID(SPIELER)))*0
        if speichere == True:
            f = open("Text.txt", "a")
            f.write("---------------------------------------------------------------------------------------------------------")
            f.write('\n')
            for x in range(7):
                f.write(str(spielfeld[x]))
                f.write('\n')
            f.write(str(wert))
            f.write('\n')
            f.write("---------------------------------------------------------------------------------------------------------")
            f.write('\n')
            f.close()

    return wert
def ermittleBestenZugBeiGegebenerZeit(zeit):
    global minmaxZug
    global minmaxSuchtiefe
    global startTime
    startTime = time.time()
    tiefe = 0
    besterZug = []
    while(abs(time.time()-startTime)< zeit):
        tiefe +=1
        platzhalter = ermittleBestenZug(tiefe)
        besterZug = minmaxZug
        print("Der beste Zug bei der Tiefe", str(tiefe), "ist", str(besterZug)+". Er wurde nach", str(time.time()-startTime)+"Sekunden gefunden.")

    minmaxSuchtiefe = tiefe
    print("Der beste Zug bei der tiefe von:", str(tiefe))

def andererSpielerLokal(spieler):
    anderer = 0
    if spieler == 1:
        anderer = 2
    elif spieler == 2:
        anderer = 1
    
    if anderer == 0:
        print("Fehler in andererSpielerLokal. Es gibt keinen anderen SPieler.")
    return anderer
def macheZug(spieler, zug):
    global spielfeld
    global gameStateArray
    global platzierteFiguren

    #Wenn die len(zug) 3 entspricht, dann hat der Spieler mit diesem zug die Figur eines gegners Geklaut.
    if len(zug) == 3:
        #Die Geklaute Position wird 0 gesetzt.
        spielfeld[zug[2][0]][zug[2][1]] = 0
    #Falls der zug[0][0] 99 entspricht befinden sich das SPiel in der Setzphase. In diesem Fall gäbe es keine Startposition die 0 gesetzt werden muss.
    if zug[0][0] != 99:
        #Ist zug[0][0] nicht 99 so muss das Startfeld 0 gesetzt werden.
        spielfeld[zug[0][0]][zug[0][1]] = 0
    #Die Endposition wird dem Spieler gleichgesetzt. -> Die Figur hat sich bewegt
    spielfeld[zug[1][0]][zug[1][1]] = spieler
    #SPIELER NICHT GEGNER kommt in die Zugphase
    if gameStateArray[(spieler-1)] == 0:
        platzierteFiguren[(spieler-1)] +=1
        if platzierteFiguren[(spieler-1)] == 9:
            gameStateArray[(spieler-1)]+=1
    #Gegner kommt in die Sprungphase
    if gameStateArray[(andererSpielerLokal(spieler)-1)] == 1 and erhalteALLEFelderMitID(andererSpielerLokal(spieler)) == 3:
        gameStateArray[(andererSpielerLokal(spieler)-1)] +=1
    #Gegner hat verloren
    if gameStateArray[(andererSpielerLokal(spieler)-1)] == 2 and erhalteALLEFelderMitID(andererSpielerLokal(spieler)) <3:
        gameStateArray[(andererSpielerLokal(spieler)-1)] +=1

def macheZugRückgängig(spieler, zug):
    global spielfeld
    global gameStateArray
    global platzierteFiguren
    #Die anzahl wird daher gebraucht um festzustellen ob der Spieler vom Gamestate 1 in 0 zurückwechseln soll.
    #Um zu schauen ob der Fall eintritt werden die Anzahl der Spielerfiguren vor und nach dem "zurückmachen" verglichen.
    #Da es keinen zug gibt bei dem der Spieler selber seine anzahl der Figuren verringert ist es nachweisbar das zu dem Zeitpunkt "einfach" weniger Figruen bisher platziert wurden
    anzahlDerSpielerFiguren = len(erhalteALLEFelderMitID(spieler))

    if len(zug) == 3:
        #Die Gegnerische Figur die geklaut wurde, wird wieder platziert
        spielfeld[zug[2][0]][zug[2][1]] = andererSpielerLokal(spieler)
    #Falls der zug[0][0] 99 entspricht befinden sich das SPiel in der Setzphase. In diesem Fall gäbe es keine Startposition die 0 gesetzt werden muss.
    if zug[0][0] != 99:
        #Ist zug[0][0] nicht 99 so muss das Startfeld auf den Spieler gesetzt werden.
        spielfeld[zug[0][0]][zug[0][1]] = spieler
    
    #Die Endposition wird wieder gleich 0 gesetzt, da "zurückbewegt" wird.
    spielfeld[zug[1][0]][zug[1][1]] = 0

    if gameStateArray[(spieler-1)] == 0:
        platzierteFiguren[(spieler-1)] -=1

    #Der Oben beschriebene Fall ist eingetroffen
    if gameStateArray[(spieler-1)] == 1 and anzahlDerSpielerFiguren > (len(erhalteALLEFelderMitID(spieler))):
        platzierteFiguren[(spieler-1)] -=1
        gameStateArray[(spieler-1)] -=1
    
    #Gegner kommt aus der Sprungphase raus
    if gameStateArray[(andererSpielerLokal(spieler)-1)] == 2 and erhalteALLEFelderMitID(andererSpielerLokal(spieler)) >3:
        gameStateArray[(andererSpielerLokal(spieler)-1)] -=1
    #Gegner hat nicht mehr verloren
    if gameStateArray[(andererSpielerLokal(spieler)-1)] == 2 and erhalteALLEFelderMitID(andererSpielerLokal(spieler)) == 3:
        gameStateArray[(andererSpielerLokal(spieler)-1)] -=1

def max(spieler, tiefe, alpha, beta):

    global startTime

    global SPIELER
    global KI
    global minmaxSuchtiefe
    global minmaxZug
    #print("Maximiere...")
    #Der Spieler hat keine möglichen Züge mehr. Die Suche wird abgebrochen.
    if hatNochMöglicheZüge(KI) == False:
        #print("Blatt erreicht. Keine Züge mehr.")
        return evaluiere()
    #Die geforderte Suchtiefe wurde erreicht.
    if tiefe == 0:
        #print("Blatt erreicht. Gewünschte Tiefe.")
        return evaluiere()
    maxWert = alpha
    #print("LulW")
    möglicheZüge = sortiereZüge(generiereSpieleSituationsabhängigeMöglicheZüge(KI))
    #print(str(len(möglicheZüge)), str(möglicheZüge))
    #print("F")
    for x in range(len(möglicheZüge)):
        #Feedback zur Generierung an den Nutzer:
        if tiefe == minmaxSuchtiefe:
            print(str((x/len(möglicheZüge))*100)+"% erledigt. Generiere weiter. Bereits vergangene Zeit: " +str((time.time()-startTime)))


        macheZug(KI,möglicheZüge[x])
        wert = min(SPIELER, (tiefe-1),maxWert, beta)
        macheZugRückgängig(KI,möglicheZüge[x])
        if wert > maxWert:
            maxWert = wert
            if tiefe == minmaxSuchtiefe:
                minmaxZug = möglicheZüge[x]
            if maxWert >= beta:
                break
    return maxWert

def min(spieler, tiefe,alpha,beta):
    global KI
    global SPIELER
    #print("Minimiere...")
    if hatNochMöglicheZüge(SPIELER) == False:
        #print("Blatt erreicht. Keine Züge mehr.")
        return evaluiere()
    if tiefe == 0:
        #print("Blatt erreicht. Gewünschte Tiefe.")
        return evaluiere()
    minWert = beta
    möglicheZüge = sortiereZüge(generiereSpieleSituationsabhängigeMöglicheZüge(SPIELER))
    for z in range(len(möglicheZüge)):
        macheZug(SPIELER,möglicheZüge[z])
        wert = max(KI, (tiefe-1), alpha, minWert)
        macheZugRückgängig(SPIELER,möglicheZüge[z])
        if wert < minWert:
            minWert = wert
            if minWert <= alpha:
                break
    return minWert

generiereDreierKombinationen()


def sortiereZüge(züge):
    zügeSortiert = []

    for x in range(len(züge)):
        zug = züge[x]
        if len(zug) >2:
            zügeSortiert.append(zug)
    for x in range(len(züge)):
        zug = züge[x]
        if len(zug) ==2:
            zügeSortiert.append(zug)

    return zügeSortiert

def zeichneSpielfeld():
    global spielfeld
    feldXStep = (sizeX-(2*offset))/6
    feldYStep = (sizeY-(2*offset))/6
    for y in range(7):
        for x in range(7):
            if spielfeld[y][x] != 3:
                posY = feldYStep*y + offset
                posX = feldXStep*x + offset
                farben = ["#00ff00", "#ff0000", "#00ffff"]
                canvas.create_oval(posX-20,posY-20,posX+20,posY+20,outline = "black", fill = farben[spielfeld[y][x]])

def keyDown(event):
    global dreierKombinationen
    global minmaxZug
    global speichere
    if event.char == 's':
        print("m")
        speichere = True
    else:
        ermittleBestenZug(int(event.char))
        print(str(minmaxZug))

zeichneSpielfeld()
root.bind("<KeyPress>",keyDown)
root.bind("<Button-1>", click)






root.mainloop()