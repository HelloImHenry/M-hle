from tkinter import *
import multiprocessing
import math
import copy
import time
import queue
from tkinter import font

class Mühle_Funktionen:
    CONST_EMPTY_SPIELFELD = [
                [0,3,3,0,3,3,0],
                [3,0,3,0,3,0,3],
                [3,3,0,0,0,3,3],
                [0,0,0,3,0,0,0],
                [3,3,0,0,0,3,3],
                [3,0,3,0,3,0,3],
                [0,3,3,0,3,3,0]  
    ]
    
    #Erstellt ein Array in dem alle Dreierkombinationen enthalten sind.
    def generiereDreierKombinationen(self):
        dreierKomb = []
        for x in range(7):
            currentCombination = []
            for y in range(7):
                if self.CONST_EMPTY_SPIELFELD[y][x] == 0:
                    currentCombination.append([y,x])
                if len(currentCombination) == 3:
                    dreierKomb.append(copy.deepcopy(currentCombination))
                    currentCombination.clear()
        
        for y in range(7):
            currentCombination = []
            for x in range(7):
                if self.CONST_EMPTY_SPIELFELD[y][x] == 0:
                    currentCombination.append([y,x])
                if len(currentCombination) == 3:
                    dreierKomb.append(copy.deepcopy(currentCombination))
                    currentCombination.clear()
        return dreierKomb


    def erhalteALLEFelderMitID(self, mp_spielfeld,id):
        felder = []
        for y in range(7):
            for x in range(7):
                if mp_spielfeld[y][x] == id:
                    felder.append([y,x])
        return felder
    def andererSpielerLokal(self, spieler):
        anderer = 0
        if spieler == 1:
            anderer = 2
        elif spieler == 2:
            anderer = 1
        
        if anderer == 0:
            pass
        return anderer

    #Testet ob eine gegebene Figur in einer dreierKombination ist.
    def testeObInDreierKombination(self,_spielfeld, position, _dreierKombinationen):
        ausgabe = False
        for x in _dreierKombinationen:
            if str(position) in str(x):
                fehlerInDreierKombination = False
                for z in range(len(x)):
                    if _spielfeld[x[z][0]][x[z][1]] != _spielfeld[position[0]][position[1]]:
                        fehlerInDreierKombination = True
                if fehlerInDreierKombination == False:
                    ausgabe = True
                    break
        return ausgabe

    def erhalteFelderMitIDDieNICHTInMühleSind(self,__spielfeld,id, _dreierKombinationen):
        figurenDieInKeinerMühleSind = []
        if id == 0:
            pass
        else:
            spielfigurenDesSpielers = self.erhalteALLEFelderMitID(__spielfeld, id)
            for x in range(len(spielfigurenDesSpielers)):
                if self.testeObInDreierKombination(__spielfeld,spielfigurenDesSpielers[x], _dreierKombinationen) == False:
                    figurenDieInKeinerMühleSind.append(spielfigurenDesSpielers[x])
        return figurenDieInKeinerMühleSind

    def ermittleKlaubareFelder(self,_spielfeld ,_spielerDerBeklautWird):
        #Eine Liste mit allen feldern die in keiner Mühle sind wird erstellt.
        felderDieKlaubarSind = self.erhalteFelderMitIDDieNICHTInMühleSind(_spielfeld,_spielerDerBeklautWird,self.dreierKombinationen)
        #Es wird geprüft ob die Liste mit klaubaren feldern = 0 ist. Fals ja dann bedeutet das, dass sich alle Figuren des Gegners in Mühlen bedinfen.
        #In diesem Fall darf der Spieler auch Figuren aus Mühlen klauen
        if len(felderDieKlaubarSind) == 0:
            #Die Liste wird neu gesetzt. Nun enthällt sie ALLE Figuren des Gegners. Auch die in Mühöen. Der Grund ist wir obig beschrieben.
            felderDieKlaubarSind = self.erhalteALLEFelderMitID(_spielfeld,_spielerDerBeklautWird)
        return felderDieKlaubarSind
    #Falls was nicht funktioniert dann ändere ab dass die appendeten sachen kopiert werden!
    def erhalteBenachbarteFelder(self,dreierKombinationen,pos):
        nachbarn = []
        for x in dreierKombinationen:
            if pos in x:
                if x[1] != pos:
                    nachbarn.append(x[1])
                elif x[1] == pos:
                    nachbarn.append(x[0])
                    nachbarn.append(x[2])
        return nachbarn
    
    def erhalteFreieBenachbarteFelder(self,spielfeld, _pos, _dreierKombinationen):
        freieNachbarn = []
        nachbarn = self.erhalteBenachbarteFelder(dreierKombinationen=_dreierKombinationen,pos = _pos)
        for x in nachbarn:
            if spielfeld[x[0]][x[1]] == 0:
                freieNachbarn.append(x)
        return freieNachbarn

    def hatKeineMöglichenZügeMehr(self,_gameState, __spielfeld,spieler,_dreierKombinationen):
        hatKeineMöglichenZügeMehr = False
        
        if _gameState[1] >= 3 or _gameState[0] >=3:
            hatKeineMöglichenZügeMehr = True
       
        elif _gameState[(spieler-1)] == 1:
            züge = []
            spielerFiguren = self.erhalteALLEFelderMitID(__spielfeld, spieler)
            for x in range(len(spielerFiguren)):
                züge.append(self.erhalteFreieBenachbarteFelder(__spielfeld, spielerFiguren[x], _dreierKombinationen))
            if len(züge) != 0:
                hatKeineMöglichenZügeMehr = True


        return hatKeineMöglichenZügeMehr

