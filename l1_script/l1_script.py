#Author-
#Description-first script

import adsk.core, adsk.fusion, adsk.cam, traceback
import math

app = adsk.core.Application.get()
ui  = app.userInterface

def createNewComponent():
    # Get the active design.
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
    allOccs = rootComp.occurrences
    newOcc = allOccs.addNewComponent(adsk.core.Matrix3D.create())
    return newOcc.component

def createSphere(rootComp, center, r):
    sketch = rootComp.sketches.add(rootComp.yZConstructionPlane)
    sketchPoints = sketch.sketchPoints
    sketchDimensions = sketch.sketchDimensions
    
    # Get the SketchCircles collection from an existing sketch.
    circles = sketch.sketchCurves.sketchCircles

    # Call an add method on the collection to create a new circle.
    circle_center = center
    
    circle1 = circles.addByCenterRadius(circle_center, r)

    # Get the SketchLines collection from an existing sketch.
    lines = sketch.sketchCurves.sketchLines

    # Call an add method on the collection to create a new line.
    axis = lines.addByTwoPoints(adsk.core.Point3D.create(-1,-4,0), adsk.core.Point3D.create(-1,4,0))
    
    sketch.geometricConstraints.addHorizontal(axis)
    sketch.geometricConstraints.addCoincident(axis.startSketchPoint, circle1)
    sketch.geometricConstraints.addCoincident(axis.endSketchPoint, circle1)
    
    sketch.geometricConstraints.addCoincident(sketch.originPoint, axis)
    sketch.geometricConstraints.addCoincident(circle1.centerSketchPoint,axis)
    sketch.geometricConstraints.addMidPoint(sketch.originPoint, axis)
    
    sketchDimensions.addDiameterDimension(circle1,adsk.core.Point3D.create(4,4,0));
    
    
    prof = sketch.profiles.item(0)
    
    print('profiles: ', len(sketch.profiles))

    revolves = rootComp.features.revolveFeatures

    revInput = revolves.createInput(prof, axis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    angle = adsk.core.ValueInput.createByReal(math.pi*2)        
    
    revInput.setAngleExtent(False, angle)
    
    return revolves.add(revInput)
    
def createCylinder(rootComp, base_center, r, h):
    sketch = rootComp.sketches.add(rootComp.xYConstructionPlane)
    sketchPoints = sketch.sketchPoints
    sketchDimensions = sketch.sketchDimensions
    
    # Get the SketchCircles collection from an existing sketch.
    circles = sketch.sketchCurves.sketchCircles

    # Call an add method on the collection to create a new circle.
    circle_center = base_center
    
    circle1 = circles.addByCenterRadius(circle_center, r)
    sketchDimensions.addDiameterDimension(circle1,adsk.core.Point3D.create(4,4,0))
    
    prof = sketch.profiles.item(0)
    
    #sketch.geometricConstraints.addCoincident(sketch.originPoint, circle1.centerSketchPoint)
    
    extrudes = rootComp.features.extrudeFeatures
    
    exInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    exInput.setOneSideExtent( adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(h)), 
                             adsk.fusion.ExtentDirections.PositiveExtentDirection)
                             
    return extrudes.add(exInput)
    
    
def subtractFeatures(rootComp,s1,slist):
    b1 = s1.bodies.item(0)
    t = adsk.core.ObjectCollection.create()
    
    if type(slist) == type([]):
        for s in slist:
            t.add(s.bodies.item(0))
    else:
        t.add(slist.bodies.item(0))
    
    #b2 = s2.bodies.item(0)
    #print(b1,b2)
    combines = rootComp.features.combineFeatures
    c = combines.createInput(b1,t)
    c.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    return combines.add(c)
    
def move(rootComp, s1, vec):
    t = adsk.core.ObjectCollection.create()
    t.add(s1.bodies.item(0))
    m  = adsk.core.Matrix3D.create()
    v = adsk.core.Vector3D.create(vec[0],vec[1],vec[2])
    m.translation = v
    inp = rootComp.features.moveFeatures.createInput(t,m)
    return rootComp.features.moveFeatures.add(inp)
    
def rotate(rootComp, s1, angs, axis):
    angs = [i/180 * math.pi for i in angs]
    t = adsk.core.ObjectCollection.create()
    t.add(s1.bodies.item(0))
    x  = adsk.core.Matrix3D.create()
    y  = adsk.core.Matrix3D.create()
    z  = adsk.core.Matrix3D.create()
    
    trans = adsk.core.Matrix3D.create()
    origin = adsk.core.Point3D.create(0,0,0)
    
    x.setToRotation(angs[0], adsk.core.Vector3D.create(1,0,0), origin)    
    y.setToRotation(angs[1], adsk.core.Vector3D.create(0,1,0), origin)    
    z.setToRotation(angs[2], adsk.core.Vector3D.create(0,0,1), origin)    
    
    trans.transformBy(x)
    trans.transformBy(y)
    trans.transformBy(z)

    inp = rootComp.features.moveFeatures.createInput(t,trans)
    return rootComp.features.moveFeatures.add(inp)
    
def run(context):
    ui = None
    try:

        #doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        #newC = createNewComponent()

        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        # Get the root component of the active design
        rootComp = design.rootComponent

        features = []
        features += list(rootComp.features.moveFeatures)
        features += list(rootComp.features.combineFeatures)
        features += list(rootComp.features.extrudeFeatures)
        features += list(rootComp.features.revolveFeatures)
        
        features += list(rootComp.sketches)
        

        for s in features:
            #print(s)
            s.deleteMe()

        origin = adsk.core.Point3D.create(0,0,0)
        circle_center = origin
        
        s1 = createSphere(rootComp,circle_center, 7)
        s2 = createSphere(rootComp,circle_center, 6)
        
        subtractFeatures(rootComp,s1,s2)
        
        cyl = createCylinder(rootComp, origin, 2, 10)
        
        #move(rootComp,cyl,[0,1,0])
        print(rootComp.xConstructionAxis)
        rotate(rootComp,cyl,[45,45,0], rootComp.xConstructionAxis)
        
        subtractFeatures(rootComp,s1,[cyl])
        
        



    except:
        print('Failed:\n{}'.format(traceback.format_exc()))
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
