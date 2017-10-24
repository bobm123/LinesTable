import adsk.core, adsk.fusion, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Create a document.
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)

        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        # Get the root component of the active design
        rootComp = design.rootComponent

        # Create sketch
        sketches = rootComp.sketches
        sketch = sketches.add(rootComp.xZConstructionPlane)
        
        # Create sketch circle
        sketchCircles = sketch.sketchCurves.sketchCircles
        centerPoint = adsk.core.Point3D.create(0, 0, 0)
        sketchCircles.addByCenterRadius(centerPoint, 5.0)        
        
        # Get the profile defined by the circle
        prof = sketch.profiles.item(0)

        # Create an extrusion input
        extrudes = rootComp.features.extrudeFeatures
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        # Define that the extent is a distance extent of 5 cm
        distance = adsk.core.ValueInput.createByReal(5)
        # Set the distance extent to be symmetric
        extInput.setDistanceExtent(True, distance)
        # Set the extrude to be a solid one
        extInput.isSolid = True
        
        # Create an cylinder
        extrude = extrudes.add(extInput)

        # Create sketch line
        sketchLines = sketch.sketchCurves.sketchLines
        startPoint = adsk.core.Point3D.create(5, 5, 0)
        endPoint = adsk.core.Point3D.create(5, 10, 0)
        sketchLineOne = sketchLines.addByTwoPoints(startPoint, endPoint)
        endPointTwo = adsk.core.Point3D.create(10, 5, 0)
        sketchLineTwo = sketchLines.addByTwoPoints(startPoint, endPointTwo)
        
        # Create three sketch points
        sketchPoints = sketch.sketchPoints
        positionOne = adsk.core.Point3D.create(0, 5.0, 0)
        sketchPointOne = sketchPoints.add(positionOne)
        positionTwo = adsk.core.Point3D.create(5.0, 0, 0)
        sketchPointTwo = sketchPoints.add(positionTwo)
        positionThree = adsk.core.Point3D.create(0, -5.0, 0)
        sketchPointThree = sketchPoints.add(positionThree)
        
        # Get construction planes
        planes = rootComp.constructionPlanes
        
        # Create construction plane input
        planeInput = planes.createInput()
        
        # Add construction plane by offset
        offsetValue = adsk.core.ValueInput.createByReal(3.0)
        planeInput.setByOffset(prof, offsetValue)
        planeOne = planes.add(planeInput)
        
        # Get the health state of the plane
        health = planeOne.healthState
        if health == adsk.fusion.FeatureHealthStates.ErrorFeatureHealthState or health == adsk.fusion.FeatureHealthStates.WarningFeatureHealthState:
            message = planeOne.errorOrWarningMessage
        
        # Add construction plane by angle
        angle = adsk.core.ValueInput.createByString('30.0 deg')
        planeInput.setByAngle(sketchLineOne, angle, prof)
        planes.add(planeInput)
        
        # Add construction plane by two planes
        planeInput.setByTwoPlanes(prof, planeOne)
        planes.add(planeInput)
        
        # Add construction plane by tangent
        cylinderFace = extrude.sideFaces.item(0)
        planeInput.setByTangent(cylinderFace, angle, rootComp.xYConstructionPlane)
        planes.add(planeInput)
        
        # Add construction plane by two edges
        planeInput.setByTwoEdges(sketchLineOne, sketchLineTwo)
        planes.add(planeInput)
        
        # Add construction plane by three points
        planeInput.setByThreePoints(sketchPointOne, sketchPointTwo, sketchPointThree)
        planes.add(planeInput)
        
        # Add construction plane by tangent at point
        planeInput.setByTangentAtPoint(cylinderFace, sketchPointOne)
        planes.add(planeInput)
        
        # Add construction plane by distance on path
        distance = adsk.core.ValueInput.createByReal(1.0)
        planeInput.setByDistanceOnPath(sketchLineOne, distance)
        planes.add(planeInput)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))