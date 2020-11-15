from PIL import Image

class TheOutliner(object):
    ''' takes a dict of xy points and
    draws a rectangle around them '''

    def __init__(self):
        self.outlineColor = 255, 0, 0
        self.pic = None
        self.picn = None
        self.minX = 0
        self.minY = 0
        self.maxX = 0
        self.maxY = 0
    def doEverything(self, imgPath, dictPoints, theoutfile):
        self.loadImage(imgPath)
        self.loadBrightPoints(dictPoints)
        self.drawBox()
        self.saveImg(theoutfile)

    def loadImage(self, imgPath):
        self.pic = Image.open(imgPath)
        self.picn = self.pic.load()

    def loadBrightPoints(self, dictPoints):
        '''iterate through all points and

        gather max/min x/y '''


        # an x from the pool (the max/min
        #   must be from dictPoints)
        self.minX = list(list(dictPoints)[0])[0]
        self.maxX = self.minX
        self.minY = list(list(dictPoints)[0])[1]
        self.maxY = self.minY


        for point in list(dictPoints):
            if list(point)[0] < self.minX:
                self.minX = list(point)[0]
            elif list(point)[0] > self.maxX:
                self.maxX = list(point)[0]

            if list(point)[1]< self.minY:
                self.minY = list(point)[1]
            elif list(point)[1] > self.maxY:
                self.maxY = list(point)[1]
    def drawBox(self):
        # drop box around bright points
        
        for x in range(int(self.minX), int(self.maxX)):
            # top bar
            self.picn[x, self.minY] = self.outlineColor
            # bottom bar
            self.picn[x, self.maxY] = self.outlineColor
        for y in range(int(self.minY), int(self.maxY)):
            # left bar

            self.picn[self.minX, y] = self.outlineColor
            # right bar
            self.picn[self.maxX, y] = self.outlineColor
    def saveImg(self, theoutfile):
         self.pic.save(theoutfile, "JPEG")
    def saveBox(self,filename):
    # Create Box
        box = (self.minX, self.minY, self.maxX, self.maxY)

    # Crop Image
        self.pic.crop(box).save(filename)


class ObjectDetector(object):
    ''' returns a list of dicts representing 
        all the objects in the image '''
    def __init__(self):
        self.detail = 4
        self.objects = []
        self.size = 1000
        self.no = 255
        self.close = 100
        self.pic = None
        self.picn = None
        self.brightDict = {}
    def loadImage(self, imgPath):
        self.pic = Image.open(imgPath)
        self.picn = self.pic.load()
        self.picSize = self.pic.size
        self.detail = (self.picSize[0] + self.picSize[1])/2000
        self.size = (self.picSize[0] + self.picSize[1])/8
        # each must be at least 1 -- and the larger

        #   the self.detail is the faster the analyzation will be
        self.detail += 1
        self.size += 1

    def getSurroundingPoints(self, xy):
        ''' returns list of adjoining point '''
        x = xy[0]
        y = xy[1]
        plist = (
            (x-self.detail, y-self.detail), (x, y-self.detail), 
            (x+self.detail, y-self.detail),
            (x-self.detail, y),(x+self.detail, y),
            (x-self.detail, y+self.detail),(x, y+self.detail),
            (x+self.detail,y+self.detail)
            )
        return (plist)

    def getRGBFor(self, x, y):
        try:
            return self.picn[x,y]
        except IndexError as e:
            return 255,255,255

    def readyToBeEvaluated(self, xy):
        try:
            r,g,b = self.picn[xy[0],xy[1]]
            if r==255 and g==255 and b==255:
                return False
        except:
            return False
        return True

    def markEvaluated(self, xy):
        try:
            self.picn[xy[0],xy[1]] = self.no, self.no, self.no
        except:
            pass

    def collectAllObjectPoints(self):
        for x in range(self.pic.size[0]):
            
                for y in range(self.pic.size[1]):
                    
                        r,g,b = self.picn[x,y]
                        if r == self.no and \
                            g == self.no and \
                            b == self.no:
                            # then no more

                            pass
                        else:
                            ol = {}
                            ol[x,y] = "go"
                            pp = []
                            pp.append((x,y))
                            stillLooking = True
                            while stillLooking:
                                if len(pp) > 0:
                                    xe, ye = pp.pop()
                                    # look for adjoining points

                                    for p in self.getSurroundingPoints((xe,ye)):

                                        if self.readyToBeEvaluated((p[0], 
                                        p[1])):
                                            r2,g2,b2 = self.getRGBFor(p[0], 
                                            p[1])
                                            if abs(r-r2) < self.close and \
                                                abs(g-g2) < self.close and \
                                                abs(b-b2) < self.close:
                                                # then its close enough

                                                ol[p[0],p[1]] = "go"
                                                pp.append((p[0],p[1]))

                                            self.markEvaluated((p[0],p[1]))
                                        self.markEvaluated((xe,ye))
                                else:
                                    # done expanding that point
                                    stillLooking = False
                                    if len(ol) > self.size:
                                     self.objects.append(ol)


if __name__ == "__main__":
    print ("Start Process");

    # assumes that the .jpg files are in
    #   working directory 
    theFile = "new2"

    theOutFile = "new2.output"

    import os
    os.listdir('./data')
    for f in os.listdir('./data'):
       if f.find(".jpg") > 0:
            theFile = f
            print ("working on " + theFile + "...")

            theOutFile = theFile + ".out.jpg"
            bbb = ObjectDetector()
            bbb.loadImage('./data/'+theFile)
            print ("     analyzing..")
            print ("     file dimensions: " + str(bbb.picSize))
            print ("        this files object weight: " + str(bbb.size))
            print ("        this files analyzation detail: " + str(bbb.detail))
            bbb.collectAllObjectPoints()
            print ("     objects detected: " +str(len(bbb.objects)))
            drawer = TheOutliner()
            print ("     loading and drawing rectangles..")

            drawer.loadImage('./data/'+theFile)
            idBox=1
            for o in bbb.objects:
                keyler =o.keys()
                print(keyler)
                drawer.loadBrightPoints(o)
                drawer.drawBox()
                idBox=idBox+1
                drawer.saveBox("box_"+str(idBox)+"_"+theOutFile)

            print ("saving image...")
            drawer.saveImg(theOutFile)

            print ("Process complete")
