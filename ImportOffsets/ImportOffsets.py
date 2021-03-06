#Author-Robert Marchese
#Description-Generate a 3D model of a boat hull from a table of offsets

import adsk.core
import adsk.fusion
import json
import math
import os
import  traceback

from . import offsets_draw
from . import offsets_reader

# Globals
_app = None
_ui  = None

# Global set of event handlers to keep them referenced for the duration of the command
_handlers = []

# current set of offset data points (a dicitonary of lines and cross sections)
_offset_data = {} # TODO: pass values in attributes
_user_filename = '' # TODO: save in attributes

# Command inputs
_roTextBox = adsk.core.TextBoxCommandInput.cast(None)
_getOffsetFile = adsk.core.TextBoxCommandInput.cast(None)
_bowAngle = adsk.core.ValueCommandInput.cast(None)
_transomAngle = adsk.core.ValueCommandInput.cast(None)
_scaleFactor = adsk.core.ValueCommandInput.cast(None)
_halfHull = adsk.core.DropDownCommandInput.cast(None)
_errMessage = adsk.core.TextBoxCommandInput.cast(None)


# Event handler that reacts to any changes the user makes to any of the command inputs.
class IotCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            inputs = eventArgs.inputs
            cmdInput = eventArgs.input

            tableInput = inputs.itemById('table')
            if cmdInput.id == 'tableAdd':
                addRowToTable(tableInput)
            elif cmdInput.id == 'tableDelete':
                if tableInput.selectedRow == -1:
                    _ui.messageBox('Select one row to delete.')
                else:
                    tableInput.deleteRow(tableInput.selectedRow)

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler that reacts to when the command is destroyed. This terminates the script.
class IotCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # When the command is done, terminate the script
            # This will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the execute event.
class IotCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            unitsMgr = _app.activeProduct.unitsManager

            global _offset_data, _user_filename

            if not _offset_data:
                _ui.messageBox('Load an offset table')
                return

            # Run the actual command code here
            des = adsk.fusion.Design.cast(_app.activeProduct)
            attribs = des.attributes
            attribs.add('ImportOffset', 'filename', str(_user_filename))

            bindex = 0
            tindex = len(_offset_data['sections']) - 1

            if 'angle' in _offset_data:
                bowAngle = _offset_data['angle'][bindex]
                transomAngle = _offset_data['angle'][tindex]
            else:
                bowAngle = math.degrees(unitsMgr.evaluateExpression(_bowAngle.expression, "deg"))
                transomAngle = math.degrees(unitsMgr.evaluateExpression(_transomAngle.expression, "deg"))

            _offset_data = offsets_reader.rake_angle(_offset_data, bindex, 90 - bowAngle)
            _offset_data = offsets_reader.rake_angle(_offset_data, tindex, 90 - transomAngle)

            if _halfHull.selectedItem.name == 'Full':
                half_hull = False
            else:
                half_hull = True

            scale_factor = float(_scaleFactor.value)
            offsets_draw.draw(des, _offset_data, scale_factor, half_hull)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the inputChanged event.
class IotCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input

            global _roTextBox, _offset_data # TODO: pass values in attributes

            # Determine what changed from changedInput.id and act on it
            if changedInput.id == 'select_file_button':
                filename = get_user_file()
                if filename:
                    fn = os.path.split(filename)[-1]
                    if filename.endswith('.json'):
                        _roTextBox.text = 'Using:\n{}'.format(fn)
                        with open(filename, 'r') as f:
                            _offset_data = json.load(f)
                            _user_filename = filename
                    elif filename.endswith('.csv'):
                        _roTextBox.text = 'Using:\n{}'.format(fn)
                        _offset_data = offsets_reader.offset_reader(filename)
                        _user_filename = filename

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the validateInputs event.
class IotCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
            unitsMgr = _app.activeProduct.unitsManager

            _errMessage.text = ''

            bowAngle = math.degrees(unitsMgr.evaluateExpression(_bowAngle.expression, "deg"))
            if bowAngle > 135 or bowAngle < 45:
                _errMessage.text = 'The bow angle must be between 45 and 135 deg'
                eventArgs.areInputsValid = False
                return

            transomAngle = math.degrees(unitsMgr.evaluateExpression(_transomAngle.expression, "deg"))
            if transomAngle > 135 or transomAngle < 45:
                _errMessage.text = 'The transom angle must be between 45 adn 135 deg'
                eventArgs.areInputsValid = False
                return

            scaleFactor = _scaleFactor.value
            if scaleFactor < 0:
                _errMessage.text = 'scale factor must be positive'
                eventArgs.areInputsValid = False
                return

            if not _offset_data:
                _errMessage.text = 'Select a file to import'
                eventArgs.areInputsValid = False
                return

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler that reacts when the command definitio is executed which
# results in the command being created and this event being fired.
class IotCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            # Verify that a Fusion design is active.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            if not des:
                _ui.messageBox('A Fusion design must be active when invoking this command.')
                return()

            getOffsetFile = False

            initialBowAngle = 90.0 * (math.pi / 180)
            bowAngleAttrib = des.attributes.itemByName('ImportOffset', 'bowAngle')
            if bowAngleAttrib:
                initialBowAngle = bowAngleAttrib.value

            initialTransomAngle = 90.0 * (math.pi / 180)
            transomAngleAttrib = des.attributes.itemByName('ImportOffset', 'transomAngle')
            if transomAngleAttrib:
                initialTransomAngle = transomAngleAttrib.value

            scaleFactor = '0.1'
            scaleFactorAttrib = des.attributes.itemByName('ImportOffset', 'scaleFactor')
            if scaleFactorAttrib:
                scaleFactor = scaleFactorAttrib.value

            # Connect to the variable the command will provide inputs for
            global _roTextBox, _getOffsetFile, _bowAngle, _transomAngle
            global _scaleFactor, _halfHull, _errMessage

            # Connect to additional command created events
            onDestroy = IotCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            # Connect to the execute event
            onExecute = IotCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)

            # Connect to the input changed event.
            onInputChanged = IotCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)

            # Connect to the validate inputs event
            onValidateInputs = IotCommandValidateInputsHandler()
            cmd.validateInputs.add(onValidateInputs)
            _handlers.append(onValidateInputs)

            # Get the CommandInputs collection associated with the command.
            inputs = cmd.commandInputs

            # Create a read only textbox input. 2nd param is a field lable
            _roTextBox = inputs.addTextBoxCommandInput('readonly_textBox_1', '', '', 2, True)
            _roTextBox.isFullWidth = True

            # Add additional UI widgets here
            # Create bool value input with button style that can be clicked.
            _getOffsetFile = inputs.addBoolValueInput('select_file_button', 'Select File', False, 'resources/filebutton', True)

            bowAngle = adsk.core.ValueInput.createByReal(initialBowAngle)
            _bowAngle = inputs.addValueInput('bowAngle', 'Bow Angle', 'deg', bowAngle)

            transomAngle = adsk.core.ValueInput.createByReal(initialTransomAngle)
            _transomAngle = inputs.addValueInput('transomAngle', 'Transom Angle', 'deg', transomAngle)

            _scaleFactor = inputs.addValueInput('scaleFactor', 'Scale Factor', '', adsk.core.ValueInput.createByReal(float(scaleFactor)))

            # Create dropdown input with radio style.
            _halfHull = inputs.addDropDownCommandInput('Generate Hull', 'Generate Hull', adsk.core.DropDownStyles.LabeledIconDropDownStyle);
            halfHullItems = _halfHull.listItems
            halfHullItems.add('Half', True, '')
            halfHullItems.add('Full', False, '')

            # Add an error message box at bottom
            _errMessage = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
            _errMessage.isFullWidth = True

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def get_user_file():
    '''User select offset file to open'''
    # Set up the file dialog.
    fileDlg = _ui.createFileDialog()
    fileDlg.isMultiSelectEnabled = False
    fileDlg.title = 'Open'
    fileDlg.filter = '*.json;*.csv'
    dlgResult = fileDlg.showOpen()
    if dlgResult == adsk.core.DialogResults.DialogOK:
        user_file = fileDlg.filenames[0]
        return user_file
    else:
        return None


def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        # Get the existing command definition or create it if it doesn't already exist.
        cmdDef = _ui.commandDefinitions.itemById('cmdImportOffsetsTable')
        if not cmdDef:
            cmdDef = _ui.commandDefinitions.addButtonDefinition('cmdImportOffsetsTable', 'Import Offsets Table', 'Import coordinates from a table of offsets.')

        # Connect to the command created event.
        onCommandCreated = IotCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        # Execute the command definition.
        cmdDef.execute()

        # Prevent this module from being terminated when the script returns, because we are waiting for event handlers to fire.
        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
