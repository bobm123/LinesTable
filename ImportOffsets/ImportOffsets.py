#Author-Robert Marchese
#Description-Generate a 3D model of a boat hull from a table of offsets

import adsk.core, adsk.fusion, adsk.cam, traceback
import json


def add_spline(point_list, sketch):
    '''Adds a spline to the current drawing given an set of points in 3-space'''

    # Create an object to store the points in
    points = adsk.core.ObjectCollection.create()

    for p in point_list:
        if p:
            points.add(adsk.core.Point3D.create(*p))

    # Create the spline.
    sketch.sketchCurves.sketchFittedSplines.add(points)

    # Do again for other side (TODO: Mirror?)
    points1 = adsk.core.ObjectCollection.create()
    for p in point_list:
        if p:
            points1.add(adsk.core.Point3D.create(-p[0], p[1], p[2]))

    sketch.sketchCurves.sketchFittedSplines.add(points1)

    return points


def add_cross_section(sketch, point_list, mirror = 1):
    '''Adds a spline to the current drawing given an set of points in 3-space'''

    # TODO: generalize drawing a polygon from list of 2D points
    lines = sketch.sketchCurves.sketchLines;

    # project the first point on the center line at start there
    #p_start = adsk.core.Point3D.create(0, point_list[0][1], 0)
    p_start = adsk.core.Point3D.create(0, point_list[0][1], point_list[0][2])
    p0 = p_start
    for p in point_list:
        #new_line = lines.addByTwoPoints(p0, adsk.core.Point3D.create(p[0], p[1], 0))
        new_line = lines.addByTwoPoints(p0, adsk.core.Point3D.create(mirror*p[0], p[1], p[2]))
        p0 = new_line.endSketchPoint

    # End at last point projected to center line
    #p_end = adsk.core.Point3D.create(0, point_list[-1][1], 0)
    p_end = adsk.core.Point3D.create(0, point_list[-1][1], point_list[-1][2])
    new_line = lines.addByTwoPoints(p0, p_end)

    # Close it by connecting p_end back to P_start
    new_line = lines.addByTwoPoints(p_end, p_start)


def add_offset_plane (comp, sketch, z):
    planes = comp.constructionPlanes
    planeInput = planes.createInput()
    offsetValue = adsk.core.ValueInput.createByReal(z)
    planeInput.setByOffset(comp.xYConstructionPlane, offsetValue)
    planes.add(planeInput)

    return planes[-1]


def add_plane_by_points(comp, sketch, p0, p1, p2):
     
    # TODO: ensure 3 points exist and not collinear
    # TODO: somehow use existing points
    sketchPoints = sketch.sketchPoints
    position = adsk.core.Point3D.create(*p0)
    sk_pt0 = sketchPoints.add(position)
    position = adsk.core.Point3D.create(*p2)
    sk_pt1 = sketchPoints.add(position)
    position = adsk.core.Point3D.create(*p1)
    sk_pt2 = sketchPoints.add(position)

    planes = comp.constructionPlanes
    planeInput = planes.createInput()
    planeInput.setByThreePoints(sk_pt0, sk_pt1, sk_pt2)
    planes.add(planeInput)

    return planes[-1]


def add_plane_at_an_angle(comp, sketch, section, angle):

    lines = sketch.sketchCurves.sketchLines;
    p0 = adsk.core.Point3D.create(*section[0])
    p1 = adsk.core.Point3D.create(*section[1])
    sectionLine = lines.addByTwoPoints(p0, p1)
    angle = adsk.core.ValueInput.createByReal(angle)
    sketchPlane = sketch.referencePlane

    planes = comp.constructionPlanes
    planeInput = planes.createInput()
    planeInput.setByAngle(sectionLine, angle, sketchPlane)
    planes.add(planeInput)

    return planes[-1]


def scale_coordinates(in_list, scale):
    # TODO: make this a numpy array operation
    out_list = []
    for point in in_list:
        out_list.append([scale * a for a in point])

    return out_list


def rake_angle(offsets, st_index, angle):
    print("modifying section points: " + str(offsets['sections'][st_index]))
    return offsets


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        #ui.messageBox('Hello script')

        design = app.activeProduct
        if not design:
            ui.messageBox('No active Fusion 360 design', 'No Design')
            return

        # Get the root component of the active design.
        rootComp = design.rootComponent

        # Create a new occurrence.
        trans = adsk.core.Matrix3D.create()
        occ = rootComp.occurrences.addNewComponent(trans)

        # Get the associated component.
        newComp = occ.component

        # Create a new sketch on the xy plane.
        sketch = newComp.sketches.add(rootComp.xYConstructionPlane)

        # Get offsets from the user's file
        msg = ''
        # Set styles of file dialog.
        fileDlg = ui.createFileDialog()
        fileDlg.isMultiSelectEnabled = False
        fileDlg.title = 'Open'
        fileDlg.filter = '*.json'
        dlgResult = fileDlg.showOpen()
        if dlgResult == adsk.core.DialogResults.DialogOK:
            #for filename in fileDlg.filenames:
            json_file = fileDlg.filenames[0]
            with open(json_file, 'r') as f:
                offset_data = json.load(f)

        #TODO: Verify input file

        # Apply optional rake angles at bow and transom
        bindex = 0
        offset_data = rake_angle(offset_data, bindex, 18)
        tindex = len(offset_data['sections']) - 1
        offset_data = rake_angle(offset_data, tindex, -25)

        # Create a spline (two of them actually) for each line
        for name,coords in offset_data['lines'].items():
            coords = scale_coordinates(coords, .1) # mm to cm
            add_spline(coords, sketch)
        
        # Create construction planes for the cross sections
        for i,section in enumerate(offset_data['sections']):
            section = scale_coordinates(section, .1) # mm to cm
            #newConstPlane = add_offset_plane(newComp, sketch, section[0][2])
            #newSketch = newComp.sketches.add(newConstPlane)
            #add_cross_section(newSketch, section)
            add_cross_section(sketch, section, 1)
            add_cross_section(sketch, section,-1)

        # Testing orientation of angled planes
        #for i,section in enumerate(offset_data['sections']):
        #    section = scale_coordinates(section, .1) # mm to cm
        #    newConstPlane = add_plane_at_an_angle(newComp, sketch, section, -25)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
