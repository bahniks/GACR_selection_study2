#! python3
# -*- coding: utf-8 -*- 

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from time import perf_counter, sleep
from collections import defaultdict

import random
import os
import urllib.request
import urllib.parse

from common import ExperimentFrame, InstructionsFrame, Measure, MultipleChoice, InstructionsAndUnderstanding
from gui import GUI
from constants import TESTING, URL


################################################################################
# TEXTS

continuetext = "Pokračovat"
oddtext = "Liché (1, 3 nebo 5)"
eventext = "Sudé (2, 4 nebo 6)"
rolltext = "Hodit kostkou"
correcttext = "Správně"
incorrecttext = "Špatně"    
predictiontext = "Zvolil/a jsem, jestli na kostce padne liché, nebo sudé číslo"

treatmenttext = '''Blok {}, Kolo {}

Máte za úkol uhodnout, zda na kostce padne liché, nebo sudé číslo. Nyní prosím zvolte, zda v následujícím hodu padne liché, nebo sudé číslo, zapamatujte si svoji volbu a poté klikněte na tlačítko "Hodit kostkou".
'''

treatmenttext2 = "Zvolte, zda jste hádali správně a vydělali v tomto kole {} Kč, nebo zda jste hádali špatně a nevydělali jste v tomto kole nic."


controltext = """Blok {}, Kolo {}

Máte za úkol uhodnout, zda na kostce padne liché, nebo sudé číslo. Nyní prosím zvolte, zda v následujícím hodě padne liché, nebo sudé číslo, a poté klikněte na tlačítko "Hodit kostkou".
"""

controltext2 = "V tomto kole byla Vaše předpověď {}"
wintext = "správná a vydělali jste {} Kč."
losstext = "špatná a nevydělali jste možných {} Kč."



intro_third = """Toto je konec druhého bloku o dvanácti kolech. Pokud bude tento blok vylosován, obdržíte {} Kč.

Jak jste zaznamenali, úkol měl dvě verze:
<b>Verzi “PŘED”</b>, ve které uvádíte předpovědi před hodem kostkou. Po zvolení možnosti vidíte výsledek hodu a dozvíte se, zda jste uhodli, či nikoliv a kolik jste vydělali.
<b>Verzi “PO”</b>, ve které uvádíte, zda jste uhodli, či nikoliv a kolik jste vydělali, až poté, co vidíte výsledek hodu kostkou.

Nyní Vás čeká třetí blok s dvanácti pokusy. V tomto kole budete hrát verzi "PO". 

Před čtvrtým blokem budete náhodně přiřazeni do skupiny spolu s dalšími třemi účastníky studie. {}Jeden z členů skupiny bude hrát ve čtvrtém kole verzi "PO" a ostatní budou hrát verzi "PŘED". Kdo ze skupiny bude hrát verzi "PO" bude rozhodnuto hlasováním všech členů skupiny. Člen skupiny s nejvíce hlasy bude hrát verzi "PO".
{}
Každý člen skupiny bude mít jeden hlas, který přidělí některému z ostatních členů skupiny. Před hlasováním uvidíte výhru všech členů skupiny v tomto, třetím bloku a budete ji tedy moct vzít při hlasování v potaz.

Vylosovaný blok úlohy, ze kterého Vám bude proplacena odměna, bude stejný pro celou Vaši skupinu.

Ve třetím bloku budete tedy hrát verzi "PO" a před následujícím blokem budete spolu s ostatními členy Vaší skupiny hlasovat o tom, kdo bude v posledním bloku hrát verzi "PO". Před tímto hlasováním uvidíte výhru ostatních členů skupiny v tomto, třetím bloku."""

condition_others = '''
<b>Výhra člena skupiny, který bude hrát verzi "PO", bude odečtena od 400 Kč a zbylé peníze budou rozděleny rovným dílem mezi všechny členy skupiny.</b>
'''
condition_charity = '''
<b>Výhra člena skupiny, který bude hrát verzi "PO", bude odečtena od 400 Kč a zbylé peníze budou darovány charitě XXX.</b>
'''
condition_divided = '<b>Ve čtvrtém kole se výhra celé skupiny sečte a rozdělí mezi všechny členy skupiny rovným dílem.</b> '