class KI(Mühle_Funktionen):
    startSuchTiefen = [3,4,5,6,7,8]
    nutzbareCPUKerne = 12
    suchTiefe = 6
    #SuchZeit in Sekunden
    suchZeit = 100
    rootObj = []
    _queue = multiprocessing.Queue()
    def __init__(self):
        self.dreierKombinationen = self.generiereDreierKombinationen()
        
    def macheZug(self,spieler, zug, _gameState,_platz_Figuren, _spielfeld):

        #Wenn die len(zug) 3 entspricht, dann hat der Spieler mit diesem zug die Figur eines gegners Geklaut.
        if len(zug) == 3:
            #Die Geklaute Position wird 0 gesetzt.
            _spielfeld[zug[2][0]][zug[2][1]] = 0
        #Falls der zug[0][0] 99 entspricht befinden sich das SPiel in der Setzphase. In diesem Fall gäbe es keine Startposition die 0 gesetzt werden muss.
        if zug[0][0] != 99:
            #Ist zug[0][0] nicht 99 so muss das Startfeld 0 gesetzt werden.
            _spielfeld[zug[0][0]][zug[0][1]] = 0
        #Die Endposition wird dem Spieler gleichgesetzt. -> Die Figur hat sich bewegt
        _spielfeld[zug[1][0]][zug[1][1]] = spieler
        #SPIELER NICHT GEGNER kommt in die Zugphase
        if _gameState[(spieler-1)] == 0:
            _platz_Figuren[(spieler-1)] +=1
            if _platz_Figuren[(spieler-1)] == 9:
                _gameState[(spieler-1)]+=1
        #Gegner kommt in die Sprungphase
        if _gameState[(self.andererSpielerLokal(spieler)-1)] == 1 and len(self.erhalteALLEFelderMitID(_spielfeld,self.andererSpielerLokal(spieler))) == 3:
            _gameState[(self.andererSpielerLokal(spieler)-1)] +=1
        #Gegner hat verloren
        if _gameState[(self.andererSpielerLokal(spieler)-1)] == 2 and len(self.erhalteALLEFelderMitID(_spielfeld,self.andererSpielerLokal(spieler))) <3:
            _gameState[(self.andererSpielerLokal(spieler)-1)] +=1

    def macheZugRückgängig(self,spieler, zug, _gameState, _platzierte_Figuren, _spielfeld):
        anzahlDerSpielerFiguren = len(self.erhalteALLEFelderMitID(_spielfeld,spieler))

        if len(zug) == 3:
            #Die Gegnerische Figur die geklaut wurde, wird wieder platziert
            _spielfeld[zug[2][0]][zug[2][1]] = self.andererSpielerLokal(spieler)
        #Falls der zug[0][0] 99 entspricht befinden sich das SPiel in der Setzphase. In diesem Fall gäbe es keine Startposition die 0 gesetzt werden muss.
        if zug[0][0] != 99:
            #Ist zug[0][0] nicht 99 so muss das Startfeld auf den Spieler gesetzt werden.
            _spielfeld[zug[0][0]][zug[0][1]] = spieler
        
        #Die Endposition wird wieder gleich 0 gesetzt, da "zurückbewegt" wird.
        _spielfeld[zug[1][0]][zug[1][1]] = 0

        if _gameState[(spieler-1)] == 0:
            _platzierte_Figuren[(spieler-1)] -=1

        #Der Oben beschriebene Fall ist eingetroffen
        if _gameState[(spieler-1)] == 1 and anzahlDerSpielerFiguren < (len(self.erhalteALLEFelderMitID(_spielfeld,spieler))):
            _platzierte_Figuren[(spieler-1)] -=1
            _gameState[(spieler-1)] -=1
        
        #Gegner kommt aus der Sprungphase raus
        if len(zug) == 3:
            if _gameState[(self.andererSpielerLokal(spieler)-1)] == 2 and len(self.erhalteALLEFelderMitID(_spielfeld,self.andererSpielerLokal(spieler))) >3:
                _gameState[(self.andererSpielerLokal(spieler)-1)] -=1
            #Gegner hat nicht mehr verloren
            if _gameState[(self.andererSpielerLokal(spieler)-1)] == 3 and len(self.erhalteALLEFelderMitID(_spielfeld,self.andererSpielerLokal(spieler))) == 3:
                _gameState[(self.andererSpielerLokal(spieler)-1)] -=1

    def minmax_max(self,_spielfeld,gameState, suchtiefe, derzeitigeSuchtiefe, alpha, beta, spielerZug,platz_Figuren, __dreierKombinationen,____startZeit, ____suchZeit):
        if self.hatKeineMöglichenZügeMehr(gameState,_spielfeld,2, __dreierKombinationen) == True:
            return self.evaluiere(_spielfeld,platz_Figuren,gameState,__dreierKombinationen)
        if derzeitigeSuchtiefe == 0:
            return self.evaluiere(_spielfeld,platz_Figuren,gameState,__dreierKombinationen)
        maxWert = alpha
        möglicheZüge = self.sortiereZüge(self.generiereSpieleSituationsabhängigeMöglicheZüge(__dreierKombinationen,_spielfeld,gameState,2))
        for x in range(len(möglicheZüge)):
            #Feedback zur Generierung an den Nutzer:
            self.macheZug(2,möglicheZüge[x],gameState,platz_Figuren,_spielfeld)
            wert = self.minmax_min(_spielfeld,gameState,suchtiefe,(derzeitigeSuchtiefe-1),maxWert, beta, 1, platz_Figuren,__dreierKombinationen, ____startZeit,____suchZeit)
            self.macheZugRückgängig(2,möglicheZüge[x], gameState,platz_Figuren,_spielfeld)
            if wert > maxWert:
                maxWert = wert
                if maxWert >= beta:
                    break

            #Suche wird abgebrochen wenn ZeitLimit erreicht
            if(time.time()-____startZeit) > ____suchZeit:
                break
        return maxWert
    
    
    def evaluiere(self,___spielfeld, platzFiguren, _gameState,_dreierKombinationen):
        wert = 0
        wert -= abs(platzFiguren[(2-1)]-len(self.erhalteALLEFelderMitID(___spielfeld,2)))*300
        anzahlDerFreienFelderGesammt = 0
        kiPositionen = self.erhalteALLEFelderMitID(___spielfeld,2)
        for x in range(len(kiPositionen)):
            anzahlDerFreienFelderGesammt += len(self.erhalteFreieBenachbarteFelder(___spielfeld,kiPositionen[x], _dreierKombinationen))
        wert += anzahlDerFreienFelderGesammt*2
        wert += abs(platzFiguren[1-1]-len(self.erhalteALLEFelderMitID(___spielfeld,1)))*150
        #"Eingesperrte" gelten als halbe Kaputte
        #Ermittlung aller KI Figuren
        kiFiguren = self.erhalteALLEFelderMitID(___spielfeld,2)
        eingesperrteFigurenDifferenz = 0
        #Alle KI Figuren werden auf einsperrung geprüft
        for figur in range(len(kiFiguren)):
            anzahlDerFreienFelder = len(self.erhalteFreieBenachbarteFelder(___spielfeld,kiFiguren[figur],_dreierKombinationen))
            if anzahlDerFreienFelder == 0:
                eingesperrteFigurenDifferenz -=1
        #Ermittlung aller Spielerfiguren
        spielerFiguren = self.erhalteALLEFelderMitID(___spielfeld,1)
        #Alle KI Figuren werden auf einsperrung geprüft
        for gegnerFigur in range(len(spielerFiguren)):
            anzahlDerFreienFelder = len(self.erhalteFreieBenachbarteFelder(___spielfeld, spielerFiguren[gegnerFigur],_dreierKombinationen))
            if anzahlDerFreienFelder == 0:
                eingesperrteFigurenDifferenz +=1
        wert += eingesperrteFigurenDifferenz*10

        #KI gewinnt
        if _gameState[0] == 3:
            wert = 6000
        #Unentschieden
        elif _gameState[0] == 2 and _gameState[1] == 2:
            if wert < 0:
                wert = 0
        return wert


    def sortiereZüge(self,züge):
        zügeSortiert = []

        for x in range(len(züge)):
            zug = züge[x]
            if len(zug) >2:
                zügeSortiert.append(zug)
        for x in range(len(züge)):
            zug = züge[x]
            if len(zug) ==2:
                zügeSortiert.append(zug)
        return züge

    def minmax_min(self,_spielfeld,gameState, suchtiefe, derzeitigeSuchtiefe, alpha, beta, spielerZug,platz_Figuren, __dreierKombinationen, ___startZeit,___suchZeit):
        
        if self.hatKeineMöglichenZügeMehr(gameState,_spielfeld, 1,__dreierKombinationen) == True:
            return self.evaluiere(_spielfeld,platz_Figuren,gameState,__dreierKombinationen)
        if derzeitigeSuchtiefe == 0:
            return self.evaluiere(_spielfeld,platz_Figuren,gameState,__dreierKombinationen)
        minWert = beta
        #minWert = 9000000
        möglicheZüge = self.sortiereZüge(self.generiereSpieleSituationsabhängigeMöglicheZüge(__dreierKombinationen,_spielfeld,gameState, 1))
        for z in range(len(möglicheZüge)):
            self.macheZug(1,möglicheZüge[z], gameState, platz_Figuren,_spielfeld)
            wert = self.minmax_max(_spielfeld, gameState, suchtiefe, (derzeitigeSuchtiefe-1), alpha, minWert, 2, platz_Figuren,__dreierKombinationen,___startZeit,___suchZeit)
            self.macheZugRückgängig(1,möglicheZüge[z], gameState,platz_Figuren,_spielfeld)
            if wert < minWert:
                minWert = wert
                if minWert <= alpha:
                    break
            #Suche wird abgebrochen wenn ZeitLimit erreicht
            if(time.time()-___startZeit) > ___suchZeit:
                break
        return minWert


    #Modifiziert für Iterative Tiefensuche auf Verschiedenen Kernen
    def sucheBestenZugMitZeitBegrenzung(self,_spielfeld_,_gameStates_,_platzFiguren_,_startZeit_,_suchZeit_,_suchTiefe_):
        möglicheZüge = self.generiereSpieleSituationsabhängigeMöglicheZüge(self.dreierKombinationen,_spielfeld_,_gameStates_,2)
        
        if __name__ == "__main__":
            prozess = multiprocessing.Process(target = self.mp_Max, args = (self._queue,möglicheZüge ,_suchTiefe_, _spielfeld_,_gameStates_,_platzFiguren_,_startZeit_,_suchZeit_))
            prozess.start()

    #Die Modifizierte max Funktion. Sie wird nur vom task_Splitter aufgerufen um den Kombination von MinMax und MultiProcessing zu vereinfachen
    def mp_Max(self,queue, züge, suchtiefe,Cspielfeld, gameState, _platzFiguren, __startZeit, __suchZeit):
        #Generierung der DreierKombinationen
        _dreierKombinationen = self.generiereDreierKombinationen()
        ergebnis = []
        alpha = -9000000000000
        beta = 9000000000000
        #Ändern für das KI auch mal startet
        for i in range(len(züge)):
            self.macheZug(2,züge[i],gameState,_platzFiguren,Cspielfeld)
            wert = self.minmax_min(Cspielfeld,gameState, suchtiefe, (suchtiefe-1), alpha, beta, 1,_platzFiguren, _dreierKombinationen, __startZeit, __suchZeit)
            self.macheZugRückgängig(2,züge[i],gameState,_platzFiguren,Cspielfeld)
            if wert > alpha:
                alpha = wert
                ergebnis = [züge[i], wert]
                if alpha >= beta:
                    break
            
            if (time.time()-__startZeit) > __suchZeit:
                ergebnis = ["Keine Zeit mehr! Suche unvollständig!"]
                break
        #Falls suchzeit nicht unbegrenz, appende die Suchtiefe
        if __suchZeit != 100000:
            ergebnis.append(suchtiefe)
        queue.put(ergebnis)
        
    """
Die möglichen Züge werden in folgendem Layout gespeichert.

AltePosition, NeuePosition, ZuKlauendePosition

Falls das Spiel sich in der Setzphase befindet ist die alte Position gleich [99,99], da Sie nicht existiert.

Falls keine Mühle durch den Zug gebildet wird, wird der 3 Parameter einfach weggelassen.

"""
    def generiereSpieleSituationsabhängigeMöglicheZüge(self, _dreierKombinationen,__spielfeld,_gameState,spieler):
        möglicheZügeKI = []
        
        #GameState 0 = Setzphase
        if _gameState[(spieler-1)] == 0:
            #In der Setzphase sind alle möglichen Züge einfach die Freien Felder.
            freieFelder = self.erhalteALLEFelderMitID(__spielfeld, 0)
            for x in range(len(freieFelder)):
                #platzieren einer Figur an der stelle um zu testen ob eine Neue Mühle entsteht.
                __spielfeld[freieFelder[x][0]][freieFelder[x][1]] = spieler
                #Test ob durch Zug neue Mühle entsteht.
                if self.testeObInDreierKombination(__spielfeld,freieFelder[x], _dreierKombinationen) == True:
                    #Falls ja wird jegliches geklaute Feld als individuelle Variation gespeichert.
                    klaubarePositionen = []
                    #Zuerst der Test ob die zu klauende Figur bei bedarf aus der gegnerischen Mühle sein darf. Dieser Fall tritt ein, falls es kein anderes klaubares Feld gibt.
                    anzahlDerFigurenAußerhalbVonMühle = len(self.erhalteFelderMitIDDieNICHTInMühleSind(__spielfeld,self.andererSpielerLokal(spieler), _dreierKombinationen))
                    if anzahlDerFigurenAußerhalbVonMühle == 0:
                        klaubarePositionen = self.erhalteALLEFelderMitID(__spielfeld, self.andererSpielerLokal(spieler))
                    elif anzahlDerFigurenAußerhalbVonMühle > 0:
                        klaubarePositionen = self.erhalteFelderMitIDDieNICHTInMühleSind(__spielfeld, self.andererSpielerLokal(spieler), _dreierKombinationen)
                    #Nun loopen durch alle Klaubaren Felder um die Variationen zu erzeugen.
                    for z in range(len(klaubarePositionen)):
                        #Nun werden die 3 Variablen in das Richtige Format wie oben gegeben gebracht.
                        möglicheZügeKI.append([[99,99], freieFelder[x], klaubarePositionen[z]])
                #Die platzierte Figur führt zu keiner neuen Mühle.
                else:
                    möglicheZügeKI.append([[99,99], freieFelder[x]])
                #Entfernen der Figur die zum Mühle-Test genutzt wurde.
                __spielfeld[freieFelder[x][0]][freieFelder[x][1]] = 0
        elif _gameState[(spieler-1)] == 1:
            spielerPositionen = self.erhalteALLEFelderMitID(__spielfeld,spieler)
            for x in range(len(spielerPositionen)):
                freieBenachbarteFelder = self.erhalteFreieBenachbarteFelder(__spielfeld,spielerPositionen[x],_dreierKombinationen)
                for z in range(len(freieBenachbarteFelder)):
                    #platzieren einer Figur an der stelle um zu testen ob eine Neue Mühle entsteht.
                    __spielfeld[freieBenachbarteFelder[z][0]][freieBenachbarteFelder[z][1]] = spieler
                    #Die Startposition wird natürlich auch 0 gesetzt.
                    __spielfeld[spielerPositionen[x][0]][spielerPositionen[x][1]] = 0
                    if self.testeObInDreierKombination(__spielfeld,freieBenachbarteFelder[z],_dreierKombinationen) == True:
                        #Falls ja wird jegliches geklaute Feld als individuelle Variation gespeichert.
                        klaubarePositionen = []
                        #Zuerst der Test ob die zu klauende Figur bei bedarf aus der gegnerischen Mühle sein darf. Dieser Fall tritt ein, falls es kein anderes klaubares Feld gibt.
                        anzahlDerFigurenAußerhalbVonMühle = len(self.erhalteFelderMitIDDieNICHTInMühleSind(__spielfeld,self.andererSpielerLokal(spieler),_dreierKombinationen))
                        if anzahlDerFigurenAußerhalbVonMühle == 0:
                            klaubarePositionen = self.erhalteALLEFelderMitID(__spielfeld,self.andererSpielerLokal(spieler))
                        elif anzahlDerFigurenAußerhalbVonMühle > 0:
                            klaubarePositionen = self.erhalteFelderMitIDDieNICHTInMühleSind(__spielfeld,self.andererSpielerLokal(spieler),_dreierKombinationen)
                        for klaubarePosition in range(len(klaubarePositionen)):
                            möglicheZügeKI.append([spielerPositionen[x], freieBenachbarteFelder[z], klaubarePositionen[klaubarePosition]])
                    #Die platzierte Figur führt zu keiner neuen Mühle.
                    else:
                        möglicheZügeKI.append([spielerPositionen[x], freieBenachbarteFelder[z]])
                    #Entfernen der Figur die zum Mühle-Test genutzt wurde.
                    __spielfeld[freieBenachbarteFelder[z][0]][freieBenachbarteFelder[z][1]] = 0
                    #Platzieren der Figur auf der Originalposition
                    __spielfeld[spielerPositionen[x][0]][spielerPositionen[x][1]] = spieler
        elif _gameState[(spieler-1)] == 2:
            spielerPositionenGameState2 = self.erhalteALLEFelderMitID(__spielfeld,spieler)
            for startPosition in range(len(spielerPositionenGameState2)):
                #In der Sprungphase sind alle möglichen Züge einfach die Freien Felder.
                freiePositionen = self.erhalteALLEFelderMitID(__spielfeld,0)
                for endPosition in range(len(freiePositionen)):
                    #platzieren einer Figur an der stelle um zu testen ob eine Neue Mühle entsteht.
                    __spielfeld[freiePositionen[endPosition][0]][freiePositionen[endPosition][1]] = spieler

                    #die StartPosition wird probehalber auch auf 0 gesetzt
                    __spielfeld[spielerPositionenGameState2[startPosition][0]][spielerPositionenGameState2[startPosition][1]] = 0

                    #Test ob dadurch eine Mühle entsteht
                    if self.testeObInDreierKombination(__spielfeld,freiePositionen[endPosition], _dreierKombinationen) == True:
                        #Falls ja wird jegliches geklaute Feld als individuelle Variation gespeichert.
                        klaubarePositionen = []
                        #Zuerst der Test ob die zu klauende Figur bei bedarf aus der gegnerischen Mühle sein darf. Dieser Fall tritt ein, falls es kein anderes klaubares Feld gibt.
                        anzahlDerFigurenAußerhalbVonMühle = len(self.erhalteFelderMitIDDieNICHTInMühleSind(__spielfeld,self.andererSpielerLokal(spieler),_dreierKombinationen))
                        if anzahlDerFigurenAußerhalbVonMühle == 0:
                            klaubarePositionen = self.erhalteALLEFelderMitID(__spielfeld,self.andererSpielerLokal(spieler))
                        elif anzahlDerFigurenAußerhalbVonMühle > 0:
                            klaubarePositionen = self.erhalteFelderMitIDDieNICHTInMühleSind(__spielfeld,self.andererSpielerLokal(spieler),_dreierKombinationen)
                        
                        for klaubarePosition in range(len(klaubarePositionen)):
                            möglicheZügeKI.append([spielerPositionenGameState2[startPosition], freiePositionen[endPosition], klaubarePositionen[klaubarePosition]])
                    #Die Platzierte Figur führt zu keiner neuen Mühle.
                    else:
                        möglicheZügeKI.append([spielerPositionenGameState2[startPosition],freiePositionen[endPosition]])
                    #Entfernen der Figur die zum Mühle-Test genutzt wurde.
                    __spielfeld[freiePositionen[endPosition][0]][freiePositionen[endPosition][1]] = 0

                    #erneutes Platzieren der Startfigur
                    __spielfeld[spielerPositionenGameState2[startPosition][0]][spielerPositionenGameState2[startPosition][1]] = spieler
        elif _gameState[(spieler-1)]==3:
            pass
        return möglicheZügeKI

    def ermittleBestenZug(self,_spielfeld, _gameState, _platzierteFiguren, _suchTiefe, _CPUKerne):
        self.nutzbareCPUKerne = _CPUKerne
        self.suchTiefe = _suchTiefe
        self.suchZeit = 100000

        #Die Parameter müssen mit jeder Suche neu gesetzt werden
        self.startZeit = time.time()
        #Der Minmax Aufruf
        self.task_Splitter(_gameState,_platzierteFiguren,_spielfeld, self.startZeit, self.suchZeit)

    def ermittleBestenZugNachZeit(self, _spielfeld, _gameState, _platzierteFiguren, _startZeit,_suchZeit, _CPUKerne):
        self.nutzbareCPUKerne = _CPUKerne
        self.suchZeit = _suchZeit
        self.startZeit = time.time()
        gleichzeitigeTiefensuchen = self.nutzbareCPUKerne
        for x in range((gleichzeitigeTiefensuchen)):
            self.sucheBestenZugMitZeitBegrenzung(_spielfeld,_gameState,_platzierteFiguren,_startZeit,_suchZeit,self.startSuchTiefen[x])

    #Der Zusatzbaustein um den Minmax auf mehreren kernen getrennt laufen zu lassen.
    def task_Splitter(self, _gameStates_, _platzFiguren_, _spielfeld_, _startZeit, _suchZeit):

        if __name__ == "__main__":
            #Verwaltet Rückgabe
            möglicheZüge = self.generiereSpieleSituationsabhängigeMöglicheZüge(self.dreierKombinationen,_spielfeld_,_gameStates_,2)
            anzahlProProzess = int(math.ceil(len(möglicheZüge)/self.nutzbareCPUKerne))
            for i in range(self.nutzbareCPUKerne):
                prozess = multiprocessing.Process(target = self.mp_Max, args = (self._queue, möglicheZüge[anzahlProProzess*i: anzahlProProzess*(i+1)],self.suchTiefe, _spielfeld_, _gameStates_,_platzFiguren_, _startZeit, _suchZeit))
                prozess.start()


