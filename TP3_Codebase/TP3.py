#!/usr/bin/python
from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.interval.SoundInterval import SoundInterval
from direct.gui.DirectGui import *
from direct.gui.DirectSlider import DirectSlider
from direct.gui.DirectButton import DirectButton
from direct.interval.MetaInterval import Parallel
from direct.interval.LerpInterval import LerpHprInterval
from direct.interval.IntervalGlobal import Sequence,Func,Wait
from pandac.PandaModules import *
from panda3d.core import CollisionTraverser,CollisionHandlerEvent
from panda3d.core import CollisionNode,CollisionSphere
from panda3d.core import VBase4
from random import randint
from Tkinter import *
import random,sys


class Ground(ShowBase):

    def __init__(self):
        # Initialize the ShowBase class from which we inherit,which will
        # create a window and set up everything we need for rendering into it.
        ShowBase.__init__(self)        
      
        self.setBackgroundColor(240,35,35,1)

        # Make a variable to store the unique collision string count
        self.collCount = 0        

        #set scale of ground
        self.scaleBy = 120

        #disable mouse control of camera and manually place it
        base.disableMouse()
        camera.setPos(self.scaleBy // 2,self.scaleBy // 2,2)

        #quit program when Escapse key pressed
        self.accept("escape",sys.exit)
        self.accept("a",self.runMiniGame)
        #set default settings of game
        self.setting = "forest"
        self.music = base.loader.loadSfx("music1.ogg")
        self.music.setVolume(.5)

        self.miniGameRun = False

        #initialization starting screen
        self.loadStartScreen()


    #display start screen w/ text and buttons
    def loadStartScreen(self):
        self.startBG = OnscreenImage(image = 'world.jpg',pos = (0,0,0),
                        scale = 3)
        self.title = OnscreenText(text="Onwards,Term Project",
                     align=TextNode.ACenter,
                     fg=(1,1,1,1),pos=(0,0.5),scale=.08,
                     shadow=(0,0,0,0.5))
        self.chooseGround = OnscreenText(text="Choose Land:",
                            align=TextNode.ACenter,
                            fg=(1,1,1,1),pos=(-0.8,0.25),scale=.08,
                            shadow=(0,0,0,0.5))
        self.buttonForest = DirectButton(pos=(-0.2,0,0.24),text="Forest",
                             scale=.1,pad=(.2,.2),
                             rolloverSound=None,clickSound=None,
                             command=self.selected,extraArgs = ["forest"],
                             relief=SUNKEN)
        self.buttonDesert = DirectButton(pos=(0.4,0,0.24),text="Desert",
                            scale=.1,pad=(.2,.2),
                            rolloverSound=None,clickSound=None,
                            command=self.selected,extraArgs = ["desert"])
        self.chooseMusic = OnscreenText(text="Choose Music:",
                            align=TextNode.ACenter,
                            fg=(1,1,1,1),pos=(-0.8,0),scale=.08,
                            shadow=(0,0,0,0.5))
        self.buttonMusic1 = DirectButton(pos=(-0.2,0,-0.01),text="Piano 1",
                           scale=.1,pad=(.2,.2),
                           rolloverSound=None,clickSound=None,
                           command=self.selected,extraArgs=["piano1"],
                           relief=SUNKEN)
        self.buttonMusic2 = DirectButton(pos=(0.35,0,-0.01),text="Piano 2",
                           scale=.1,pad=(.2,.2),
                           rolloverSound=None,clickSound=None,
                           command=self.selected,extraArgs = ["piano2"])
        self.buttonMusic3 = DirectButton(pos=(0.8,0,-0.01),text="None",
                           scale=.1,pad=(.2,.2),
                           rolloverSound=None,clickSound=None,
                           command=self.selected,extraArgs = ["stop"])
        self.volume = OnscreenText(text="Volume:",
                            align=TextNode.ACenter,
                            fg=(1,1,1,1),pos=(-0.8,-0.3),scale=.08,
                            shadow=(0,0,0,0.5))
        self.volumeSlider = DirectSlider(pos=(0.3,0,-0.3),scale=0.7,value=.5,
                                   command=self.setMusicVolume)
        self.enterInstruction = OnscreenText(text="Press 'Enter' to Begin",
                            align=TextNode.ACenter,fg=(1,1,1,1),
                            pos=(0,-0.5),scale=.08,shadow=(0,0,0,0.5))
        self.accept("enter",self.loadModels)


    #change button reliefs if clicked or not & game settings based on button
    def selected(self,pressed):
        if pressed == "desert":
            self.setting = "desert"
            self.buttonForest['relief'] = RAISED
            self.buttonDesert['relief'] = SUNKEN
        elif pressed == "forest":
            self.setting = "forest"
            self.buttonForest['relief'] = SUNKEN
            self.buttonDesert['relief'] = RAISED
        if pressed == "piano1":
            self.music.stop()
            self.music = base.loader.loadSfx("music1.ogg")
            self.music.setLoop(True)
            self.music.play()
            self.buttonMusic1['relief'] = SUNKEN
            self.buttonMusic2['relief'] = RAISED
            self.buttonMusic3['relief'] = RAISED
        elif pressed == "piano2":
            self.music.stop()
            self.music = base.loader.loadSfx("music2.ogg")
            self.music.setLoop(True)
            self.music.play()
            self.buttonMusic1['relief'] = RAISED
            self.buttonMusic2['relief'] = SUNKEN
            self.buttonMusic3['relief'] = RAISED
        elif pressed == "stop":
            self.music.stop()
            self.buttonMusic1['relief'] = RAISED
            self.buttonMusic2['relief'] = RAISED
            self.buttonMusic3['relief'] = SUNKEN


    #change volume based on slider position
    def setMusicVolume(self):
        vol = self.volumeSlider.guiItem.getValue()
        self.music.setVolume(vol)


    #load models when 'enter' pressed
    def loadModels(self):
        self.startBG.destroy()
        self.title.destroy()
        self.chooseGround.destroy()
        self.buttonForest.destroy()
        self.buttonDesert.destroy()
        self.chooseMusic.destroy()
        self.buttonMusic1.destroy()
        self.buttonMusic2.destroy()
        self.buttonMusic3.destroy()
        self.enterInstruction.destroy()
        self.volumeSlider.destroy()
        self.volume.destroy()
        
        self.cTrav = CollisionTraverser()

        self.lastHitEntry = "is an entry"
        self.plants = []
        self.plantColls = []
        self.animals = []
        self.animalColls = []

        self.miniGameBoxes = []

        self.axes = []
        self.planters = []
        self.haveAxe = False
        self.havePlanter = False
        self.selectedPlanterOpt = 0

        self.planterOptionsForest = [("plants/foliage01.egg.pz",11,12),
        ("plants/foliage02.egg.pz",-12,14),("plants/foliage03.egg.pz",14,23),
        ("plants/foliage04.egg.pz",0,0),("plants/foliage05.egg.pz",6,22),
        ("plants/foliage09.egg.pz",-3,10),("chicken.egg",0,0)]

        self.planterOptionsDesert = [("plants/shrubbery.egg.pz",1,14),
        ("plants/cactus1.egg",0,12),("plants/cactus2.egg",2.5,11),
        ("chicken.egg",0,0)]

        #display instructions
        self.loadText()

        #respond when arrow keys are pressed
        self.accept("arrow_up",self.eventArrowPressed,["up"])
        self.accept("arrow_up-repeat",self.eventArrowPressed,["up"])
        self.accept("arrow_right",self.eventArrowPressed,["right"])
        self.accept("arrow_right-repeat",self.eventArrowPressed,["right"])
        self.accept("arrow_left",self.eventArrowPressed,["left"])
        self.accept("arrow_left-repeat",self.eventArrowPressed,["left"])
        self.accept("arrow_down",self.eventArrowPressed,["down"])
        self.accept("arrow_down-repeat",self.eventArrowPressed,["down"])
        self.accept("f",self.eventAerielView)
        self.accept("0",self.restartGame)
        self.accept("enter",self.doNothing)

        
        groundTexture = loader.loadTexture(self.setting + ".jpg")

        #load starting square of land
        land = loader.loadModel("box")
        land.setPos(0,0,0)
        land.setSy(self.scaleBy)
        land.setSx(self.scaleBy)
        land.setSz(0.5)
        land.setTexture(groundTexture,1)

        self.spanGround = [(0,0)]
        self.ground = land
        self.ground.reparentTo(render)

        #load main char
        self.mainChar = loader.loadModel("box")
        self.mainChar.reparentTo(camera)
        self.mainChar.setPos(0,10,-2)
        self.mainChar.setColorScale(0.6,0.6,1.0,1.0)
        self.moveMainCharX = 0.5
        self.moveMainCharY = 0.75
        
        #load main char's collision ray onto screen & make char a collider
        self.mainCharGroundRay = CollisionRay()
        self.mainCharGroundRay.setOrigin(0.5,0,30)
        self.mainCharGroundRay.setDirection(0,0,-1)
        self.mainCharGroundCol = CollisionNode('mainCharRay')
        self.mainCharGroundCol.addSolid(self.mainCharGroundRay)
        self.mainCharGroundCol.setFromCollideMask(CollideMask.bit(0))
        self.mainCharGroundCol.setIntoCollideMask(CollideMask.allOff())
        self.mainCharGroundColNp = self.mainChar.attachNewNode(\
                                                        self.mainCharGroundCol)
        self.mainCharGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.mainCharGroundColNp,\
                                                    self.mainCharGroundHandler)
        #load camera's collision ray & make it a collider
        self.camGroundRay = CollisionRay()
        self.camGroundRay.setOrigin(0,0,30)
        self.camGroundRay.setDirection(0,0,-1)
        self.camGroundCol = CollisionNode('camRay')
        self.camGroundCol.addSolid(self.camGroundRay)
        self.camGroundCol.setFromCollideMask(CollideMask.bit(0))
        self.camGroundCol.setIntoCollideMask(CollideMask.allOff())
        self.camGroundColNp = self.camera.attachNewNode(self.camGroundCol)
        self.camGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.camGroundColNp,self.camGroundHandler)
        
        #shows collision nodes (for debugging)
        # self.mainCharGroundColNp.show()
        # self.camGroundColNp.show()

        self.curPos = self.mainChar.getPos()
        self.cameraCurPos = camera.getPos()

        # shows collisions occuring (for debugging)
        # self.cTrav.showCollisions(render)

        #continuously check for collisions
        taskMgr.add(self.checkCollisions,"checkCollisionsTask")

        #initialize fog so that scene in distance is blocked from view
        color = (240,35,35)
        expfog = Fog("Scene-wide exponential Fog object")
        expfog.setColor(*color)
        expfog.setExpDensity(0.006)
        render.setFog(expfog)
        base.setBackgroundColor(color)


    #display instructions on screen top & title on botton
    def loadText(self):
        self.bottomTitle = \
            OnscreenText(text="Onwards,Term Project",
                         parent=base.a2dBottomRight,align=TextNode.ARight,
                         fg=(1,1,1,1),pos=(-0.1,0.1),scale=.08,
                         shadow=(0,0,0,0.5))
        self.startInstructions = \
           OnscreenText(text="Press Arrow Keys to explore. Press and hold 'f' "+
                              "to activate Aeriel View. Press Esc to exit."+
                              "\nPress '0' to go to Start Screen",
                         parent=base.a2dTopLeft,align=TextNode.ALeft,
                         pos=(0.05,-0.08),fg=(1,1,1,1),scale=.06,
                         shadow=(0,0,0,0.5))

    
    #set what happens when arrow keys pressed
    def eventArrowPressed(self, dir):
        self.curPos = self.mainChar.getPos()
        self.cameraCurPos = camera.getPos()
        x,y,z = base.camera.getPos()
        if dir == "up":
            camera.setPos(x,y + self.moveMainCharY,z)
        elif dir == "down":
            camera.setPos(x,y - self.moveMainCharY,z)
        elif dir == "right":
            camera.setPos(x + self.moveMainCharX,y,z)
        elif dir == "left":
            camera.setPos(x - self.moveMainCharX,y,z)
        self.checkExtend(dir)


    #set what happens when x pressed & axe activated
    def eventAxe(self):
        deleted = False
        if len(self.plantColls) > 0:
            for i in range(len(self.plantColls)):
                if (self.lastHitEntry in self.plantColls[i][0].getName()):
                    self.plantColls[i][0].remove_node()
                    self.plants[i].remove_node()
                    self.plantColls = self.plantColls[:i]+self.plantColls[i+1:]
                    self.plants = self.plants[:i] + self.plants[i+1:]
                    deleted = True
                    break
        if len(self.animalColls) > 0 and deleted == False:
            for i in range(len(self.animalColls)):
                if (self.lastHitEntry in self.animalColls[i][0].getName()):
                    self.animalColls[i][0].remove_node()
                    self.animals[i][0].remove_node()
                    self.animalColls = self.animalColls[:i]+\
                                       self.animalColls[i+1:]
                    self.animals = self.animals[:i]+self.animals[i+1:]
                    deleted = True
                    break
        if len(self.miniGameBoxes) > 0 and deleted == False:
            for i in range(len(self.miniGameBoxes)):
                if (self.lastHitEntry in self.miniGameBoxes[i][1][0].getName()):
                    self.miniGameBoxes[i][1][0].remove_node()
                    self.miniGameBoxes[i][0].remove_node()
                    self.miniGameBoxes = self.miniGameBoxes[:i]+\
                                         self.miniGameBoxes[i+1:]
                    deleted = True
                    self.acceptMiniGame()
                    break


    #set what happens when w pressed & planter activated
    def eventPlanter(self):
        #create new object and position it in front of main character
        x,y,z = camera.getPos()
        if self.setting == "forest":
            plantType,shiftX,shiftY = \
                            self.planterOptionsForest[self.selectedPlanterOpt]
        else:
            plantType,shiftX,shiftY = \
                            self.planterOptionsDesert[self.selectedPlanterOpt]
        if plantType == "chicken.egg":
            self.newAnimal()
        else:
            plant = loader.loadModel(plantType)
            plant.setScale(0.2)
            plant.setPos(x + shiftX,y + shiftY,0)
            plant.reparentTo(render)
            if plantType == "plants/cactus1.egg":
                plant.setTexture(loader.loadTexture("cactusskin.png"),1)
                plant.setScale(1)
                plantColl = self.initCollisionSphere(plant,0.1,False)
            elif plantType == "plants/cactus2.egg":
                plant.setScale(1)
                plant.setZ(0.5)
                plantColl = self.initCollisionSphere(plant,0.8,False)
            elif plantType == "plants/shrubbery.egg.pz":
                plant.setScale(0.15)
                plantColl = self.initCollisionSphere(plant,0.2,False)
            else:
                plantColl = self.initCollisionSphere(plant,0.08,False)
            self.plants += [plant]
            self.plantColls += [plantColl]


    #shift camera upwards to show aeriel view
    def eventAerielView(self):
        self.x,self.y,self.z = camera.getPos()
        shiftPos = camera.posInterval(0.1,\
                                     Point3(self.x,self.y + 30,self.z + 150))
        shiftAngle = camera.hprInterval(0.2,Vec3(0,-90,0))
        aerielView = Sequence(shiftPos,shiftAngle)
        aerielView.start()
        self.moveMainCharX = 2
        self.moveMainCharY = 3
        self.accept("f-up",self.eventNormalView)
    

    #shift camera back to normal view
    def eventNormalView(self):
        shiftPos = camera.posInterval(0.1,Point3(self.x,self.y,self.z))
        shiftAngle = camera.hprInterval(0.2,Vec3(0,0,0))
        aerielView = Sequence(shiftPos,shiftAngle)
        aerielView.start()
        self.moveMainCharX = 0.5
        self.moveMainCharY = 0.75


    #check whether or not to extend ground
    def checkExtend(self,dir):
        x,y,z = base.camera.getPos()
        checkV = (0,0)
        whole = self.scaleBy
        #Up
        checkX = x // self.scaleBy
        checkY = (y + whole) // self.scaleBy
        cUp = (checkX,checkY)
        if cUp not in self.spanGround:
            self.spanGround += [cUp]
            self.extendScene()
        #Down
        checkX = x // self.scaleBy
        checkY = (y - whole) // self.scaleBy
        cDown = (checkX,checkY)
        if cDown not in self.spanGround:
            self.spanGround += [cDown]
            self.extendScene()
        #Right
        checkX = (x + whole) // self.scaleBy
        checkY = y // self.scaleBy
        cRight = (checkX,checkY)
        if cRight not in self.spanGround:
            self.spanGround += [cRight]
            self.extendScene()
        #Left
        checkX = (x - whole) // self.scaleBy
        checkY = y // self.scaleBy
        cLeft = (checkX,checkY)
        if cLeft not in self.spanGround:
            self.spanGround += [cLeft]
            self.extendScene()
        #Upper Right Diagonal
        checkX = (x + whole) // self.scaleBy
        checkY = (y + whole) // self.scaleBy
        cUpRight = (checkX,checkY)
        if cUpRight not in self.spanGround:
            self.spanGround += [cUpRight]
            self.extendScene()
        #Upper Left Diagonal
        checkX = (x - whole) // self.scaleBy
        checkY = (y + whole) // self.scaleBy
        cUpLeft = (checkX,checkY)
        if cUpLeft not in self.spanGround:
            self.spanGround += [cUpLeft]
            self.extendScene()
        #Lower Right Diagonal
        checkX = (x + whole) // self.scaleBy
        checkY = (y - whole) // self.scaleBy
        cUpRight = (checkX,checkY)
        if cUpRight not in self.spanGround:
            self.spanGround += [cUpRight]
            self.extendScene()
        #Lower Left Diagonal
        checkX = (x - whole) // self.scaleBy
        checkY = (y - whole) // self.scaleBy
        cUpLeft = (checkX,checkY)
        if cUpLeft not in self.spanGround:
            self.spanGround += [cUpLeft]
            self.extendScene()


    #extend ground
    def extendScene(self):
        #add square of ground
        groundTexture = loader.loadTexture(self.setting + ".jpg")
        new = loader.loadModel("box")
        new.setSy(self.scaleBy)
        new.setSx(self.scaleBy)
        new.setSz(0.5)
        new.setTexture(groundTexture,1)
        newPos = self.spanGround[-1]
        newPosX = newPos[0] * self.scaleBy
        newPosY = newPos[1] * self.scaleBy
        new.setPos(newPosX,newPosY,0)
        self.newground = new
        self.newground.reparentTo(render)

        #load axe if haven't collided with one yet
        if not self.haveAxe:
            axe = loader.loadModel("axe")
            axe.setColor(0,0,0,1.0)
            axe.setScale(0.5,1,0.5)
            axe.setPos(randint(newPosX,newPosX + self.scaleBy),
                              randint(newPosY,newPosY +self.scaleBy),0.3)
            axe.reparentTo(render)
            axeObject = loader.loadModel("axe01")
            axeObject.setScale(3)
            axeObject.setPos(0.5,0,2)
            axeObject.setHpr(0,65,35)
            axeObject.reparentTo(axe)
            axeColl = self.initCollisionSphere(axe,1,False)
            self.axes += [axe]

        #load planter if haven't collided with one yet
        if not self.havePlanter:
            planter = loader.loadModel("planter")
            planter.setColor(0,0,1,1)
            planter.setScale(1,1,1)
            planter.setPos(randint(newPosX,newPosX + self.scaleBy),
                              randint(newPosY,newPosY +self.scaleBy),0.3)
            planter.reparentTo(render)
            planterBag = loader.loadModel("planter01")
            planterBag.setScale(1.5)
            planterBag.setHpr(0,30,0)
            planterBag.setPos(0.75,0,1.25)
            planterBag.reparentTo(planter)
            planterColl = self.initCollisionSphere(planter,1,False)
            self.planters += [planter]

        #load random number of mini game boxes
        for i in range(randint(1,4)):
            miniGameBox = loader.loadModel("box")
            miniGameBox.setPos(randint(newPosX,newPosX + self.scaleBy),
                              randint(newPosY,newPosY +self.scaleBy),0.5)
            miniGameBox.reparentTo(render)
            miniGameBoxColl = self.initCollisionSphere(miniGameBox,1.3,False)
            self.miniGameBoxes += [[miniGameBox,miniGameBoxColl]]

        #load certain plants in forest setting
        if self.setting == "forest":
            for i in range(randint(3,15)):
                #place plant 1
                plant1 = loader.loadModel("plants/foliage01.egg.pz")
                plant1.setScale(0.2)
                plant1.setPos(randint(newPosX,newPosX + self.scaleBy),
                              randint(newPosY,newPosY +self.scaleBy),0)
                plant1.reparentTo(render)
                plantColl = self.initCollisionSphere(plant1,0.08,False)
                self.plants += [plant1]
                self.plantColls += [plantColl]
            for i in range(randint(3,15)):
                #place plant2
                plant2 = loader.loadModel("plants/foliage02.egg.pz")
                plant2.setScale(0.2)
                plant2.setPos(randint(newPosX,newPosX + self.scaleBy),
                              randint(newPosY,newPosY +self.scaleBy),0)
                plant2.reparentTo(render)
                plantColl = self.initCollisionSphere(plant2,0.06,False)
                self.plants += [plant2]
                self.plantColls += [plantColl]
            for i in range(randint(3,15)):
                #place plant3
                plant3 = loader.loadModel("plants/foliage03.egg.pz")
                plant3.setScale(0.8)
                plant3.setPos(randint(newPosX,newPosX + self.scaleBy),
                              randint(newPosY,newPosY +self.scaleBy),0)
                plant3.reparentTo(render)
                plantColl = self.initCollisionSphere(plant3,0.06,False)
                self.plants += [plant3]
                self.plantColls += [plantColl]
            for i in range(randint(3,15)):
                #place plant4
                plant4 = loader.loadModel("plants/foliage04.egg.pz")
                plant4.setScale(0.6)
                plant4.setPos(randint(newPosX,newPosX + self.scaleBy),
                              randint(newPosY,newPosY +self.scaleBy),0)
                plant4.reparentTo(render)
                plantColl = self.initCollisionSphere(plant4,0.07,False)
                self.plants += [plant4]
                self.plantColls += [plantColl]
            for i in range(randint(3,15)):
                #place plant5
                plant5 = loader.loadModel("plants/foliage05.egg.pz")
                plant5.setScale(0.6)
                plant5.setPos(randint(newPosX,newPosX + self.scaleBy),
                              randint(newPosY,newPosY +self.scaleBy),0)
                plant5.reparentTo(render)
                plantColl = self.initCollisionSphere(plant5,0.05,False)
                self.plants += [plant5]
                self.plantColls += [plantColl]
            for i in range(randint(3,15)):
                #place plant6
                plant6 = loader.loadModel("plants/foliage09.egg.pz")
                plant6.setScale(0.6)
                plant6.setPos(randint(newPosX,newPosX + self.scaleBy),
                              randint(newPosY,newPosY +self.scaleBy),0)
                plant6.reparentTo(render)
                plantColl = self.initCollisionSphere(plant6,0.08,False)
                self.plants += [plant6]
                self.plantColls += [plantColl]
            #load walking animals
            if newPos[0] % 4 == 0 and newPos[1] % 3 == 0:
                animal = loader.loadModel("box")
                animal.setScale(1)
                animal.setPos(randint(newPosX,newPosX + self.scaleBy),
                              randint(newPosY,newPosY +self.scaleBy),-0.75)
                animal.reparentTo(render)
                animalColl = self.initCollisionSphere(animal,0.75,False)
                chicken = loader.loadModel("chicken")
                chicken.setScale(0.15)
                chicken.setPos(0.5,0.5,1.25)
                chicken.setHpr(0,0,0)
                chicken.reparentTo(animal)
                self.animalColls += [animalColl]
                animalGroundHandler = CollisionHandlerQueue()
                self.animals += [[animal,randint(0,4),animalGroundHandler]]
                self.cTrav.addCollider(animalColl[0],animalGroundHandler)
        #load certain plants in desert setting
        elif self.setting == "desert":
            for i in range(randint(0,6)):
                #place shrubbery
                plant0 = loader.loadModel("plants/shrubbery.egg.pz")
                plant0.setScale(0.1)
                plant0.setPos(randint(newPosX,newPosX + self.scaleBy),
                              randint(newPosY,newPosY +self.scaleBy),0)
                plant0.reparentTo(render)
                plantColl = self.initCollisionSphere(plant0,0.3,False)
                self.plants += [plant0]
                self.plantColls += [plantColl]
            for i in range(randint(0,6)):
                #place cactus1
                plant1 = loader.loadModel("plants/cactus1.egg")
                plant1.setScale(1)
                plant1.setPos(randint(newPosX,newPosX + self.scaleBy),
                              randint(newPosY,newPosY +self.scaleBy),0)
                plant1.setTexture(loader.loadTexture("cactusskin.png"),1)
                plant1.reparentTo(render)
                plantColl = self.initCollisionSphere(plant1,0.1,False)
                self.plants += [plant1]
                self.plantColls += [plantColl]
            for i in range(randint(0,6)):
                #place cactus2
                plant2 = loader.loadModel("plants/cactus2.egg")
                plant2.setScale(1)
                plant2.setPos(randint(newPosX,newPosX + self.scaleBy),
                              randint(newPosY,newPosY +self.scaleBy),0.5)
                plant2.reparentTo(render)
                plantColl = self.initCollisionSphere(plant2,0.8,False)
                self.plants += [plant2]
                self.plantColls += [plantColl]
            #load walking animals
            if newPos[0] % 4 == 0 and newPos[1] % 3 == 0:
                animal = loader.loadModel("box")
                animal.setScale(1)
                animal.setPos(randint(newPosX,newPosX + self.scaleBy),
                              randint(newPosY,newPosY +self.scaleBy),-0.75)
                animal.reparentTo(render)
                animalColl = self.initCollisionSphere(animal,0.75,False)
                chicken = loader.loadModel("chicken")
                chicken.setScale(0.15)
                chicken.setPos(0.5,0.5,1.25)
                chicken.setHpr(0,0,0)
                chicken.reparentTo(animal)
                self.animalColls += [animalColl]
                animalGroundHandler = CollisionHandlerQueue()
                self.animals += [[animal,randint(0,4),animalGroundHandler]]
                self.cTrav.addCollider(animalColl[0],animalGroundHandler)


    #load animal in front of main char
    def newAnimal(self):
        #load and initialize box for chicken to be rendered to
        x,y,z = self.cameraCurPos
        animal = loader.loadModel("box")
        animal.setScale(1)
        animal.setPos(x + 1,y + 15,-0.75)
        animal.reparentTo(render)
        animalColl = self.initCollisionSphere(animal,0.75,False)
        #load chicken
        chicken = loader.loadModel("chicken")
        chicken.setScale(0.15)
        chicken.setPos(0.5,0.5,1.25)
        chicken.setHpr(0,0,0)
        chicken.reparentTo(animal)
        #store animal into
        self.animalColls += [animalColl]
        animalGroundHandler = CollisionHandlerQueue()
        self.animals += [[animal,0,animalGroundHandler]]
        self.cTrav.addCollider(animalColl[0],animalGroundHandler)
        taskMgr.add(self.moveAnimal,"moveAnimalsTask")
        taskMgr.add(self.checkAnimalCollisions,"checkAnimalCollisionsTask")


    #move every animal in self.animals forward
    def moveAnimal(self,task):
        for animal in self.animals:
            x,y,z = animal[0].getPos()
            if animal[1] == 0:
                animal[0].setPos(x,y + 0.025,z)
                animal[0].setHpr(180,0,0)
            elif animal[1] == 2:
                animal[0].setPos(x + 0.025,y,z)
                animal[0].setHpr(90,0,0)
            elif animal[1] == 1:
                animal[0].setPos(x,y - 0.025,z)
                animal[0].setHpr(0,0,0)
            elif animal[1] == 3:
                animal[0].setPos(x - 0.025,y,z)
                animal[0].setHpr(270,0,0)
        return Task.cont


    #check if animal collided with surroundings
    def checkAnimalCollisions(self,task):
        #check collisions of each automatically moving animals
        for animal in self.animals:
            entries = list(animal[2].getEntries())
            entries.sort(key=lambda x: x.getSurfacePoint(render).getZ())
            if len(entries) > 0:
                x,y,z = animal[0].getPos()
                if animal[1] == 0:
                    animal[0].setPos(x,y - 0.03,z)
                elif animal[1] == 2:
                    animal[0].setPos(x - 0.03,y,z)
                elif animal[1] == 1:
                    animal[0].setPos(x,y + 0.03,z)
                elif animal[1] == 3:
                    animal[0].setPos(x + 0.03,y,z)
                animal[1] = (animal[1] + 1) % 4
        return Task.cont


    #check if main character collided with surroundings
    def checkCollisions(self,task):
        #check collisions for mainChar
        entries = list(self.mainCharGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(render).getZ())
        #if bump into tree,go back to last position so char doesn't go in tree
        if (len(entries)>0 and ("axe" not in entries[0].getIntoNode().getName())
            and ("planter" not in entries[0].getIntoNode().getName())):
            camera.setPos(self.cameraCurPos)
            #show what was last hit item
            if self.haveAxe:
                #unhighlight last entry
                unhighlighted = True
                if unhighlighted:
                    for i in range(len(self.plantColls)):
                        if (self.lastHitEntry in \
                            self.plantColls[i][0].getName()):
                            self.plants[i].setColorScale(1,1,1,1.0)
                            unhighlighted = False
                            break
                if unhighlighted:
                    for i in range(len(self.animalColls)):
                        if (self.lastHitEntry in \
                            self.animalColls[i][0].getName()):
                            self.animals[i][0].setColorScale(1,1,1,1.0)
                            unhighlighted = False
                            break
                if unhighlighted:
                    for i in range(len(self.miniGameBoxes)):
                        if(self.lastHitEntry in \
                            self.miniGameBoxes[i][1][0].getName()):
                            self.miniGameBoxes[i][0].setColorScale(1,1,1,1.0)
                            unhighlighted = False
                            break
                #find last entry & highlight it
                if len(entries) > 0:
                    self.lastHitEntry = entries[0].getIntoNode().getName()
                    highlighted = True
                    if highlighted:
                        for i in range(len(self.plantColls)):
                            if (self.lastHitEntry in \
                                self.plantColls[i][0].getName()):
                                self.plants[i].setColorScale(0.6,0.6,1.0,1.0)
                                highlighted = False
                                break
                    if highlighted:
                        for i in range(len(self.animalColls)):
                            if (self.lastHitEntry in \
                                self.animalColls[i][0].getName()):
                                self.animals[i][0].setColorScale(0.6,\
                                                                 0.6,1.0,1.0)
                                highlighted = False
                                break
                    if highlighted:
                        for i in range(len(self.miniGameBoxes)):
                            if(self.lastHitEntry in \
                                self.miniGameBoxes[i][1][0].getName()):
                                self.miniGameBoxes[i][0].setColorScale(0.6,\
                                                                    0.6,1.0,1.0)
                                highlighted = False
                                break
        #if bump into axe,activate axe & delete it
        elif len(entries) > 0 and ("axe" in entries[0].getIntoNode().getName()):
            self.haveAxe = True
            for obj in self.axes:
                obj.remove_node()

        #if bump into planter,activate planter & delete it
        elif (len(entries) > 0 
            and ("planter" in entries[0].getIntoNode().getName())):
            self.havePlanter = True
            for obj in self.planters:
                obj.remove_node()
        #change onscreen text & add keyboard events if hit axe and/or planter
        if self.havePlanter:
            self.accept('w',self.eventPlanter)
            self.planterInstructions=OnscreenText(text="Press 'w' to plant."+
                         "Press 'q' or 'e' to change plant",
                         parent=base.a2dTopLeft,align=TextNode.ALeft,
                         pos=(0.05,-0.28),fg=(1,1,1,1),scale=.06,
                         shadow=(0,0,0,0.5))
            self.accept('e',self.changeSelectedPlanterOpt,["e"])
            self.accept('q',self.changeSelectedPlanterOpt,["q"])
        if self.haveAxe:
            self.accept('x',self.eventAxe)
            self.axeInstructions=OnscreenText(text="Press 'x' to cut plant.",
                         parent=base.a2dTopLeft,align=TextNode.ALeft,
                         pos=(0.05,-0.20),fg=(1,1,1,1),scale=.06,
                         shadow=(0,0,0,0.5))
        return Task.cont


    #change selecter planter opt so that it stays w/in list
    def changeSelectedPlanterOpt(self,direction):
        #in forest,modify selectedPlantOpt if it goes out of range
        if self.setting == "forest":
            if direction == "e":
                self.selectedPlanterOpt += 1
                if self.selectedPlanterOpt >= len(self.planterOptionsForest):
                    self.selectedPlanterOpt -= len(self.planterOptionsForest)
            else:
                self.selectedPlanterOpt -= 1
                if self.selectedPlanterOpt <= -1*len(self.planterOptionsForest):
                    self.selectedPlanterOpt += len(self.planterOptionsForest)
        #in desert,modify selectedPlantOpt if it goes out of range
        else:
            if direction == "e":
                self.selectedPlanterOpt += 1
                if self.selectedPlanterOpt >= len(self.planterOptionsDesert):
                    self.selectedPlanterOpt -= len(self.planterOptionsDesert)
            else:
                self.selectedPlanterOpt -= 1
                if self.selectedPlanterOpt <= -1*len(self.planterOptionsDesert):
                    self.selectedPlanterOpt += len(self.planterOptionsDesert)


    #source: https://www.panda3d.org/manual/index.php/Event_Example
    #initialize collision sphere around object
    def initCollisionSphere(self,obj,circR,show=False):
        # Get the size of the object for the collision sphere.
        bounds = obj.getChild(0).getBounds()
        radius = bounds.getRadius() * circR

        center = bounds.getCenter()
        #make center of collision circle be on ground around tree trunks
        center[2] = 0
        if obj.getName() == "foliage01.egg.pz":
            pass
        elif obj.getName() == "foliage02.egg.pz":
            center[0] -= 4
        elif obj.getName() == "foliage03.egg.pz":
            center[0] -= 3.5
        elif obj.getName() == "foliage04.egg.pz":
            center[0] += 11
            center[1] -= 1
        elif obj.getName() == "foliage05.egg.pz":
            center[0] += 1.5
            center[1] -= 4
        elif obj.getName() == "foliage09.egg.pz":
            center[0] -= 2.5
            center[1] -= 2
 
        # Create a collision sphere and name it something understandable.
        collSphereStr = 'CollisionHull' + str(self.collCount)+"_" +obj.getName()
        self.collCount += 1
        cNode = CollisionNode(collSphereStr)
        cNode.addSolid(CollisionSphere(center,radius))
 
        cNodepath = obj.attachNewNode(cNode)
        if show:
            cNodepath.show()
 
        # Return a tuple with the collision node and its corrsponding string so
        # that the bitmask can be set.
        return (cNodepath,collSphereStr)


    #remove functionality from keyboard key
    def doNothing(self):
        pass


    #ask player if they want to continue to minigame screen
    def acceptMiniGame(self):
        self.question = OnscreenText(text="Do you want to play a minigame?",
                     align=TextNode.ACenter,
                     fg=(1,1,1,1),pos=(0,0.5),scale=.08,
                     shadow=(0,0,0,0.5))
        
        self.buttonNo = DirectButton(pos=(-0.2,0,0.24),text="No",
                             scale=.1,pad=(.2,.2),
                             rolloverSound=None,clickSound=None,
                             command=self.miniSelected,extraArgs = ["no"],
                             relief=SUNKEN)

        self.buttonYes = DirectButton(pos=(0.2,0,0.24),text="Yes",
                             scale=.1,pad=(.2,.2),
                             rolloverSound=None,clickSound=None,
                             command=self.miniSelected,extraArgs = ["yes"],
                             relief=RAISED)

        self.enterInstruction = OnscreenText(text="Press 'enter' to continue",
                            align=TextNode.ACenter,fg=(1,1,1,1),
                            pos=(0,-0.5),scale=.08,shadow=(0,0,0,0.5))

        self.accept("enter",self.executeMiniButtons)


    #change values of button when pressed
    def miniSelected(self,pressed):
        if pressed == "yes":
            self.miniGameRun = True
            self.buttonNo['relief'] = RAISED
            self.buttonYes['relief'] = SUNKEN
        elif pressed == "no":
            self.miniGameRun = False
            self.buttonNo['relief'] = SUNKEN
            self.buttonYes['relief'] = RAISED


    #control whether to run mini game or continue normal game
    def executeMiniButtons(self):
        self.question.destroy()
        self.buttonNo.destroy()
        self.buttonYes.destroy()
        self.enterInstruction.destroy()
        if self.miniGameRun:
            self.runMiniGame()


    #run minigame if magic box is collected
    def runMiniGame(self):
        #remove game functionality from keys while minigame is being played
        self.accept("a",self.doNothing)
        self.accept("f",self.doNothing)
        self.accept("w",self.doNothing)
        self.accept("e",self.doNothing)
        self.accept("q",self.doNothing)
        self.accept("enter",self.doNothing)

        #temporarily stop checking collisions on main game level
        taskMgr.remove('checkCollisionsTask')

        #temporarily add task
        taskMgr.add(self.miniGameCheckCollisions,'miniGameCheckCollisionsTask')

        #temporary mini game controls
        self.accept("arrow_up",self.eventUpMini)
        self.accept("arrow_up-repeat",self.eventUpMini)
        self.accept("arrow_right",self.eventRightMini)
        self.accept("arrow_right-repeat",self.eventRightMini)
        self.accept("arrow_left",self.eventLeftMini)
        self.accept("arrow_left-repeat",self.eventLeftMini)
        self.accept("arrow_down",self.eventDownMini)
        self.accept("arrow_down-repeat",self.eventDownMini)
        self.accept("x",self.eventAxe)

        self.miniGameRun = False

        #shift camera down to minigame level
        self.x,self.y,self.z = camera.getPos()
        shiftPos = camera.posInterval(0.1,Point3(self.scaleBy//2,
                                                 self.scaleBy//2,-148))
        miniGameView = Sequence(shiftPos)
        miniGameView.start()

        #game objects (object,x,y,scale)
        self.miniGameModles = [("plants/foliage01.egg.pz",11,12,1),
        ("plants/foliage02.egg.pz",-12,14,1),("plants/shrubbery.egg.pz",1,14,1),
        ("plants/cactus1.egg",0,0,1),("plants/cactus2.egg",2.5,11,1),
        ("chicken.egg",0,0,0.15)]

        #create minigame ground
        land = loader.loadModel("box")
        land.setPos(0,0,-150)
        land.setSy(self.scaleBy)
        land.setSx(self.scaleBy)
        land.setSz(0.5)
        land.reparentTo(render)
        
        self.instructionsChicken = OnscreenText(text="Find chicken to return!",
                     align=TextNode.ACenter,
                     fg=(1,1,1,1),pos=(0,0.5),scale=.08,
                     shadow=(0,0,0,0.5))

        #load and initialize box for chicken to be rendered to
        x,y,z = self.cameraCurPos
        animal = loader.loadModel("box")
        animal.setScale(1)
        animal.setPos(randint(1,118),randint(10,106),-150.75)
        animal.reparentTo(render)
        animalColl = self.initCollisionSphere(animal,0.75,False)
        #load chicken
        chicken = loader.loadModel("chicken")
        chicken.setScale(0.15)
        chicken.setPos(0.5,0.5,1.25)
        chicken.setHpr(0,0,0)
        chicken.reparentTo(animal)
        #store animal into
        self.animalColls += [animalColl]
        animalGroundHandler = CollisionHandlerQueue()
        self.animals += [[animal,0,animalGroundHandler]]
        self.cTrav.addCollider(animalColl[0],animalGroundHandler)


    #when game is done,change setting back to original
    def miniGameDone(self):
        self.instructionsChicken.destroy()

        #delete new chicken
        self.animalColls[-1][0].remove_node()
        self.animals[-1][0].remove_node()
        self.animalColls = self.animalColls[:-1]
        self.animals = self.animals[:-1]

        #back to original game controls
        self.accept("arrow_up",self.eventArrowPressed,["up"])
        self.accept("arrow_up-repeat",self.eventArrowPressed,["up"])
        self.accept("arrow_right",self.eventArrowPressed,["right"])
        self.accept("arrow_right-repeat",self.eventArrowPressed,["right"])
        self.accept("arrow_left",self.eventArrowPressed,["left"])
        self.accept("arrow_left-repeat",self.eventArrowPressed,["left"])
        self.accept("arrow_down",self.eventArrowPressed,["down"])
        self.accept("arrow_down-repeat",self.eventArrowPressed,["down"])
        self.accept("f",self.eventAerielView)
        self.accept("w",self.eventPlanter)
        self.accept("e",self.changeSelectedPlanterOpt,["e"])
        self.accept("q",self.changeSelectedPlanterOpt,["e"])
        if not self.haveAxe:
            self.accept('x',self.doNothing)

        #redo taskMgr
        taskMgr.add(self.checkCollisions,'checkCollisionsTask')
        taskMgr.remove('miniGameCheckCollisionsTask')

        #go back to normal view
        shiftPos = camera.posInterval(0.1,Point3(self.x,self.y,self.z))
        normalGameView = Sequence(shiftPos)
        normalGameView.start()


    #check if main character collided with chicken
    def miniGameCheckCollisions(self,task):
        #check collisions for mainChar
        entries = list(self.mainCharGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(render).getZ())
        #if bump into chicken,go back to normal gam
        if (len(entries)>0):
            self.miniGameDone()
        return Task.cont


    #set what happens when up arrow pressed
    def eventUpMini(self):
        self.curPosMini = self.mainChar.getPos()
        self.cameraCurPosMini = camera.getPos()
        x,y,z = base.camera.getPos()
        if y + self.moveMainCharX < 107:
            camera.setPos(x,y + self.moveMainCharY,z)


    #set what happens when down arrow pressed
    def eventDownMini(self):
        self.curPosMini = self.mainChar.getPos()
        self.cameraCurPosMini = camera.getPos()
        x,y,z = base.camera.getPos()
        if y - self.moveMainCharX > -9:
            camera.setPos(x,y - self.moveMainCharY,z)


    #set what happens when right arrow pressed
    def eventRightMini(self):
        self.curPosMini = self.mainChar.getPos()
        self.cameraCurPosMini = camera.getPos()
        x,y,z = base.camera.getPos()
        if x + self.moveMainCharX < 119:
            camera.setPos(x + self.moveMainCharX,y,z)


    #set what happens when left arrow pressed
    def eventLeftMini(self):
        self.curPosMini = self.mainChar.getPos()
        self.cameraCurPosMini = camera.getPos()
        x,y,z = base.camera.getPos()
        if x - self.moveMainCharX > 0:
            camera.setPos(x - self.moveMainCharY,y,z)

    #reload game
    def restartGame(self):
        self.loadStartScreen()

w = Ground()
base.run()