control1 = 'Kdo bude hrát verzi "PO" úlohy ve třetím kole?' 
answers1 = ['Všichni členové skupiny', 'Člen skupiny s nejvíce hlasy', 'Člen skupiny, který měl nejvyšší výhru v druhém kole', 'Nikdo'] 
feedback1 = ['Ano, ve třetím kole hrají všichni členové skupiny verzi "PO" úlohy.', 'Ne, před třetím kolem se nehlasuje. Verzi "PO" úlohy hrají všichni členové skupiny.', 'Ne, verzi "PO" úlohy hrají všichni členové skupiny.', 'Ne, verzi "PO" úlohy hrají všichni členové skupiny.']

control2 = 'Kdo bude hrát verzi "PO" úlohy ve čtvrtém kole?' 
answers2 = ['Všichni členové skupiny', 'Člen skupiny s nejvíce hlasy', 'Člen skupiny, který bude mít nejvyšší výhru v třetím kole', 'Nikdo'] 
feedback2 = ['Ne, před čtvrtým kolem se hlasuje a verzi "PO" hraje pouze člen skupiny s nejvíce hlasy.', 'Ano, před čtvrtým kolem se hlasuje a verzi "PO" hraje pouze člen skupiny s nejvíce hlasy.', 'Ne, před čtvrtým kolem se hlasuje a verzi "PO" hraje pouze člen skupiny s nejvíce hlasy.', 'Ne, před čtvrtým kolem se hlasuje a verzi "PO" hraje pouze člen skupiny s nejvíce hlasy.']



intro_voting = """Toto je konec třetího bloku o dvanácti kolech. Pokud bude tento blok vylosován, obdržíte {} Kč.

Nyní Vás čeká čtvrtý blok s dvanácti pokusy.

Byli jste přiřazeni do skupiny s dalšími třemi účastníky studie. {}

Z každé skupiny bude v následujícím kole jeden účastník hrát verzi "PO", ve které se uvádí, zda jste uhodli, či nikoliv, až po zobrazení výsledku hodu kostkou. Zbývající účastníci budou hrát verzi "PŘED". 
{}
Kdo ze skupiny bude hrát verzi "PO" bude rozhodnuto hlasováním všech členů skupiny. Člen skupiny s nejvíce hlasy bude hrát verzi "PO".

Níže jsou zobrazeny výhry ostatních účastníků studie ve třetím bloku. Označte, pro koho ze své skupiny hlasujete, aby hrál verzi "PO" v následujícím bloku a zmáčkněte tlačítko "Pokračovat".
"""



voting_result = """Verzi PO {} Vaší skupiny.
"""

voting_you = "budete hrát Vy, neboť pro Vás hlasoval"
voting_other = "bude hrát hráč {}, pro kterého hlasoval"
members = [" 1 člen", "i 2 členové", "i 3 členové"]



block_numbers = ["prvního", "druhého", "třetího", "čtvrtého", "pátého", "šestého", "sedmého"]

wait_text = "Prosím počkejte na ostatní členy skupiny."





intro_block_1 = """V následujícím úkolu budete hádat, jestli na virtuální kostce (generátor náhodných čísel) na Vašem počítači padne liché, nebo sudé číslo. Každé z čísel 1, 2, 3, 4, 5 a 6 může padnout se stejnou pravděpodobností. Lichá čísla jsou 1, 3 a 5. Sudá čísla jsou 2, 4 a 6. 

Úkol je rozdělen do sedmi samostatných bloků a každý blok sestává z dvanácti kol. V každém kole budete hádat výsledek jednoho hodu kostkou. Bloky se odlišují pravidly, dle nichž budete hádat hody kostkou. Pravidla níže však platí pro všech sedm bloků.

Uhodnete-li první hod v daném bloku, získáte 5 Kč, uhodnete-li další, získáte za něj dalších 10 Kč, uhodnete-li další hod, získáte za něj dalších 15 Kč a tak dále. Za každý další uhodnutý hod získáte navíc částku o 5 Kč vyšší, než byla předchozí odměna. Pokud tedy uhodnete všech 12 hodů v daném bloku, za poslední dvanáctý uhodnutý hod získáte 60 Kč a celkem získáte 390 Kč.

Po skončení studie bude jeden blok náhodně vylosován. Obdržíte peníze, které jste vydělali pouze v tomto vylosovaném bloku. Pokud správně uhodnete všech dvanáct hodů v daném bloku, a tento blok bude později vylosován, obdržíte 390 Kč. Vaše výsledky v ostatních blocích nijak neovlivní množství peněz, které obdržíte.

Při obdržení odměny za dnešní studii Vám bude vyplacena celková suma za všechny části studie. Experimentátor, který Vám bude vyplácet odměnu, neuvidí, kolik jste vyhráli v jednotlivých částech studie a kolik peněz díky Vám obdržela charita. 

Abychom ověřili, že rozumíte instrukcím, prosím odpovězte na následující otázku:
Když správně uhodnete 7 hodů z 12 v prvním bloku, 5 hodů z 12 ve druhém bloku, 2 hody z 12 ve třetím bloku, 8 hodů ve čtvrtém bloku a poté je vylosován třetí blok, kolik peněz obdržíte?
"""