class Main(Mühle_Funktionen):
    root = Tk()
    #Höhe und breite des Spielfeld bei Starten des Programm
    heightWindow = 600
    widthWindow = 1000
    #Der Kreisradius
    kreisRadius = 20
    derzeitigeStepSize = 0
    #Für die Klicks des Spielers. Der erste legt das STartfeld und der 2 das endfeld fest.
    clickNummer = 1
    #Der Spieler am zug. Nur relevant falls 2 spieler da an sonsten einfach die KI aufgerufen wird.
    spielerAmZug = 1
    
    log = []


    CONST_EMPTY_SPIELFELD = [
                [0,3,3,0,3,3,0],
                [3,0,3,0,3,0,3],
                [3,3,0,0,0,3,3],
                [0,0,0,3,0,0,0],
                [3,3,0,0,0,3,3],
                [3,0,3,0,3,0,3],
                [0,3,3,0,3,3,0]  
    ]

    spielfeld = [ 
                [0,3,3,0,3,3,0],
                [3,0,3,0,3,0,3],
                [3,3,0,0,0,3,3],
                [0,0,0,3,0,0,0],
                [3,3,0,0,0,3,3],
                [3,0,3,0,3,0,3],
                [0,3,3,0,3,3,0]
                ]

    
    gameStateArray = [0,0]
    platzierteFiguren = [0,0]
    ersterClick = True
    geklickteErstePosition = []

    kiAmÜberlegen = 0

    dreierKombinationen = []

    ermittelteZüge = []

    möglicheZügeMarkierungen = []
    #Dieses Array enthält die möglichen Züge, da um die Markierungen mitskalieren zu können diese neu generiert werden müssen
    möglicheZügeMark =[]


    altePosition = []
    uiKreise = []
    uiLinien = []

    verfuegbareSpielerFarben = ["#cc0000","#134d00","#FFFFFF","#000000","#993300"]


    #Die SPieler farben. 0 ist frei 1 ist spieler 1 und 2 spieler 2
    foregroundColorArray = ["#FFFFCC", "#ffffff", "#000000"]
    #Offset damit mehr abstand zum rand
    offset = 50
    #Das offset damit Quadrat
    symetryOffset = [0,0]

    

    #Mit ZUG ist nicht einer sondern ALLE möglichen Züge gemeint
    def markiereMöglicheZüge(self, zug):
        self.möglicheZügeMark = copy.deepcopy(zug)
        for x in range(len(zug)):
            self.möglicheZügeMarkierungen.append([self.cv.create_oval(self.symetryOffset[0] + zug[x][0]*self.derzeitigeStepSize -self.kreisRadius,self.symetryOffset[1]+zug[x][1]*self.derzeitigeStepSize-self.kreisRadius, self.symetryOffset[0]+zug[x][0]*self.derzeitigeStepSize+self.kreisRadius,self.symetryOffset[1]+zug[x][1]*self.derzeitigeStepSize+self.kreisRadius, width = 5,outline = "green")])
    def löscheMöglicheZügeMarkierung(self):
        for x in range(len(self.möglicheZügeMarkierungen)):
            self.cv.delete(self.möglicheZügeMarkierungen[x])
        self.möglicheZügeMarkierungen.clear()


    curPointAmount = 0
    def prüfeObBesterZugFertig(self):
        
        

        bestValue = -90000000
        if len(self.ermittelteZüge) != self.gegnerKI.nutzbareCPUKerne:
            try:
                wert = self.gegnerKI._queue.get(block = False)
                self.ermittelteZüge.append(wert)
            except queue.Empty:
                pass

            pointStr = [".", "..", "..."]


            self.canvasInfo.delete(self.KIInfoText)
            if self.curPointAmount == 2:
                self.curPointAmount = 0
            elif self.curPointAmount == 1:
                self.curPointAmount =2
            elif self.curPointAmount == 0:
                self.curPointAmount = 1
            if self.suchzeit.get() != 0:
                if len(self.ermittelteZüge) != 0:
                    self.KIInfoText = self.canvasInfo.create_text(5,65,text =(str(self.gegnerKI.startSuchTiefen[len(self.ermittelteZüge)]-1)+"er Tiefe gesucht. KI arbeitet" + pointStr[self.curPointAmount]), font= font.Font(size = 15), anchor="w") 
            elif self.suchzeit.get() == 0:
                self.KIInfoText = self.canvasInfo.create_text(50,65,text =(str(int((len(self.ermittelteZüge)/ self.gegnerKI.nutzbareCPUKerne)*100)) + "% erledigt. KI arbeitet" + pointStr[self.curPointAmount]), font= font.Font(size = 15), anchor="w") 


            self.root.after(1000,self.prüfeObBesterZugFertig)
        elif len(self.ermittelteZüge) == self.gegnerKI.nutzbareCPUKerne:
            #Die Rotation wird zurückgesetzt um zu verhindern das durch das Rotieren und den gleichzeitig Arbeitenden minmax Algorithmus fehler aufterten
            self.spielfeld = copy.deepcopy(self.kopiertesSpielfeld)
            self.zeichneSpielfeld()

            if self.suchzeit.get() == 0:
                besterZug = []
                for x in range(len(self.ermittelteZüge)):
                    if str(self.ermittelteZüge[x]) == "[]":
                        pass
                    else:
                        if bestValue <= self.ermittelteZüge[x][1]:
                            bestValue = self.ermittelteZüge[x][1]
                            besterZug = self.ermittelteZüge[x][0]
            else:
                besterZug = []
                tiefsteSuchtiefe = 0
                for x in range(len(self.ermittelteZüge)):
                    if str(self.ermittelteZüge[x]) == "[]":
                        pass
                    else:
                        if len(self.ermittelteZüge[x]) == 3:
                            if tiefsteSuchtiefe <= self.ermittelteZüge[x][2]:
                           
                                tiefsteSuchtiefe = self.ermittelteZüge[x][2]
                                besterZug = self.ermittelteZüge[x][0]
                                bestValue = self.ermittelteZüge[x][1]
            if self.gameStateArray[1] == 1 or self.gameStateArray[1] == 2:
                self.BewegeFigur(besterZug[0], besterZug[1])
            elif self.gameStateArray[1] == 0:
                self.PlatziereFigur(besterZug[1], 2)
                if self.platzierteFiguren[1] == 9:
                    self.gameStateArray[1] = 1
            if len(besterZug) == 3:
                self.KlaueFigur(besterZug[2])
            if self.gameStateArray[0] == 1 and len(self.erhalteALLEFelderMitID(self.spielfeld,1)) == 3:
                self.gameStateArray[0] = 2


            self.kiAmÜberlegen = 0
            self.curPointAmount = 0
            self.canvasInfo.delete(self.KIInfoText)

            self.ermittelteZüge.clear()
        

    def zeichneSpielfeld(self):
        #Berrechnen der kürzeren Seite
        height = self.cv.winfo_height()
        width = self.cv.winfo_width()
        height, width = height-self.offset*2, width-self.offset*2
        
        aviableSize = 0
        if height > width:
            self.symetryOffset = [self.offset,self.offset+ ((height-width)/2)]
            aviableSize = width
        elif height < width:
            self.symetryOffset = [ self.offset + ((width-height)/2),self.offset]
            aviableSize = height
        else:
            aviableSize = height
        #Berrechnung der Schrittgröße
        #Berrechnung der größe der Kreise
        self.kreisRadius = (aviableSize/20)
        
        #Der KreisRadius wird zwischen zwei Werten gesperrt um grafische Bugs zu verhindern.
        if self.kreisRadius < 10:
            self.kreisRadius = 10
        elif self.kreisRadius >40:
            self.kreisRadius = 40
        
        stepSize = aviableSize/6
        
        self.derzeitigeStepSize = stepSize

        curLength = 6
        for x in range(7):
            self.uiLinien.append(self.cv.create_line(self.symetryOffset[0]+stepSize*x, self.symetryOffset[1]+stepSize*x, self.symetryOffset[0]+stepSize*x + stepSize*curLength, self.symetryOffset[1]+stepSize*x, width= 2))
            self.uiLinien.append(self.cv.create_line(self.symetryOffset[0]+stepSize*x, self.symetryOffset[1]+stepSize*x, self.symetryOffset[0]+stepSize*x , self.symetryOffset[1]+stepSize*x+ stepSize*curLength, width = 2))
            curLength -=2
        curLength = 2
        for i in range(2):
            self.uiLinien.append(self.cv.create_line(self.symetryOffset[0] + stepSize*3,self.symetryOffset[1]+stepSize*4*i,self.symetryOffset[0]+stepSize*3,+ self.symetryOffset[1]+stepSize*i*4 + stepSize*curLength, width = 2))
            self.uiLinien.append(self.cv.create_line(self.symetryOffset[0]+stepSize*4*i,self.symetryOffset[1] + stepSize*3,+ self.symetryOffset[0]+stepSize*i*4 + stepSize*curLength,self.symetryOffset[1]+stepSize*3, width = 2))
        self.zeichneHintergrundKreise(self.symetryOffset[0], self.symetryOffset[1], stepSize,stepSize) 
    def zeichneHintergrundKreise(self,offsetX,offsetY,stepX,stepY):

        #Berrechnung der größe der Kreise
        posX,posY = 0,0
        for y in range(len(self.spielfeld)):
            for x in range(len(self.spielfeld[y])):
                if self.spielfeld[x][y] != 3:
                    self.uiKreise.append([self.cv.create_oval(offsetX + posX*stepX -self.kreisRadius,offsetY+posY*stepY-self.kreisRadius, offsetX+posX*stepX+self.kreisRadius,offsetY+posY*stepY+self.kreisRadius, width = 2,fill = self.foregroundColorArray[self.spielfeld[x][y]]),(x,y)])
                posX+=1
            posX = 0
            posY+=1
    keyPressHistory = []
    def keyPress(self,event):
        if str(event.keysym).capitalize() not in self.keyPressHistory:
            self.keyPressHistory.append(str(event.keysym).capitalize())
        self.keyEvent()
    def keyEvent(self):
        if "Z" in self.keyPressHistory and "Control_l" in self.keyPressHistory or "Z" in self.keyPressHistory and "Control_r" in self.keyPressHistory:
            #Only for Debug purposes
            if self.gameStateArray[0] < 4 and self.gameStateArray[1] <4:
                self.undoAction()
                self.aktualisiereGameState()
    def keyUp(self,event):
        if str(event.keysym).capitalize() in self.keyPressHistory:
            self.keyPressHistory.pop(self.keyPressHistory.index(str(event.keysym).capitalize()))
    


    def aktualisiereGameState(self):
        for x in range(2):
            if self.gameStateArray[x] == 1 and self.platzierteFiguren[x] <9:
                self.gameStateArray[x] = 0
            if self.gameStateArray[x] == 2 and len(self.erhalteALLEFelderMitID(self.spielfeld, (x+1))) > 3:
                self.gameStateArray[x] = 1

            if self.gameStateArray[x] == 0 and self.platzierteFiguren[x] == 9:
                self.gameStateArray[x] = 1
            if self.gameStateArray[x] == 1 and len(self.erhalteALLEFelderMitID(self.spielfeld,(x+1))) == 3:
                self.gameStateArray[x] = 2
            if len(self.erhalteALLEFelderMitID(self.spielfeld,(x+1))) < 2 and self.gameStateArray[x] != 0:
                self.gameStateArray[x] = 4

    #Wird nur beim ersten Aufruf der KI oder bei SPieler gegen Spieler genutzt
    def wechsleSpieler(self):
        self.löscheMöglicheZügeMarkierung()
        if self.spielModus.get() == "Spieler gegen Spieler":
            if self.spielerAmZug == 1:
                self.spielerAmZug = 2
            else:
                self.spielerAmZug = 1
        elif self.spielModus.get() == "Spieler gegen KI":
            self.kopiertesSpielfeld = copy.deepcopy(self.spielfeld)
            #Test ob Iterativ oder nicht
            if self.suchzeit.get() == 0:
                self.gegnerKI.ermittleBestenZug(self.spielfeld, self.gameStateArray, self.platzierteFiguren, self.suchtiefe.get(), 4)
            else:
                suchZeiten = [100000, 5, 10, 30, 60, 120]
                self.gegnerKI.ermittleBestenZugNachZeit(self.spielfeld,self.gameStateArray,self.platzierteFiguren,time.time(),suchZeiten[self.suchzeit.get()], 4)
            self.kiAmÜberlegen = 1
            self.root.after(1000, self.prüfeObBesterZugFertig)
    def PlatziereFigur(self,position, spieler):
        self.spielfeld[position[0]][position[1]] = spieler
        self.platzierteFiguren[(spieler-1)] +=1
        
        self.canvasInfo.delete(self.verbleibendeZuPlatzierendeFigurenSpieler1)
        self.canvasInfo.delete(self.verbleibendeZuPlatzierendeFigurenSpieler2)

        self.verbleibendeZuPlatzierendeFigurenSpieler1 = self.canvasInfo.create_text(65,30,text = str((9-self.platzierteFiguren[0])), font = font.Font(size = 15))
        self.verbleibendeZuPlatzierendeFigurenSpieler2 = self.canvasInfo.create_text(265,30,text = str((9-self.platzierteFiguren[1])), font = font.Font(size = 15))
        
        self.zeichneSpielfeld()


    def BewegeFigur(self,altePos, neuePos):
        self.spielfeld[neuePos[0]][neuePos[1]] = self.spielfeld[altePos[0]][altePos[1]]
        self.spielfeld[altePos[0]][altePos[1]] = 0

        self.löscheMöglicheZügeMarkierung()
        self.möglicheZügeMark.clear()
        
        self.zeichneSpielfeld()

    
    def KlaueFigur(self,position):
        self.spielfeld[position[0]][position[1]] = 0
        
        self.zeichneSpielfeld()


    def undoAction(self):
        if len(self.log) != 0:
            self.spielfeld = self.log[len(self.log)-1][0]
            self.spielerAmZug = self.log[len(self.log)-1][2]
            self.platzierteFiguren = self.log[len(self.log)-1][1]
            self.log.pop((len(self.log)-1))

            self.canvasInfo.delete(self.verbleibendeZuPlatzierendeFigurenSpieler1)
            self.canvasInfo.delete(self.verbleibendeZuPlatzierendeFigurenSpieler2)
            self.verbleibendeZuPlatzierendeFigurenSpieler1 = self.canvasInfo.create_text(65,30,text = str((9-self.platzierteFiguren[0])), font = font.Font(size = 15))
            self.verbleibendeZuPlatzierendeFigurenSpieler2 = self.canvasInfo.create_text(265,30,text = str((9-self.platzierteFiguren[1])), font = font.Font(size = 15))


            self.zeichneSpielfeld()

    

    def führeZugAusSetzphase(self, zug):
        leereFelder = self.erhalteALLEFelderMitID(self.spielfeld, 0)
        if zug in leereFelder:
            self.log.append([copy.deepcopy(self.spielfeld), copy.deepcopy(self.platzierteFiguren), copy.deepcopy(self.spielerAmZug)])
            self.PlatziereFigur(zug, self.spielerAmZug)
            if self.platzierteFiguren[(self.spielerAmZug-1)] == 9:
                self.gameStateArray[(self.spielerAmZug-1)] +=1
            if self.testeObInDreierKombination(self.spielfeld, zug, self.dreierKombinationen) == True:
                self.gameStateArray[(self.spielerAmZug-1)] +=0.5
                klaubar = self.ermittleKlaubareFelder(self.spielfeld, self.andererSpielerLokal(self.spielerAmZug))
                self.markiereMöglicheZüge(klaubar)
            else:
                self.wechsleSpieler()

    def führeZugAusZugphase(self,zug):
        if self.ersterClick == True:
            spielerPositionen = self.erhalteALLEFelderMitID(self.spielfeld, self.spielerAmZug)
            if zug in spielerPositionen:
                self.geklickteErstePosition = zug
                self.markiereMöglicheZüge(self.erhalteFreieBenachbarteFelder(self.spielfeld, zug, self.dreierKombinationen))

                if len(self.erhalteFreieBenachbarteFelder(self.spielfeld, zug, self.dreierKombinationen)) != 0:
                    self.ersterClick = False
        else:
            nachbarFelder = self.erhalteFreieBenachbarteFelder(self.spielfeld, self.geklickteErstePosition, self.dreierKombinationen)
            
            if zug in nachbarFelder:
                self.log.append([copy.deepcopy(self.spielfeld), copy.deepcopy(self.platzierteFiguren), copy.deepcopy(self.spielerAmZug)])
                self.BewegeFigur(self.geklickteErstePosition, zug)


                if self.testeObInDreierKombination(self.spielfeld, zug, self.dreierKombinationen) == True:
                    self.gameStateArray[(self.spielerAmZug-1)] += 0.5

                    klaubar = self.ermittleKlaubareFelder(self.spielfeld, self.andererSpielerLokal(self.spielerAmZug))
                    self.markiereMöglicheZüge(klaubar)
                else:
                    self.wechsleSpieler()
                self.ersterClick = True
            else:
                self.ersterClick = True
    
    def führeZugAusSprungphase(self, zug):
        if self.ersterClick == True:
            spielerPositionen = self.erhalteALLEFelderMitID(self.spielfeld, self.spielerAmZug)
            if zug in spielerPositionen:
                self.geklickteErstePosition = zug
                self.markiereMöglicheZüge(self.erhalteALLEFelderMitID(self.spielfeld, 0))
                self.ersterClick = False
        else:
            freiePositionen = self.erhalteALLEFelderMitID(self.spielfeld,0)
            if zug in freiePositionen:
                self.log.append([copy.deepcopy(self.spielfeld), copy.deepcopy(self.platzierteFiguren), copy.deepcopy(self.spielerAmZug)])
                self.BewegeFigur(self.geklickteErstePosition, zug)
                if self.testeObInDreierKombination(self.spielfeld,zug,self.dreierKombinationen) == True:
                    self.gameStateArray[(self.spielerAmZug-1)] += 0.5
                    klaubar = self.ermittleKlaubareFelder(self.spielfeld, self.andererSpielerLokal(self.spielerAmZug))
                    self.markiereMöglicheZüge(klaubar)
                else:
                    self.wechsleSpieler()
                self.ersterClick = True
            else:
                self.ersterClick = True
            
    #Gibt die Spielfelder einer ID zurück die in keiner Mühle verbaut sind
      
    
    def click(self, event):
        if self.kiAmÜberlegen == 0 and self.gameStateArray[0] < 3 and self.gameStateArray[1] < 3:
            #Alle möglichen Züge werden resettet falls das SPiel sich nicht in der Klauphase befindet, da in dieser die Markierungen bei einem MIsclick nicht verschwinden dürfen
            if ".5" not in str(self.gameStateArray[(self.spielerAmZug-1)]):
                self.löscheMöglicheZügeMarkierung()


            mousePos = [event.x, event.y]
            field = self.erhalteGeclicktesFeld(mousePos)
            
            #Gamestate 0 entspricht der Setzphase. In der Phase platziert der SPieler einfach nur Figuren auf auf freien feldern
            if self.gameStateArray[(self.spielerAmZug-1)] == 0:
                self.führeZugAusSetzphase(field)
            #Gamestate 1 entspricht der Zugphase. Der Spieler kann Figuren auf anliegende FREIE Felder bewegen.
            elif self.gameStateArray[(self.spielerAmZug-1)] == 1:
                self.führeZugAusZugphase(field)
            elif self.gameStateArray[(self.spielerAmZug-1)] == 2:
                self.führeZugAusSprungphase(field)
            
            #Die Klauphase
            elif ".5" in str(self.gameStateArray[(self.spielerAmZug-1)]):
                
                felderDieKlaubarSind = self.ermittleKlaubareFelder(self.spielfeld, self.andererSpielerLokal(self.spielerAmZug))

                if field in felderDieKlaubarSind:
                    self.KlaueFigur(field)
                    #Nachdem die Figur nun geklaut wurde wird der Gamestate wieder um 0.5 verringert und nochmal zum int konvertiert
                    self.gameStateArray[(self.spielerAmZug-1)] -=0.5
                    self.gameStateArray[(self.spielerAmZug-1)] = int(self.gameStateArray[(self.spielerAmZug-1)])

                    #Die Markierten Felder werden wieder gelöscht.
                    self.löscheMöglicheZügeMarkierung()


                    self.wechsleSpieler()
                else:
                    pass
            else:
                pass
            #Aktualisierung des GameState
            self.aktualisiereGameState()
        elif self.gameStateArray[0] > 3 and self.gameStateArray[1] < 3:
            self.canvasInfo.delete(self.KIInfoText)
            self.KIInfoText = self.canvasInfo.create_text(5,65,text =("Spieler 2 hat gewonnen."), font= font.Font(size = 15), anchor="w")
        elif self.gameStateArray[1] > 3 and self.gameStateArray[0] < 3:
            self.canvasInfo.delete(self.KIInfoText)
            self.KIInfoText = self.canvasInfo.create_text(5,65,text =("Spieler 1 hat gewonnen."), font= font.Font(size = 15), anchor="w")


    def rotatePositive(self):
        output = []
        for x in range(len(self.spielfeld)):
            newColumn = []
            for y in range(len(self.spielfeld[x])-1,-1,-1):
                newColumn.append(copy.copy(self.spielfeld[y][x]))
            output.append(copy.copy(newColumn))
            newColumn.clear()
            
        #Spielfeld ersetzen und neu Zeichnen
        self.spielfeld = output
        self.zeichneSpielfeld()


    def rotateNegative(self):
        output = []
        for x in range(len(self.spielfeld)-1,-1,-1):
            newColumn = []
            for y in range(len(self.spielfeld[x])):
                newColumn.append(copy.copy(self.spielfeld[y][x]))
            output.append(copy.copy(newColumn))
            newColumn.clear()
        
        #Spielfeld ersetzen und neu Zeichnen
        self.spielfeld = output
        self.zeichneSpielfeld()


    #KI gegen Spieler oder SPieler gegen Spieler
    spielModus = StringVar()


    #Platzhalterfunktion
    def c1(self):
        pass

    def displaySuchtiefe(self):
        selection = str(self.suchtiefe.get())
    def suchZeitInput(self):
        if self.suchzeit.get() != 0:
            self.einstellungs_Menu[1].entryconfig(0,state = "disabled")
        else:
            self.einstellungs_Menu[1].entryconfig(0, state = "normal")

    suchtiefe = IntVar()
    suchzeit = IntVar()

    #Die Schwierigkeit wird ausgewählt
    def __init__(self):
        self.root.bind("<Configure>", self.größeÄndernEvent)
        self.root.bind("<KeyPress>", self.keyPress)
        self.root.bind("<KeyRelease>", self.keyUp)
        self.root.geometry(str(self.widthWindow)+"x"+str(self.heightWindow))
        self.root.minsize(300,300)
        self.canvasInfo = Canvas(self.root, width = 300, height = 80)
        self.canvasInfo.pack()

        self.canvasInfo.create_oval(10,10,50,50,fill = self.foregroundColorArray[1])
        self.verbleibendeZuPlatzierendeFigurenSpieler1 = self.canvasInfo.create_text(65,30,text = ": 9", font = font.Font(size = 15))

        self.canvasInfo.create_oval(210,10,250,50,fill = self.foregroundColorArray[2])
        self.verbleibendeZuPlatzierendeFigurenSpieler2 = self.canvasInfo.create_text(265,30,text = ": 9", font = font.Font(size = 15))

        self.KIInfoText = self.canvasInfo.create_text(150,65,text = "", font= font.Font(size = 15), anchor="center")

        self.cv = Canvas(self.root, width=self.widthWindow, height=self.heightWindow)
        self.cv.pack()
        self.root.update()
        self.cv.bind("<Button-1>", self.click)
        self.zeichneSpielfeld()
        #Der Menu bar code----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        self.menu_Bar = Menu(self.root)
        self.root.geometry(str(self.widthWindow)+"x"+str(self.heightWindow))
        self.root.title("Mühle-Seminararbeit-Henry-Gagelmann")

        #Das Spielfeld rotieren
        self.createMenuCascadeComponent(type="Button", componentName="Spielfeld rotieren", labels=["90° Rechts", "90° Links"], outputFunctions=[self.rotateNegative, self.rotatePositive], parent = self.menu_Bar)
        
        self.root.config(menu = self.menu_Bar)
        self.einstellungs_Menu = self.createMenuCascadeComponent(componentName="Einstellungen",labels=["KI Einstellungen"])
        
        
        """
        0 ist der "Original" Menu Eintrag also EINSTELLUNGEN
        1 ist Spielmodus
        2 ist KI EInstellungen
        """
        self.createMenuCascadeComponent(type = "RadioButton", parent = self.einstellungs_Menu[0],componentName="Spielmodus", labels = ["Spieler gegen Spieler", "Spieler gegen KI"],inputValues=["Spieler gegen Spieler","Spieler gegen KI"],outputVariables=[self.spielModus],deafaultSelectedValues= ["Spieler gegen KI"], outputFunctions=[self.c1])
        self. suchTiefeMenuComp = self.createMenuCascadeComponent(type="RadioButton", parent = self.einstellungs_Menu[1], componentName="Suchtiefe", labels=["2","4","6"], inputValues=[2,4,6], outputFunctions=[self.displaySuchtiefe], outputVariables=[self.suchtiefe], deafaultSelectedValues=[4])
        self.createMenuCascadeComponent(type="RadioButton", parent = self.einstellungs_Menu[1],componentName="Suchzeit", labels=["Unbegrenzt", "7 Sekunden", "11 Sekunden", "30 Sekunden", "1 Minute", "2 Minuten"], outputFunctions=[self.suchZeitInput], inputValues=[0,1,2,3,4,5], outputVariables= [self.suchzeit], deafaultSelectedValues=[0])        
        self.menu_Bar.add_separator()
        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
        self.dreierKombinationen = self.generiereDreierKombinationen()

        self.gegnerKI = KI()
    
    def erhalteGeclicktesFeld(self,mousePosition):
        feld = [99,99]
        feldXStep = (self.cv.winfo_width()-(2*self.symetryOffset[0]))/6
        feldYStep = (self.cv.winfo_height()-(2*self.symetryOffset[1]))/6
        for x in range(7):
            posX = feldXStep*x+self.symetryOffset[0]
            entfernungX = posX-mousePosition[0]
            if entfernungX <= self.kreisRadius:
                for y in range(7):
                    posY = feldYStep*y + self.symetryOffset[1]
                    entfernung = math.sqrt((posX-mousePosition[0])**2+(posY-mousePosition[1])**2)
                    if entfernung <= self.kreisRadius:
                        feld = [x,y]
        return feld
    
    def löscheSpielfeld(self):
        for x in self.uiLinien:
            self.cv.delete(x)
        self.uiLinien.clear()
        for x in self.uiKreise:
            self.cv.delete(x[0])
        self.uiKreise.clear()    
    def größeÄndernEvent(self,event):
        self.cv.config(width=event.width, height=event.height)
        self.löscheSpielfeld()
        self.löscheMöglicheZügeMarkierung()
        self.zeichneSpielfeld()
        self.markiereMöglicheZüge(self.möglicheZügeMark)

    def createMenuCascadeComponent(self, type = "c", parent = None, componentName ="Kein Name", labels =[], inputValues=[], outputFunctions=[],outputVariables = [], deafaultSelectedValues = [], onValue = True, offValue = False):
        output = []
        if len(outputVariables) != 0 and type == "Check":
            for x in range(len(outputVariables)):
                outputVariables[x].set(deafaultSelectedValues[x])
        elif type == "RadioButton":
            outputVariables[0].set(deafaultSelectedValues[0])
        component = Menu(parent, tearoff=0)
        output.append(component)
        for x in range(len(labels)):
            if type == "RadioButton":
                component.add_radiobutton(label=labels[x],command = outputFunctions[0], variable=outputVariables[0],value=inputValues[x])
            elif type == "Button":
                component.add_command(label = labels[x], command = outputFunctions[x])
            elif type == "c":
                newMenu = Menu(component, tearoff=0)
                component.add_cascade(label = labels[x], menu = newMenu)
                output.append(newMenu)
            elif type == "Check":
                component.add_checkbutton(label = labels[x], onvalue= onValue, offvalue=offValue,variable=outputVariables[x])
            if x != (len(labels)-1):
                #component.add_separator()
                pass
        if parent == None:
            parent = self.menu_Bar
        parent.add_cascade(label = componentName, menu = component)
        return output
if __name__ == "__main__":
    window = Main()
    window.root.mainloop()
