#Author-Robert Marchese
#Description-Generate a 3D model of a boat hull from a table of offsets

import adsk.core, adsk.fusion, adsk.cam, traceback
import json
from math import isnan, radians, sin, cos


def add_spline(point_list, sketch, mirror = 1):
    '''Adds a spline to the current drawing given an set of points in 3-space'''

    # Create an object to store the points in
    points = adsk.core.ObjectCollection.create()
    for p in point_list:
        if p:
            points.add(adsk.core.Point3D.create(mirror*p[0], p[1], p[2]))

    # Create the spline.
    sketch.sketchCurves.sketchFittedSplines.add(points)

    return points


def add_cross_section(sketch, point_list, mirror = 1):
    '''Adds a polygon for a list of cross section verticies'''

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
    ''' Apply a scale factor to all the values in a list '''

    out_list = []
    for point in in_list:
        out_list.append([scale * a for a in point])

    return out_list


def rotate_point(cy, cz, angle, p):
    '''rotate by an angle around a point in the yz-plane'''
    s = sin(angle)
    c = cos(angle)

    # translate point back to origin:
    p[1] -= cy
    p[2] -= cz

    # rotate point
    ynew = p[2] * s + p[1] * c
    znew = p[2] * c - p[1] * s

    # translate point back:
    p[1] = ynew + cy
    p[2] = znew + cz

    return p;


def rake_angle(offsets, st_index, angle):
    ''' Apply a rake angle at the give section (usually bow or transom)'''

    xc_original = offsets['sections'][st_index]
    #logger.debug("original section " + str(st_index) + " points\n" + str(xc_original))

    # Angle is given in degrees from the baseline
    angle = radians(angle)

    # Assume angle taken at top of section
    y0 = xc_original[0][1]
    z0 = xc_original[0][2]

    # Apply rotation in xz plane around y = y0 to sections
    xc_new = []
    for pt in xc_original:
        pt = list(pt)
        pt = rotate_point(y0, z0, angle, pt)
        xc_new.append(pt)
    offsets['sections'][st_index] = xc_new

    #logger.debug("modified section " + str(st_index) + " points\n" + str(xc_new))

    # Apply rotation in xz plane around y = y0 to lines
    for name,coords in offsets['lines'].items():
        if coords[st_index]:
            #logger.debug("modifying " + str(name) + " at station " + str(st_index))
            pt = list(coords[st_index])
            pt = rotate_point(y0, z0, angle, pt)
            coords[st_index] = pt
        #else:
        #    logger.debug("ignoring " + str(name) + " at station " + str(st_index))

    return offsets 


def draw_offsets(design, offset_data):
    ''' Draw the lines and sections represented by the offset table
    on a new component '''
    # Create a new component.
    rootComp = design.rootComponent
    trans = adsk.core.Matrix3D.create()
    occ = rootComp.occurrences.addNewComponent(trans)
    newComp = occ.component

    # Create a new sketch on the xy plane.
    sketch = newComp.sketches.add(rootComp.xYConstructionPlane)

    # Apply optional rake angles at bow and transom
    bindex = 0
    offset_data = rake_angle(offset_data, bindex, 18)
    tindex = len(offset_data['sections']) - 1
    offset_data = rake_angle(offset_data, tindex, -25)

    # Create a spline (two of them actually) for each line
    for name,coords in offset_data['lines'].items():
        coords = scale_coordinates(coords, .1) # mm to cm
        add_spline(coords, sketch, 1)
        add_spline(coords, sketch,-1)

    # Create the cross sections
    for i,section in enumerate(offset_data['sections']):
        section = scale_coordinates(section, .1) # mm to cm
        #newConstPlane = add_offset_plane(newComp, sketch, section[0][2])
        #newSketch = newComp.sketches.add(newConstPlane)
        add_cross_section(sketch, section, 1)
        add_cross_section(sketch, section,-1)

    # Testing orientation of angled planes
    #for i,section in enumerate(offset_data['sections']):
    #    section = scale_coordinates(section, .1) # mm to cm
    #    newConstPlane = add_plane_at_an_angle(newComp, sketch, section, -25)

    return newComp


def get_user_file(ui):
    '''User select offset file to open'''

    # Set up the file dialog.
    msg = ''
    fileDlg = ui.createFileDialog()
    fileDlg.isMultiSelectEnabled = False
    fileDlg.title = 'Open'
    fileDlg.filter = '*.json'
    dlgResult = fileDlg.showOpen()
    if dlgResult == adsk.core.DialogResults.DialogOK:
        user_file = fileDlg.filenames[0]
        return user_file
    else:
        return None


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        design = app.activeProduct
        if not design:
            ui.messageBox('No active Fusion 360 design', 'No Design')
            return

        user_file = get_user_file(ui);
        if user_file:
            with open(user_file, 'r') as f:
                offset_data = json.load(f)
        else:
            return

        #TODO: Verify input file
        draw_offsets(design, offset_data)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