wrong_answer = "{} Kč je chybná odpověď, správná odpověď je 15 Kč. Byl vylosován třetí blok, ve kterém jste správně uhodli 2 hody. Obdržíte tedy 5 + 10 = 15 Kč."
correct_answer = "15 Kč je správná odpověď. Byl vylosován třetí blok, ve kterém jste správně uhodli 2 hody. Obdržíte tedy 5 + 10 = 15 Kč."



intro_block_2 = """
Toto je konec prvního bloku. Pokud bude tento blok vylosován, obdržíte {} Kč. Nyní začne druhý blok s dvanácti koly.
"""

endtext = """Toto je konec posledního bloku. Pokud bude tento blok vybrán, obdržíte {} Kč

Toto je konec úkolu s kostkou.
"""




perception_intro = """Nyní odpovězte na několik otázek týkající se volby."""


################################################################################




class Cheating(ExperimentFrame):
    def __init__(self, root):
        super().__init__(root)

        #######################
        # adjustable parameters
        self.trials = 12 if not TESTING else 2
        self.pause_after_roll = 0.5
        self.pause_before_trial = 0.2
        self.displayNum = self.createDots # self.createDots or self.createText
        self.fakeRolling = not TESTING
        self.diesize = 240
        self.rewards = [i*5 + 5 for i in range(self.trials)]
        self.endowment = 100
        #######################

        if not "block" in self.root.status:
            self.root.status["block"] = 1
            conditions = ["treatment", "control"]
            random.shuffle(conditions)  
            conditions += ["treatment"]
            self.root.status["conditions"] = conditions
        self.blockNumber = self.root.status["block"]      
        
        self.condition = self.root.status["conditions"][self.blockNumber - 1]

        self.width = self.root.screenwidth
        self.height = self.root.screenheight

        self.file.write("Cheating {}\n".format(self.blockNumber))

        self.upperText = Text(self, height = 5, width = 60, relief = "flat", font = "helvetica 15",
                              wrap = "word")
        self.upperButtonFrame = Canvas(self, highlightbackground = "white", highlightcolor = "white",
                                       background = "white", height = 100)
        self.die = Canvas(self, highlightbackground = "white", highlightcolor = "white",
                          background = "white", width = self.diesize, height = self.diesize)
        self.bottomText = Text(self, height = 3, width = 60, relief = "flat", font = "helvetica 15",
                               wrap = "word")
        self.bottomButtonFrame = Canvas(self, highlightbackground = "white", highlightcolor = "white",
                                        background = "white", height = 100)

        self.infoWinnings = ttk.Label(self, text = "", font = "helvetica 15",
                                      background = "white", justify = "right")
        self.fillerLeft = Canvas(self, highlightbackground = "white", highlightcolor = "white",
                                 background = "white", width = 200, height = 1)
        self.fillerRight = Canvas(self, highlightbackground = "white", highlightcolor = "white",
                                  background = "white", width = 200, height = 1)
        self.infoWinnings.grid(row = 1, column = 2, sticky = NW)
        self.fillerLeft.grid(column = 0, row = 0)
        self.fillerRight.grid(column = 2, row = 0)

        self.upperText.grid(column = 1, row = 1)
        self.upperButtonFrame.grid(column = 1, row = 2)
        self.die.grid(column = 1, row = 3, pady = 40)
        self.bottomText.grid(column = 1, row = 4)
        self.bottomButtonFrame.grid(column = 1, row = 5)
        self._createFiller()

        self["highlightbackground"] = "white"
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.rowconfigure(0, weight = 3)
        self.rowconfigure(1, weight = 1)
        self.rowconfigure(2, weight = 1)
        self.rowconfigure(3, weight = 1)
        self.rowconfigure(4, weight = 1)
        self.rowconfigure(5, weight = 1)
        self.rowconfigure(6, weight = 4)

        self.currentTrial = 0

        ttk.Style().configure("TButton", font = "helvetica 15")

        if not hasattr(self.root, "wins"):
            self.root.wins = defaultdict(int)    

        self.responses = []


    def run(self):
        self.bottomText["state"] = "disabled"
        self.upperText["state"] = "disabled"
        if self.currentTrial < self.trials:
            self.currentTrial += 1
            self.startTrial()
        else:
            self.root.texts["win" + str(self.blockNumber)] = sum(self.rewards[:self.root.wins[self.blockNumber]])
            if self.blockNumber == 4: # pocet bloku
                win = random.randint(1, 4)
                self.root.texts["dice"] = self.root.texts["win{}".format(win)]
                self.root.texts["block"] = win
            self.nextFun()


    def startTrial(self):
        self.time = perf_counter()
        self.showWinnings()
        self.upperPart()


    def _createFiller(self):
        self.fillerFrame = Canvas(self.bottomButtonFrame, highlightbackground = "white",
                                  highlightcolor = "white", background = "white", height = 100, width = 1)
        self.fillerFrame.grid(column = 0, row = 0, sticky = NS)


    def upperPart(self):
        self.upperText["state"] = "normal"
        if "treatment" in self.condition:
            ttk.Style().configure("TCheckbutton", background = "white", font = "helvetica 15")
            self.predictionVar = BooleanVar()
            self.predictionVar.set(False)
            self.upperText.insert("1.0", treatmenttext.format(self.blockNumber, self.currentTrial))
            self.predictedCB = ttk.Checkbutton(self.upperButtonFrame, text = predictiontext,
                                               command = self.checkbuttoned, variable = self.predictionVar,
                                               onvalue = True, offvalue = False)
            self.predictedCB.grid(row = 0, column = 1, pady = 15)
        elif "control" in self.condition:
            ttk.Style().configure("TRadiobutton", background = "white", font = "helvetica 15")
            self.predictionVar = StringVar()
            self.upperText.insert("1.0", controltext.format(self.blockNumber, self.currentTrial))
            self.evenButton = ttk.Radiobutton(self.upperButtonFrame, text = eventext, value = "even",
                                              variable = self.predictionVar, command = self.checked)
            self.oddButton = ttk.Radiobutton(self.upperButtonFrame, text = oddtext, value = "odd",
                                             variable = self.predictionVar, command = self.checked)
            self.evenButton.grid(row = 0, column = 2, padx = 10, pady = 15)
            self.oddButton.grid(row = 0, column = 0, padx = 10, pady = 15)

        self.rollButton = ttk.Button(self.upperButtonFrame, text = rolltext, command = self.roll,
                                     state = "disabled")
        self.rollButton.grid(row = 1, column = 1)
        self.upperText["state"] = "disabled"


    def checked(self):
        self.rollButton["state"] = "!disabled"


    def checkbuttoned(self):
        self.rollButton["state"] = "!disabled"
        self.predictedCB["state"] = "disabled"


    def bottomPart(self):
        self.bottomText["state"] = "normal"
        if "treatment" in self.condition:
            reward = self.rewards[self.root.wins[self.blockNumber]]
            text = treatmenttext2.format(reward)
            self.bottomText.insert("1.0", text)
            ttk.Style().configure("Green.TButton", foreground = "green")
            ttk.Style().configure("Red.TButton", foreground = "red")
            self.winButton = ttk.Button(self.bottomButtonFrame, text = correcttext,
                                        command = lambda: self.answer("win"), width = 18, style = "Green.TButton")
            self.lossButton = ttk.Button(self.bottomButtonFrame, text = incorrecttext,
                                         command = lambda: self.answer("loss"), width= 18, style = "Red.TButton")
            self.winButton.grid(row = 0, column = 0, padx = 30)
            self.lossButton.grid(row = 0, column = 2, padx = 30)
        elif "control" in self.condition:
            win = (self.response == "odd" and self.currentRoll in (1,3,5)) or (
                self.response == "even" and self.currentRoll in (2,4,6))
            if win:
                text = wintext.format(self.rewards[self.root.wins[self.blockNumber]])
                self.root.wins[self.blockNumber] += 1
            else:
                text = losstext.format(self.rewards[self.root.wins[self.blockNumber]])
            self.bottomText.insert("1.0", controltext2.format(text))
            self.showWinnings()
            self.continueButton = ttk.Button(self.bottomButtonFrame, text = continuetext, command = self.answer)
            self.continueButton.grid(row = 0, column = 1)
        self.bottomText["state"] = "disabled"


    def roll(self):
        self.firstResponse = perf_counter()
        if "treatment" in self.condition:
            self.response = "NA"    
        else:
            self.response = self.predictionVar.get()
            self.oddButton["state"] = "disabled"
            self.evenButton["state"] = "disabled"
        self.rollButton["state"] = "disabled"
        self.die.create_rectangle((5, 5, self.diesize - 5, self.diesize - 5),
                                  fill = "white", tag = "die", outline = "black", width = 5)
        # fake rolling
        if self.fakeRolling:
            for roll in range(random.randint(4,6)):         
                self.displayNum(self.diesize/2, self.diesize/2, random.randint(1, 6))
                self.update()
                sleep(0.2)
                self.die.delete("dots")
        self.currentRoll = random.randint(1, 6)
        self.displayNum(self.diesize/2, self.diesize/2, self.currentRoll)
        self.update()
        if not TESTING:
            sleep(self.pause_after_roll)
        self.beforeSecondResponse = perf_counter()
        self.bottomPart()


    def createDots(self, x0, y0, num):
        positions = {"1": [(0,0)],
                     "2": [(-1,-1), (1,1)],
                     "3": [(-1,-1), (0,0), (1,1)],
                     "4": [(-1,-1), (-1,1), (1,-1), (1,1)],
                     "5": [(-1,-1), (-1,1), (0,0), (1,-1), (1,1)],
                     "6": [(-1,-1), (-1,1), (1,-1), (1,1), (-1,0), (1,0)]}
        for x, y in positions[str(num)]:
            d = self.diesize/4
            coords = [x0 + x*d + d/3, y0 - y*d + d/3,
                      x0 + x*d - d/3, y0 - y*d - d/3]
            self.die.create_oval(tuple(coords), fill = "black", tag = "dots")


    def createText(self, x0, y0, num):
        self.die.create_text(x0, y0, text = str(num), font = "helvetica 70", tag = "die")

    def showWinnings(self):
        wins = self.root.wins[self.blockNumber]        
        self.infoWinnings["text"] = "Počet správných odhadů:\n{}".format(wins)        
        self.infoWinnings["text"] += "\n\nVaše současná výhra:\n{} Kč".format(sum(self.rewards[:wins]))

    def answer(self, answer = "NA"):
        t = perf_counter()
        if answer == "win":
            self.root.wins[self.blockNumber] += 1
        self.responses.append([self.blockNumber, self.currentTrial, self.condition, self.root.status["source"], 
                               self.root.status["condition"], self.currentRoll, self.response, answer, 
                               sum(self.rewards[:self.root.wins[self.blockNumber]]), t - self.time, self.firstResponse - self.time,
                               t - self.beforeSecondResponse])
        self.bottomText["state"] = "normal"
        self.upperText["state"] = "normal"
        self.die.delete("die")
        self.die.delete("dots")
        self.upperText.delete("1.0", "end")
        self.bottomText.delete("1.0", "end")
        for child in self.upperButtonFrame.winfo_children():
            child.grid_remove()
        for child in self.bottomButtonFrame.winfo_children():
            child.grid_remove()
        self._createFiller()
        self.showWinnings()
        self.update()
        sleep(self.pause_before_trial)
        self.run()
        
                   
    def write(self):
        self.root.status["block"] += 1
        for response in self.responses:
            begin = [self.id]
            self.file.write("\t".join(map(str, begin + response)) + "\n")

    
    def nextFun(self):
        if self.blockNumber == 3: # send the results of the after version in the third round            
            wins = self.root.wins[self.blockNumber]
            reward = sum(self.rewards[:self.root.wins[self.blockNumber]])
            outcome = "|".join(["outcome", str(wins), str(reward)]) 
            while True:
                data = urllib.parse.urlencode({'id': self.id, 'round': self.blockNumber, 'offer': outcome})
                data = data.encode('ascii')
                if URL == "TEST":
                    self.root.texts["testOutcome"] = self.root.status["number"] + outcome.lstrip("outcome")
                    response = "ok"
                else:
                    try:
                        with urllib.request.urlopen(URL, data = data) as f:
                            response = f.read().decode("utf-8")       
                    except Exception:
                        continue
                if response == "ok":                    
                    super().nextFun()  
                    return            
                sleep(0.1)
        else:
            super().nextFun()  


    def gothrough(self):
        # nefunguje :(
        self.run()
       
        if "treatment" in self.condition:
            self.predictedCB.invoke()
            self.after(200, self.rollButton.invoke)
            self.after(200, self.winButton.invoke)
            #self.root.update()
            #self.after(500, self.update)
            #answer = random.choice([self.winButton, self.lossButton])
            #self.after(700, answer.invoke)
        elif "control" in self.condition:
            answer = random.choice([self.evenButton, self.oddButton])
            answer.invoke()            
            self.after(200, self.rollButton.invoke)
            self.update()
            self.after(200, self.continueButton.invoke)
            #self.root.update()
            #self.after(700, self.continueButton.invoke)



    
    

