#PYxis: Quaich 2016 - 2017

#setup
#Importing modules
from tkinter import * #enables use of the Tkinter UI, responsible for drawing of objects and generation of GUI
from tkinter import filedialog #Cannot run without this unless in IDLE
from tkinter.colorchooser import *
import time #needed for restriction of refresh rate (may not be needed)
import math #needed for physics calculation
import random #for some more "fun" parts of the program.

#constants
G = 6.6741  #simplfied
H = True
#2d arrays
OBD = [] #2D dictionary for planet variables
poplist = []
anchorlist = []
edu = False
if H==True:
    H=True
name = print("Hello")

def main():
    for planet1 in range(0,len(OBD)): #for more than one object
        if planet1 not in anchorlist:
            objectxy = [((OBD[planet1]["x0"]+OBD[planet1]["x1"])/2),((OBD[planet1]["y0"]+OBD[planet1]["y1"])/2)]
            for planet2 in range(0,len(OBD)):
                if planet2 != planet1:
                    object2xy = [((OBD[planet2]["x0"]+OBD[planet2]["x1"])/2),((OBD[planet2]["y0"]+OBD[planet2]["y1"])/2)]
                    if object2xy != objectxy:
                        ###Essentialy the collision detection###
                        radius,theta,xn,yn = maths(objectxy,object2xy)
                        if colide(planet1,planet2,radius) == True:
                            if OBD[planet1]["radius"] >= OBD[planet2]["radius"] and planet2 not in poplist: #condense this bit
                                tbd = planet2
                                tbnd = planet1
                                OBD[planet1]["mass"] += OBD[planet2]["mass"]
                                OBD[planet1]["planetsdevoured"] += 1
                            elif OBD[planet2]["radius"] >= OBD[planet1]["radius"] and planet1 not in poplist:
                                tbd = planet1
                                tbnd = planet2
                                OBD[planet2]["mass"] += OBD[planet1]["mass"]
                                OBD[planet2]["planetsdevoured"] += 1

                            try:
                                if tbd not in poplist and tbnd not in poplist:
                                    poplist.append(tbd)
                            except UnboundLocalError:
                                pass
                            ui.window.lower("star")
                            break
                        Euler(objectxy,object2xy,planet1,planet2,OBD,ui.speed)
            OBD[planet1]["lx"] = objectxy [0]
            OBD[planet1]["ly"] = objectxy [1]

def maths(objectxy,object2xy):
    a = int(objectxy[0] - object2xy[0])
    b = int(objectxy[1] - object2xy[1])
    radius = math.sqrt((a**2) + (b**2)) #Pythagorus theorem
    if radius != 0:
        if a == 0:
            theta = 0 #change in x is 0 and we dont want an error to be thrown.
        else:
            theta = abs(math.atan(b/a))
    else:
        theta = 0
    if -1 < radius < 1:
        radius = 1 #no div by 0
    if b > 0:
        yn = True
    else:
        yn = False
    if a > 0:
        xn = True
    else:
        xn = False
    return(radius,theta,xn,yn)

def physics(planet1,planet2,objectxy,object2xy,OBD,speed):
    radiusbetweenplanets,theta,xn,yn = maths(objectxy,object2xy)
    if radiusbetweenplanets != 0:
        Fgrav = ((G*(int(OBD[planet1]["mass"])*(int(OBD[planet2]["mass"]))))/radiusbetweenplanets**2) / OBD[planet1]["mass"]
        accelerationx = Fgrav*math.cos(theta)
        accelerationy = Fgrav*math.sin(theta)
        if xn == True:
            accelerationx = -(accelerationx)
        if yn == True:
            accelerationy = -(accelerationy)

        cspeed = (speed.get()/1000)
        #Resolving (Right) (positive x)
        vx = accelerationx*cspeed #Mass is not used here because it results in a more "exaggerated" but more workable interactions.
        vy = accelerationy*cspeed #Essentially removes the need for larger numbers.
        #Resolving (Down) (positive y)

        #arrow for educationmode#

        if edu == True and ui.planetselected == planet1:
            widthofline = abs((abs(vx) + abs(vy))*500)
            if widthofline > 20:
                widthofline = 20
            line = ui.window.create_line(objectxy[0],objectxy[1],object2xy[0],object2xy[1],width = widthofline,fill = "White",tag="educat",arrow="last")
            ui.window.lower(line) #correct the ordering of objects.
            ui.window.lower("oval")
            ui.window.lower("t")
            ui.window.lower("star")
        return(vx,vy)

