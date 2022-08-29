import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import scrolledtext

BACK_COL = "lightgray"

class GUI:
    def __init__(self, manager, domainFileName=None, problemFileName=None):
        self.win = tk.Tk()
        self.manager = manager
        self.win.configure(bg=BACK_COL)
        self.win.title("PDDL Checker")
        self.win.geometry("1080x720")
        
        self.createGUI()
        
        
        if domainFileName:
            self.loadFilePDDL(domainFileName, self.domainText)
        if problemFileName:
            self.loadFilePDDL(problemFileName, self.problemText)
        self.win.mainloop()
    
    
    def createGUI(self):
        ##Configure GRID:
            #Columns
        self.win.columnconfigure(0, weight=1)
        self.win.columnconfigure(1, weight=10)
        self.win.columnconfigure(2, weight=2)
        self.win.columnconfigure(3, weight=10)
        self.win.columnconfigure(4, weight=1)
            #Rows
        self.win.rowconfigure(0,weight=1)
        self.win.rowconfigure(1,weight=10)
        self.win.rowconfigure(2,weight=2)
        
        ##Create and configure Scroll TEXTS:
            #Domain scroll Text area
        self.domainText = scrolledtext.ScrolledText(self.win)
        self.domainText.grid(column=1,row=1,sticky="nsew")
        self.domainText.tag_config("error", foreground="red")
        
            #Problem scroll Text area
        self.problemText = scrolledtext.ScrolledText(self.win)
        self.problemText.grid(column=3,row=1,sticky="nsew")
        self.problemText.config(state=DISABLED)
        self.problemText.tag_config("error", foreground="red")
        
        ##Create and configure Buttons
            #loading domain button
        self.buttonLoadDomain = Button(self.win,text="Open domain PDDL", 
                command= lambda: self.openFilePDDL("Open PDDL domain", self.domainText))
        self.buttonLoadDomain.grid(column=1,row=0)
            #loading problem button
        self.buttonLoadProblem = Button(self.win,text="Open problem PDDL",
               command=lambda: self.openFilePDDL("Open PDDL problem", self.problemText))
        self.buttonLoadProblem.grid(column=3,row=0)
            #Correct button
        self.buttonCorrect = Button(self.win,text="Correct", 
               command=lambda: self.correct())
        self.buttonCorrect.grid(column=1,row=2,columnspan=3)
        
        ## Create Label for Error in Domain and problem
        self.DomainVarText = StringVar()
        self.domainLabel = Label(self.win, textvariable = self.DomainVarText, bg=BACK_COL, fg="green")
        self.domainLabel.grid(column=1,row=2)
        
        self.ProblemVarText = StringVar()
        self.problemLabel = Label(self.win, textvariable = self.ProblemVarText, bg=BACK_COL, fg="yellow")
        self.problemLabel.grid(column=3,row=2)
        
        ## Create Output for console
        self.console = scrolledtext.ScrolledText(self.win)
        self.problemText.config(state=DISABLED)
    
    def loadFilePDDL(self, path, area):
        tf = open(path)
        data = tf.read()
        self.activeText(area)
        #Ripulisci
        area.delete(0.0, END)
        #Scrivi
        area.insert(INSERT, data)
        self.activeText(area,False)
        tf.close()
    
    def openFilePDDL(self, title, area):
        tf = filedialog.askopenfilename(
            initialdir="C:/Users/MainFrame/Desktop/", 
            title=title, 
            filetypes=(("PDDL Files", "*.pddl"),("Text Files", "*.txt"))
            )
        self.loadFilePDDL(tf, area)
    
    def activeText(self, area, active=True):
        if active:
            area.config(state=NORMAL)
        else:
            area.config(state=DISABLED)
    
    def correct(self):
        self.manager.check(self.domainText.get(1.0, END), self.problemText.get(1.0, END))
        self.DomainVarText.set("Domain is correct")
        self.domainLabel.configure(fg="blue")
        self.ProblemVarText.set("Problem is correct")
    
    def reset_tag(area):
        for tag in area.tag_names():
            area.tag_remove(tag, "1.0", "end")
    
    def error_word(self, word, line, area): #line=str(a)+".0"
        countVar = IntVar()             # contain the number of chars that matched
        searched_position = area.search(pattern=word, index=line, 
                                                stopindex=self.endindex, count=countVar)
        endindex = "{}+{}c".format(searched_position, countVar.get())   #add index+length of word/pattern
        area.tag_add("error", searched_position, endindex)
        
'''
class CmdThread (threading.Thread):
   def __init__(self, command, textvar):
        threading.Thread.__init__(self)
        self.command = command
        self.textvar = textvar

   def run(self):
        proc = subprocess.Popen(self.command, stdout=subprocess.PIPE)
        while not proc.poll():
            data = proc.stdout.readline()
            if data:
                print(data)
                self.textvar.set(data)
            else:
                break
'''

#GUI()