class CheatingInstructions(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = intro_block_1, height = 33, font = 15, width = 100)

        self.checkVar = StringVar()
        self.vcmd = (self.register(self.onValidate), '%P')
        self.checkFrame = Canvas(self, background = "white", highlightbackground = "white",
                                 highlightcolor = "white")
        self.checkFrame.grid(row = 2, column = 1)
        self.entry = ttk.Entry(self.checkFrame, textvariable = self.checkVar, width = 10, justify = "right",
                               font = "helvetica 15", validate = "key", validatecommand = self.vcmd)
        self.entry.grid(row = 2, column = 1, padx = 6)
        self.currencyLabel = ttk.Label(self.checkFrame, text = "Kč", font = "helvetica 15",
                                       background = "white")
        self.currencyLabel.grid(row = 2, column = 2, sticky = NSEW)

        self.lowerText = Text(self, font = "helvetica 15", relief = "flat", background = "white",
                              width = 100, height = 2, wrap = "word", highlightbackground = "white")
        self.lowerText.grid(row = 3, column = 1, pady = 15)
        self.lowerText["state"] = "disabled"
        
        self.next.grid(row = 7, column = 1)
        self.next["state"] = "disabled"
        self.text.grid(row = 1, column = 1, columnspan = 1)

        self.rowconfigure(0, weight = 1)
        self.rowconfigure(2, weight = 0)
        self.rowconfigure(3, weight = 0)
        self.rowconfigure(7, weight = 1)
        self.rowconfigure(8, weight = 2)

        self.checked = False
        
    def onValidate(self, P):
        try:
            if int(P) >= 0:
                self.next["state"] = "!disabled"
            else:
                self.next["state"] = "disabled"
        except Exception as e:
            self.next["state"] = "disabled"
        return True
    
    def nextFun(self):
        if self.checked:
            super().nextFun()
        else:
            answer = int(self.checkVar.get())
            if answer == 15:
                text = correct_answer.format(answer)
            else:
                text = wrong_answer.format(answer)
            self.lowerText["state"] = "normal"
            self.lowerText.insert("1.0", text)
            self.lowerText["state"] = "disabled"
            self.checked = True

    def gothrough(self):
        self.entry.focus_set()
        self.event_generate('<KeyPress-1>')
        self.event_generate('<KeyPress-5>')
        self.after(500, self.next.invoke)
        self.after(500, self.next.invoke)