def Euler(objectxy,object2xy,planet1,planet2,OBD,speed):
    prevxy = objectxy
    vx,vy = physics(planet1,planet2,objectxy,object2xy,OBD,speed)
    OBD[planet1]["dx"] += vx
    OBD[planet1]["dy"] += vy

def createplanet(rad,mass,x,y,R,G,B,cx,cy,theta,undo,id):
    global OBD
    OBD.append({"x0": x-rad,"y0": y-rad,"x1": x+rad, "y1": y+rad,"mass": mass,"RGB":('#%02x%02x%02x' % (int(R//1), int(G//1), int(B//1))),"dx":cx,"dy":cy,"lx":x,"ly":y,"radius":rad,"R":R,"G":G,"B":B,"planet":0,"alivetime":time.time(),"Theta":theta,"planetsdevoured":0})
    slot = (len(OBD)-1)
    OBD[slot]["planet"] = ui.window.create_oval(OBD[slot]["x0"],OBD[slot]["y0"],OBD[slot]["x1"],OBD[slot]["y1"],fill=(OBD[slot]["RGB"]),tags="oval")
    tba = ["A",OBD[slot]["planet"],OBD[slot]["x0"],OBD[slot]["y0"],OBD[slot]["x1"],OBD[slot]["y1"],OBD[slot]["mass"],OBD[slot]["RGB"],OBD[slot]["dx"],OBD[slot]["dy"],OBD[slot]["lx"],OBD[slot]["ly"],OBD[slot]["radius"],OBD[slot]["R"],OBD[slot]["G"],OBD[slot]["B"],OBD[slot]["planet"],OBD[slot]["alivetime"],OBD[slot]["Theta"],OBD[slot]["planetsdevoured"]]
    if undo == False:
        mainstack.push(tba)
    else:
        mainstack.replaceid(id,OBD[slot]["planet"])
    ui.window.lower("oval")
    ui.window.lower("star")

def deleteplanet(mod,undo):
    try:
        if not undo:
            tba = ["D",OBD[mod]["planet"],OBD[mod]["x0"],OBD[mod]["y0"],OBD[mod]["x1"],OBD[mod]["y1"],OBD[mod]["mass"],OBD[mod]["RGB"],OBD[mod]["dx"],OBD[mod]["dy"],OBD[mod]["lx"],OBD[mod]["ly"],OBD[mod]["radius"],OBD[mod]["R"],OBD[mod]["G"],OBD[mod]["B"],OBD[mod]["planet"],OBD[mod]["alivetime"],OBD[mod]["Theta"],OBD[mod]["planetsdevoured"]]
            mainstack.push(tba)
        poplist.append(mod)
        if mod in anchorlist:
            anchorlist.pop(anchorlist.index(mod))
        if mod == ui.planetselected:
            ui.window.delete("s")
            ui.planetselected = 0

    except IndexError:
        pass #deleting something that doesnt exist doesn't matter. Like wise, if the undo mod isnt found it will throw a IndexError.
def colide(planet1,planet2,radius):
    if radius <  OBD[planet2]["radius"] + OBD[planet1]["radius"]:
        if radius < OBD[planet2]["radius"]:
            ui.window.lower(OBD[planet2]["planet"])
        else:
            ui.window.lower(OBD[planet1]["planet"])
        return True
    else:
        return False

###UI Related subroutines###

def drawtrail(prevxy,objectxy,planet1):
    if 0 < objectxy[0] < 1000 and 0 < objectxy[1] < 1000: #no point drawing things the user wont see.
        trail = ui.window.create_line(prevxy[0],prevxy[1],objectxy[0],objectxy[1],fill=OBD[planet1]["RGB"],tags="t")
        ui.window.lower(trail)
        if ui.trailduration.get() != 20:
            ui.master.after(int((ui.trailduration.get())*1000),lambda:ui.window.delete(trail))

def playpause(colourc):
    if colourc == True:
        if ui.paused != True:
            ui.prevpaused = ui.paused
            ui.playp["text"] = " ► "
            ui.paused = True
    elif colourc ==  False:
        if ui.playp["text"] == "▐▐  ":
            ui.playp["text"] = " ► "
        else:
            ui.playp["text"] = "▐▐  "
        ui.paused = not ui.paused

def safetypause(colourc):
    if ui.paused == True:
        playpause(colourc)
        ui.tobepaused = False
    else:
        ui.tobepaused = True

def getcolour():
    ui.prevpaused = ui.paused
    if ui.paused == True:
        askcolour(ui.prevpaused)
        ui.tobepausedcolour = False
    else:
        ui.tobepausedcolour = True

def askcolour(prevpaused):
    ui.planetcolour = askcolor()
    try:
        x = ui.planetcolour [1][0]
    except TypeError:
        ui.planetcolour = ((255,0,0),"#FF0000")

###LOAD AND SAVE SYSTEM###
def load(quick):
    #variables to be edited#
    if quick == False:
        try:
            file = filedialog.askopenfilename(filetypes=[(".pyx Format","*.pyx")],title="Choose a file to load")
        except AttributeError:
            pass #User closed the window.
    else:
        file =".tmp.pyx"
    try:
        with open(file,'r') as load:
            temparray = []
            ##Reset Variables##
            systemname = ("PYxis - System: {}".format(file))
            ui.master.wm_title(systemname)
            ui.window.delete("t")
            ###Delete array###
            for lines in range(len(OBD)):
                deleteplanet(lines,False)
            popplanets()
            anchorlist = []
            ###set array to the file###
            lines = [line.split() for line in load]
            for line in range(0,len(lines)):
                temparray.append(lines[line])
            ui.window.delete("oval")
            ui.window.delete("s")
            ###convert to float###
            for y in range(0,len(temparray)):
                for x in range(len(temparray[y])):
                    try:
                        temparray[y][x] = float(temparray[y][x])
                    except ValueError:
                        pass #cant convert strings to float
        for lines in range(0,len(temparray)):
            createplanet(temparray[lines][10],temparray[lines][4],((temparray[lines][0]+temparray[lines][2])/2),((temparray[lines][1]+temparray[lines][3])/2),temparray[lines][11],temparray[lines][12],temparray[lines][13],temparray[lines][6],temparray[lines][7],0,False,0)
            if temparray[lines][17] == "True": #saves the data as string
                anchorlist.append(lines)
    except FileNotFoundError:
        print("FILE: No file was found.")
    except IndexError:
        print("FILE: Invalid File.")

def save(quick):
    global OBD
    if quick == True:
        file = open(".tmp.pyx","w")
    else:
        try:
            file = filedialog.asksaveasfile(filetypes=[(".pyx Format","*.pyx")],title="Choose a file to save",defaultextension=".gpy")
        except AttributeError:
            pass #User closed the window.
    for lines in range(len(OBD)):
        if lines in anchorlist:
            anchor = True
        else:
            anchor = False
        array = [OBD[lines]["x0"],OBD[lines]["y0"],OBD[lines]["x1"],OBD[lines]["y1"],OBD[lines]["mass"],OBD[lines]["RGB"],OBD[lines]["dx"],OBD[lines]["dy"],OBD[lines]["lx"],OBD[lines]["ly"],OBD[lines]["radius"],OBD[lines]["R"],OBD[lines]["G"],OBD[lines]["B"],OBD[lines]["alivetime"],OBD[lines]["Theta"],OBD[lines]["planetsdevoured"],anchor]
        for entitiy in array:
            file.write(str(entitiy))
            file.write(" ")
        file.write(" \n")
    file.close()

def popplanets():
    global poplist
    ##BUBBLESORT##
    for itterations in range(len(poplist)):
        for swaps in range(len(poplist)-1):     
            if poplist[swaps]<poplist[swaps+1]:
                poplist[swaps+1], poplist[swaps] = poplist[swaps],poplist[swaps+1]
    for planet in range(len(poplist)):
        try:
            ui.window.delete(OBD[poplist[planet]]["planet"])
            OBD.pop(poplist[planet])
        except TypeError:
            pass #planet was destroyed between actions due to the stack
    poplist = []

def selectobject(event):
    x = event.x
    y = event.y
    closest = ui.window.find_closest(x,y)
    try:
        if ui.window.gettags(closest)[0] == "oval":
            coords = ui.window.coords(closest)
            for planets in range(0,len(OBD)):
                if coords == [OBD[planets]["x0"],OBD[planets]["y0"],OBD[planets]["x1"],OBD[planets]["y1"]]:
                    ui.planetselected = planets
    except:
        pass #planet is unavailable
def deltrail():
    ui.window.delete("t")

def anchor():
    global anchorlist
    if ui.planetselected not in anchorlist:
        anchorlist.append(ui.planetselected)
    else:
        anchorlist.remove(ui.planetselected)

def educationmode():
    global edu
    if ui.education["text"] != "←":
        ui.education["text"] = "←"
    else:
        ui.education["text"] = "X"
    edu = not edu

class stack():
    def __init__(self,Maxlength,Maxwidth):
        self.StackArray = [["" for x in range(20)] for y in range(Maxlength)]#(Y,X) #2d array for planet variables and [0] to represent why it was added.
        self.StackMaximum = Maxlength -1
        self.StackPointer = -1
        self.CurrentData = []
        self.mod = 0
    def pop(self):
        if not self.isEmpty():
            self.CurrentData = self.StackArray[self.StackPointer]
            self.StackPointer += -1
    def push(self,Data):
        if not self.isFull():
            self.StackPointer += 1
            self.StackArray[self.StackPointer] = Data
    def peek(self):
        print(self.StackArray[self.StackPointer])
    def isFull(self):
        if self.StackPointer >= self.StackMaximum:
            return True
        else:
            return False
    def isEmpty(self):
        if self.StackPointer < 0:
            return True
        else:
            return False

    def printStack(self):
        print("------------------------------------------------------------------------------------------------")
        for y in range(len(self.StackArray)):
            if self.StackMaximum - y == self.StackPointer:
                print("→",self.StackArray[len(self.StackArray)-1 - y],"←")
            else:
                print("|",self.StackArray[len(self.StackArray)-1 - y],"|")

    def fetchposition(self):
        for x in range(len(OBD)):
            if OBD[x]["planet"] == self.StackArray[self.StackPointer][1]:
                return(x)
    def replaceid(self,oldid,newid):
        for x in range(len(self.StackArray)):
            if self.StackArray[x][1] == oldid:
                self.StackArray[x][1] = newid
    def undo(self):
        if self.isEmpty() == False:
            self.mod = self.fetchposition()
            if self.StackArray[self.StackPointer][0] == "A":
                deleteplanet(self.mod,True)
            if self.StackArray[self.StackPointer][0] == "D": 
                createplanet(self.StackArray[self.StackPointer][12],self.StackArray[self.StackPointer][6],(self.StackArray[self.StackPointer][2]+self.StackArray[self.StackPointer][4])/2,(self.StackArray[self.StackPointer][3]+self.StackArray[self.StackPointer][5])/2,self.StackArray[self.StackPointer][13],self.StackArray[self.StackPointer][14],self.StackArray[self.StackPointer][15],self.StackArray[self.StackPointer][8],self.StackArray[self.StackPointer][9],self.StackArray[self.StackPointer][18],True,self.StackArray[self.StackPointer][1])
        self.pop()
    def redo(self):
        if not self.isFull()and self.StackArray[self.StackPointer+1][0] != "":
            self.StackPointer += 1
            if self.StackArray[self.StackPointer][0] == "A":
                createplanet(self.StackArray[self.StackPointer][12],self.StackArray[self.StackPointer][6],(self.StackArray[self.StackPointer][2]+self.StackArray[self.StackPointer][4])/2,(self.StackArray[self.StackPointer][3]+self.StackArray[self.StackPointer][5])/2,self.StackArray[self.StackPointer][13],self.StackArray[self.StackPointer][14],self.StackArray[self.StackPointer][15],self.StackArray[self.StackPointer][8],self.StackArray[self.StackPointer][9],self.StackArray[self.StackPointer][18],True,self.StackArray[self.StackPointer][1])
            if self.StackArray[self.StackPointer][0] == "D":
                deleteplanet(self.mod,True)

mainstack = stack(1000,18)

class userinterface():
    def __init__(self):
        self.master = Tk() #master window
        self.window = Canvas(self.master, width=1200, height=1000) #generate 1200x1000 canvas
        self.master.resizable(width=False,height=False)
        self.window.pack() 

        try:
            self.master.iconbitmap("icon.ico")
        except TclError:
            print("INFO: Icon not found. Continuing..")

        #Basic UI elements#
        self.starttime = time.time()
        self.lasttime = self.starttime
        self.window.configure(background="Black") #Main background
        self.optionsbackground = self.window.create_rectangle(1001,0,1205,1000,fill="white") #white rectangle behind the options
        self.curtime = self.window.create_text(50,30,fill = "White") #Time running
        self.fps = self.window.create_text(150,30,fill = "White") #current FPS
        self.ox = 0
        self.oy = 0
        self.otime = time.time()
        #Pause related#
        self.tobepaused = False
        self.tobepausedcolour = False
        self.paused = False
        self.prevpaused = False
        self.playp = Button(self.master,text="▐▐  ", command =lambda:safetypause(False),font=("Helvetica", 12))
        self.playp.place(x=1130,y=120,width=30,height=27)

        #Delete trails#
        self.deltrailb = Button(self.master,text="Delete Trails",command=deltrail,fg="green",activeforeground="green")
        self.deltrailb.place(x=1040,y=120,width=80)

        #Planet colour chooser#
        self.planetcolour = ((255,0,0),"#FF0000") #default planetcolour
        self.colourchoose = Button(self.master,text="Select colour",command=lambda:getcolour())
        self.colourchoose.place(x=1040,y=300,width = 120)

        self.education = Button(self.master,text="←",command=educationmode)
        self.education.place(x=1075,y=90,width = 30)

        self.planetanchor = Button(self.master,text="⚓",command=anchor)
        self.planetanchor.place(x=1040,y=90,width = 30)

        #load and save#
        self.loadfunct = Button(self.master,text="Load file",command=lambda:load(False))
        self.loadfunct.place(x=1110,y=415,width=60)

        self.quickloadfunct = Button(self.master,text="Quick Load",command=lambda:load(True))
        self.quickloadfunct.place(x=1030,y=415,width=70)

        self.savefunct = Button(self.master,text="Save file",command=lambda:save(False))
        self.savefunct.place(x=1110,y=385,width=60)

        self.quicksavefunct = Button(self.master,text="Quick save",command=lambda:save(True))
        self.quicksavefunct.place(x=1030,y=385,width=70)

        #toggle stars#
        self.stary = Button(self.master, text="Toggle Stars on", command=self.startoggle,fg="Red",activeforeground="red")
        self.stary.place(x=1040,y=150,width=120)

        ###Planet specific variables###
        self.window.create_rectangle(1020,50,1180,190,fill="Light Grey") #toggle function box
        self.window.create_rectangle(1020,675,1180,760,fill="Light Grey")
        self.window.create_rectangle(1020,200,1180,340,fill="Light Grey")
        self.window.create_rectangle(1020,350,1180,450,fill="Light Grey")
        self.window.create_rectangle(1001,460,1250,470,fill="BLACK")
        self.window.create_rectangle(1020,480,1180,660,fill="Light Grey")
        self.window.create_text(1100,63,text="Misc Functions",font=("Helvetica",10,"bold "))
        self.window.create_text(1100,366,text="Load and save",font=("Helvetica",10,"bold "))
        self.window.create_text(1100,215,text="Planet Properties",font=("Helvetica",10,"bold "))

        #Mass#

        self.mass = DoubleVar()
        self.mass.set(100)
        self.window.create_text(1060,247,text= "Mass",font=("Helvetica", 10))
        self.Mass = Entry(self.master,width=10,textvariable=self.mass)
        self.Mass.place(x=1100,y=240)

        #Density#

        self.density = DoubleVar()
        self.density.set(20)
        self.window.create_text(1065,277,text= "Density",font=("Helvetica",10))
        self.Density = Entry(self.master,width=10, textvariable=self.density)
        self.Density.place(x=1100,y = 270)

        #Trail Duration#

        self.trailduration = IntVar()
        self.trailduration.set(0)
        self.window.create_text(1100,700,text="Trail duration\n      (20 = ∞)",font=("Helvetica",10,"bold"))
        self.trailduration = Scale(self.master,from_=0,to=20,orient=HORIZONTAL,bg="light grey",highlightthickness=0)
        self.trailduration.place(x=1050,y=715)

        #Force Amplification

        self.speed = 1 #force amplification
        self.window.create_text(1090,80,text="Amp")
        self.speed = Scale(self.master,from_=1,to=5,resolution=0.01,variable=self.speed,orient=HORIZONTAL,length = 50,width=20,bg="light grey",highlightthickness=0)
        self.speed.place(x=1110,y=70)
        #Planet variable showing#
        self.planetselected = 0

        self.window.create_text(1100,495,text="Planet Information",font=("Helvetica",10,"bold"))

        self.window.create_text(1062,520,text="Velocity")
        self.planetvelocity = IntVar()
        self.showoffvelocity = Entry(self.master,width=6,textvariable=self.planetvelocity)
        self.showoffvelocity.place(x=1100,y=513)
        self.planetvelocity.set(0)
        self.showoffvelocity.configure(state="disabled")

        self.window.create_text(1062,550,text="Mass")
        self.planetmass = IntVar()
        self.showoffmass = Entry(self.master,width=6,textvariable=self.planetmass)
        self.showoffmass.place(x=1100,y=540)
        self.planetmass.set(0)
        self.showoffmass.configure(state="disabled")

        self.window.create_text(1062,572,text="Density")
        self.planetdensity = IntVar()
        self.showoffdensity = Entry(self.master,width=6,textvariable=self.planetdensity)
        self.showoffdensity.place(x=1100,y=567)
        self.planetdensity.set(0)
        self.showoffdensity.configure(state="disabled")

        self.window.create_text(1062,605,text="Devorered\n  planets")
        self.planetsdevoured = IntVar()
        self.showoffdevoured = Entry(self.master,width=6,textvariable=self.planetsdevoured)
        self.showoffdevoured.place(x=1100,y=595)
        self.planetsdevoured.set(0)
        self.showoffdevoured.configure(state="disabled")

        self.window.create_text(1062,635,text="Time alive(s)")
        self.planetalivetime = IntVar()
        self.showoffalive = Entry(self.master,width=6,textvariable=self.planetalivetime)
        self.showoffalive.place(x=1100,y=622)
        self.planetalivetime.set(0)
        self.showoffalive.configure(state="disabled")

        #undo
        self.undo = Button(self.master,text="⟲",command=mainstack.undo,width = 2,height=-5,font=("Helvetica",10))
        self.undo.place(x=1070,y=15)

        #redo
        self.redo = Button(self.master,text="⟳",command=mainstack.redo,width=2,height=1,font=("Helvetica",10))
        self.redo.place(x=1110,y=15)



        ###    TITLE    ###
        alphabet = []
        for alpha in range (65,91): alphabet.append(chr(alpha))  #something like that
        self.systemname = ("PYxis - System: {}{}-{}{}{}".format(alphabet[random.randint(0,25)],alphabet[random.randint(0,25)],random.randint(0,9),random.randint(0,9),random.randint(0,9))) #Standard string consentraition methods leave ugly curly brackets.
        self.master.wm_title(self.systemname)

    def startoggle(self): #make these shift all in one direction at some point
        if self.stary["text"] == "Toggle Stars off":
            self.window.delete("star")
            self.stary["text"] = "Toggle Stars on"
            self.stary.config(fg="Red",activeforeground="Red")
        else:
            for stars in range(0,1000):
                for starsperline in range(0,1): #make this variable
                    ran = random.randint(0,1000)
                    colourcode = random.randint(0,255)
                    self.window.create_oval(ran,stars,ran,stars,outline=('#%02x%02x%02x' % (colourcode,colourcode, colourcode)),tags="star")
            self.stary["text"] = "Toggle Stars off"
            self.stary.config(fg="Green",activeforeground="Green")

        self.window.lower("star")
    def clickfunct(self,event):
        try:
            floatmass = float(self.mass.get())
            floatdensity = float(self.density.get())
            nmass = round(abs(floatmass))
            ndensity = round(abs(floatdensity))
            if event.x < 1000:
                self.ox = event.x
                self.oy = event.y
                self.window.create_oval(event.x+(nmass/ndensity),event.y+(nmass/ndensity),event.x-(nmass/ndensity),event.y-(nmass/ndensity),fill=self.planetcolour[1],tags="shotoval")
        except TclError:
            print("ERROR: Mass and/or density values are invalid.")
    def motion(self,event):
        self.window.delete("shot")
        colour = self.planetcolour[1]
        if event.x < 1000:
            self.window.create_line(self.ox,self.oy,event.x,event.y,fill=colour,tags="shot",arrow="last")

    def release(self,event):
        if event.x < 1000:
            x = event.x
            y = event.y
            cx = event.x - self.ox
            cy = event.y - self.oy
            self.window.delete("shot")
            try:
                lmass = int(self.mass.get()//1)
                ldensity = int(self.density.get()//1)
                if lmass < ldensity:
                    lmass = ldensity
                    self.mass.set(lmass)
                radius = lmass / ldensity
                if radius > 250:
                    radius = 250
                end = [x,y]
                start = [self.ox,self.oy]
                rad,theta,xneg,yneg = maths(start,end)
                vx = cx / lmass
                vy = cy / lmass
                createplanet(round(radius),lmass,self.ox,self.oy,self.planetcolour[0][0],self.planetcolour[0][1],self.planetcolour[0][2],vx,vy,theta,False,0)
            except TclError:
                pass
        self.window.delete("shotoval")
    def select(self,line):
        if self.planetselected > len(OBD) - 1: 
            self.planetselected = 0
        if line == self.planetselected:
            self.window.delete("s")
            self.selected = self.window.coords(OBD[line]["planet"])
            self.selectoval = self.window.create_oval(self.selected[0]-10,self.selected[1]-10,self.selected[2]+10,self.selected[3]+10,outline = "yellow",stipple="gray75",tags="s" )
            self.window.lower(self.selectoval)

ui = userinterface()

def updateUI():
    ui.window.delete("educat")
    if ui.planetselected in anchorlist:
        ui.planetanchor["text"] = "⛵"
    else:
        ui.planetanchor["text"] = "⚓"
    ui.window.itemconfig(ui.curtime,text=("Time",round(time.time() - ui.starttime,2)))
    red = (round((255/20)*ui.trailduration.get()))
    ui.trailduration.config(fg='#%02x%02x%02x' % (red,round((255-red)/2),0))
    if len(OBD) > 0:
        ui.planetvelocity.set(math.sqrt(((OBD[ui.planetselected]["dx"])**2) +  ((OBD[ui.planetselected]["dy"])**2))*1000)
        ui.planetmass.set(OBD[ui.planetselected]["mass"])
        ui.planetdensity.set(OBD[ui.planetselected]["mass"] / OBD[ui.planetselected]["radius"])
        ui.planetalivetime.set(round(time.time() - OBD[ui.planetselected]["alivetime"]))
        ui.planetsdevoured.set(OBD[ui.planetselected]["planetsdevoured"])
    try:
        ui.window.itemconfig(ui.fps,text=("FPS:", round(1/(time.time()-ui.otime))))
    except ZeroDivisionError:
        pass #if the time change is too low
    ui.otime = time.time()

def safepause():
    if ui.tobepaused == True or ui.tobepausedcolour == True:
        if ui.tobepausedcolour == True:
            playpause(True)
            askcolour(ui.prevpaused)
            playpause(False)
            ui.tobepausedcolour = False
        else: playpause(False)

#keybinds

ui.window.bind("<Button-1>",ui.clickfunct) #initial click
ui.window.bind("<B1-Motion>",ui.motion) #click and drag
ui.window.bind("<ButtonRelease-1>",ui.release) #release of click
ui.window.bind("<Button-3>",selectobject)
ui.window.bind("<Button-2>",lambda x:deleteplanet(ui.planetselected,False))

while True:
    if ui.paused != True:
        updateUI()
        main()
        if len(poplist) > 0:
            popplanets()
        safepause()
        ##Move the planets in time with the rest of the program.##
        #I decided not to function this to save on calling globals##
        for line in range(0,len(OBD)):
            ui.select(line)
            if line not in anchorlist:
                ui.window.move(OBD[line]["planet"],OBD[line]["dx"],OBD[line]["dy"])
                oldxy = [((OBD[line]["x0"]+OBD[line]["x1"])/2),((OBD[line]["y0"]+OBD[line]["y1"])/2)]
                try:
                    OBD[line]["x0"],OBD[line]["y0"],OBD[line]["x1"],OBD[line]["y1"]= ui.window.coords(OBD[line]["planet"])
                except ValueError:
                    pass
                newxy = [((OBD[line]["x0"]+OBD[line]["x1"])/2),((OBD[line]["y0"]+OBD[line]["y1"])/2)]
                if ui.trailduration.get() > 0:
                    drawtrail(oldxy,newxy,line)
    ui.window.update()
