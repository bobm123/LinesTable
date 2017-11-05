#Author-Robert Marchese
#Description-Generate a 3D model of a boat hull from a table of offsets

import adsk.core
import adsk.fusion
import json
#from math import isnan, radians, sin, cos
from . import offsets_draw
from . import offsets_reader
import  traceback


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
        offsets_draw.draw(design, offset_data)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