class Instructions3(InstructionsAndUnderstanding):
    def __init__(self, root):
        # for testing
        if TESTING and not "win2" in root.texts:
            root.texts["win2"] = 150            

        controlTexts = [[control1, answers1, feedback1], [control2, answers2, feedback2]]
        super().__init__(root, controlTexts = controlTexts, text = intro_third, height = 25, font = 15, width = 100, update = ["win2", "condition", "source"])








class Voting(InstructionsFrame):
    def __init__(self, root):
        # for testing
        if not "block" in root.status: 
            root.status["block"] = 1
        if TESTING and not "outcome" in root.texts:
            root.texts["outcome"] = "outcome_1|1|5_2|3|30_3|12|390_4|10|275_True"

        super().__init__(root, text = root.texts["intro_block_4"], height = 20, font = 15, update = ["win3"])

        # vote frame
        self.voteVar = StringVar()
        self.voteFrame = Canvas(self, background = "white", highlightbackground = "white", highlightcolor = "white")
        
        self.labs = {}
        self.radios = {}
        self.wins = {}

        self.playerHead = ttk.Label(self.voteFrame, text = "Hráč", font = "helvetica 15 bold", background = "white")
        self.playerHead.grid(row = 0, column = 1, pady = 10, padx = 20, sticky = W)
        self.winHead = ttk.Label(self.voteFrame, text = "Výhra", font = "helvetica 15 bold", background = "white")
        self.winHead.grid(row = 0, column = 2, pady = 10, padx = 20, sticky = E)
        self.radioHead = ttk.Label(self.voteFrame, text = "Volba", font = "helvetica 15 bold", background = "white")
        self.radioHead.grid(row = 0, column = 3, pady = 10, padx = 20)
        
        ttk.Style().configure("TRadiobutton", background = "white", font = "helvetica 15")
        for i in range(4):
            you = i + 1 == int(self.root.status["number"])
            player = "Hráč " + str(i + 1) if not you else "Vy"
            self.labs[i] = ttk.Label(self.voteFrame, text = player, font = "helvetica 15", background = "white")
            self.labs[i].grid(row = i + 1, column = 1, sticky = W, padx = 20)
            win = self.root.texts["outcome"].split("_")[i+1].split("|")[2]
            self.wins[i] = ttk.Label(self.voteFrame, text = win, font = "helvetica 15", background = "white")
            self.wins[i].grid(row = i + 1, column = 2, padx = 20, sticky = E)
            state = "disabled" if you else "normal"
            self.radios[i] = ttk.Radiobutton(self.voteFrame, text = "", variable = self.voteVar, value = str(i + 1), command = self.voted, state = state)
            self.radios[i].grid(row = i + 1, column = 3, padx = 20)
                            
        self.voteFrame.grid(row = 4, column = 1)
        self.next.grid(row = 5, column = 1, sticky = N)
        self.next["state"] = "disabled"
   
        self.rowconfigure(0, weight = 2)
        self.rowconfigure(6, weight = 2)        


    def voted(self):
        self.next["state"] = "!disabled"

    def nextFun(self):
        self.write()
        super().nextFun()
 
    def write(self):
        self.root.texts["votingResponse"] = self.voteVar.get()

        self.file.write("Voting\n")
        self.file.write(self.id + "\t" + str(self.root.status["block"]) + "\t" + self.voteVar.get() + "\t" + "\n\n")

        data = urllib.parse.urlencode({'id': self.id, 'round': self.root.status["block"], 'offer': self.voteVar.get()})
        data = data.encode('ascii')
        if URL != "TEST":
            for i in range(60):
                try: 
                    with urllib.request.urlopen(URL, data = data) as f:
                        if f.getcode() != 200 or f.read().decode("utf-8").strip() != "ok":
                            self.root.config(cursor = "wait")
                            self.root.update()
                            sleep(1)
                        else:
                            self.root.config(cursor = "")
                            break
                except Exception:
                    continue
            else:
                messagebox.showinfo(message = "Zavolejte prosím experimentátora.", icon = "error", parent = self.root, 
                                  detail = "Pravděpodobně je problém se serverem.", title = "Problém")
        else:
            self.root.status["TESTvote"] = self.voteVar.get()




class Perception(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = perception_intro, height = 20, font = 15)

        # TO DO





class Wait(InstructionsFrame):
    def __init__(self, root, what = "voting"):
        super().__init__(root, text = wait_text, height = 3, font = 15, proceed = False, width = 45)
        self.what = what
        self.progressBar = ttk.Progressbar(self, orient = HORIZONTAL, length = 400, mode = 'indeterminate')
        self.progressBar.grid(row = 2, column = 1, sticky = N)

    def checkOffers(self):
        count = 0
        while True:
            self.update()
            if count % 50 == 0:
                if self.what == "voting":
                    data = urllib.parse.urlencode({'id': self.id, 'round': self.root.status["block"], 'offer': "voting"})
                elif self.what == "outcome":
                    data = urllib.parse.urlencode({'id': self.id, 'round': self.root.status["block"], 'offer': "outcome"})
                data = data.encode('ascii')
                if URL == "TEST":
                    if self.what == "voting":
                        myvote = int(self.root.status["TESTvote"])
                        # pridat pocitacni hlasu
                        maxvotes = random.randint(1, 4)
                        votes = random.randint(1, 3)
                        condition = "treatment" if maxvotes == self.root.status["number"] else "control"
                        response = "_".join([condition, str(maxvotes), str(votes)])
                    elif self.what == "outcome":                                                
                        response = "outcome"
                        for i in range(4):
                            if i + 1 == int(self.root.status["number"]):
                                response += "_" + self.root.texts["testOutcome"]
                            else:
                                outcome = random.randint(0,12)                 
                                response += "_" + "|".join([str(i + 1), str(outcome), str(sum([i*5 + 5 for i in range(12)][:outcome]))]) 
                        response += "_True"
                else:
                    try:
                        with urllib.request.urlopen(URL, data = data) as f:
                            response = f.read().decode("utf-8")       
                    except Exception as e:
                        pass
                if response:                  
                    if self.what == "voting":
                        condition, maxvotes, votes = response.split("_")         
                        if maxvotes == "0":
                            continue  
                        self.root.status["conditions"].append(condition)                        
                        self.updateResults(maxvotes, votes)
                        self.write(response)
                    elif self.what == "outcome":   
                        if not response.endswith("True"):
                            continue
                        else:
                            self.root.texts["outcome"] = response
                    self.progressBar.stop()
                    self.nextFun()  
                    return
            count += 1
            sleep(0.1)

    def run(self):
        self.progressBar.start()
        self.checkOffers()

    def updateResults(self, maxvotes, votes):                
        if maxvotes == self.root.status["number"]:
            self.root.texts["voting_result_text"] = voting_you + members[int(votes) - 1]
        else:
            self.root.texts["voting_result_text"] = voting_other.format(maxvotes) + members[int(votes) - 1]

    def write(self, response):
        self.file.write("Voting Result" + "\n")
        self.file.write(self.id + "\t" + str(self.root.status["block"]) + "\t" + response.replace("_", "\t") + "\n\n")          
            

class Login(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = "Počkejte na spuštění experimentu", height = 3, font = 15, width = 45, proceed = False)

        self.progressBar = ttk.Progressbar(self, orient = HORIZONTAL, length = 400, mode = 'indeterminate')
        self.progressBar.grid(row = 2, column = 1, sticky = N)

    def login(self):        
        count = 0
        while True:
            self.update()
            if count % 50 == 0:            
                data = urllib.parse.urlencode({'id': self.root.id, 'round': 0, 'offer': "login"})
                data = data.encode('ascii')
                if URL == "TEST":
                    response = "_".join(["start", random.choice(["others_kept", "charity_kept", "charity_divided", "experimenter_kept", "experimenter_divided"]), str(random.randint(1,4))])
                else:
                    response = ""
                    try:
                        with urllib.request.urlopen(URL, data = data) as f:
                            response = f.read().decode("utf-8") 
                    except Exception:
                        self.changeText("Server nedostupný")
                if "start" in response:
                    info, source, condition, number = response.split("_")                    
                    self.root.status["source"] = source
                    self.root.status["condition"] = condition                    
                    self.root.status["number"] = number
                    self.update_intro(source, condition)
                    self.progressBar.stop()
                    self.write(response)
                    self.nextFun()                      
                    break
                elif response == "login_successful" or response == "already_logged":
                    self.changeText("Přihlášen")
                elif response == "ongoing":
                    self.changeText("Do studie se již nelze připojit")
                elif response == "no_open":
                    self.changeText("Studie není otevřena")
                elif response == "closed":
                    self.changeText("Studie je uzavřena pro přihlašování")
                elif response == "not_grouped":
                    self.changeText("Nebyla Vám přiřazena žádná skupina. Zavolejte prosím experimentátora zvednutím ruky.")
            count += 1                  
            sleep(0.1)        

    def run(self):
        self.progressBar.start()
        self.login()

    def update_intro(self, source, condition):
        source = {"others": condition_others, "charity": condition_charity, "experimenter": ""}[source]
        condition = {"divided": condition_divided, "kept": ""}[condition]
        self.root.texts["condition"] = condition
        self.root.texts["source"] = source
        self.root.texts["intro_block_4"] = intro_voting.format("{}", condition, source)

    def write(self, response):
        self.file.write("Login" + "\n")
        self.file.write(self.id + response.replace("_", "\t").lstrip("start") + "\n\n")        

    def gothrough(self):
        self.run()




Instructions2 = (InstructionsFrame, {"text": intro_block_2, "height": 5, "update": ["win1"]})
#Instructions3 = (InstructionsFrame, {"text": intro_third, "height": 30, "update": ["win2", "condition", "source"]})
VotingResult = (InstructionsFrame, {"text": voting_result, "height": 3, "update": ["voting_result_text"]})
EndCheating = (InstructionsFrame, {"text": endtext, "height": 5, "update": ["win4"]})
OutcomeWait = (Wait, {"what": "outcome"})




if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([Login,
         Instructions3, # odstranit
         CheatingInstructions,
         Cheating,
         Instructions2,
         Cheating,
         Instructions3,
         Cheating,
         OutcomeWait,
         Voting,
         Perception,
         Wait,
         VotingResult,
         Cheating,         
         EndCheating
         ])
