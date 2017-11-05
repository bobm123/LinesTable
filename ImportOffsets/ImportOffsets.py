#Author-Robert Marchese
#Description-Generate a 3D model of a boat hull from a table of offsets

import adsk.core
import adsk.fusion
import json
import os
import  traceback

from . import offsets_draw
from . import offsets_reader

# Globals
_app = None
_ui  = None

# Global set of event handlers to keep them referenced for the duration of the command
_handlers = []

# Command inputs
_roTextBox = adsk.core.TextBoxCommandInput.cast(None)
_errMessage = adsk.core.TextBoxCommandInput.cast(None)
_numTeeth = adsk.core.StringValueCommandInput.cast(None)
_getOffsetFile = adsk.core.TextBoxCommandInput.cast(None)
_bowAngle = adsk.core.StringValueCommandInput.cast(None)
_transomAngle = adsk.core.StringValueCommandInput.cast(None)
_offsetFilename = adsk.core.StringValueCommandInput.cast(None)


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
            # Run the actual command code here

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
            #if changedInput.id == 

            # Determine what changed from changedInput.id and act on it
            #if changedInput.id == 'pressureAngle':
            #    if _pressureAngle.selectedItem.name == 'Custom':
            #        _pressureAngleCustom.isVisible = True
            #    else:
            #        _pressureAngleCustom.isVisible = False

            if changedInput.id == 'select_file_button':
                filename = get_user_file()
                if filename:
                    fn = os.path.split(filename)[-1]
                    _roTextBox.text = 'Using:\n{}'.format(fn)

            elif changedInput.id == 'offset_filename':
                    _ui.messageBox("TODO: verify that\n{} exists".format(_offsetFilename.value))

            else:
                    _ui.messageBox("changed input for\n{}".format(changedInput.id))

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

            #_errMessage.text = 'Add some more parameters'
            #eventArgs.areInputsValid = False

            # Make sure user inputs are reasonable
            try:
                bowAngle = float(_bowAngle.value)
            except ValueError:
                _errMessage.text = 'The bow angle must be a number.'
                eventArgs.areInputsValid = False
                return False

            if bowAngle > 135 or bowAngle < 45:
                _errMessage.text = 'The bow angle must be between 45 adn 135 deg'
                eventArgs.areInputsValid = False
                return

            try:
                transomAngle = float(_transomAngle.value)
            except ValueError:
                _errMessage.text = 'The transom angle must be a number.'
                eventArgs.areInputsValid = False
                return False

            if transomAngle > 135 or transomAngle < 45:
                _errMessage.text = 'The transom angle must be between 45 adn 135 deg'
                eventArgs.areInputsValid = False
                return

            # Make sure user inputs are reasonable
            if not _numTeeth.value.isdigit():
                _errMessage.text = 'The number of teeth must be a whole number.'
                eventArgs.areInputsValid = False
                return
            else:
                numTeeth = int(_numTeeth.value)

            if numTeeth < 4:
                _errMessage.text = 'The number of teeth must be 4 or more.'
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

            bowAngle = '90'
            bowAngleAttrib = des.attributes.itemByName('ImportOffset', 'bowAngle')
            if bowAngleAttrib:
                bowAngle = bowAngleAttrib.value

            transomAngle = '90'
            transomAngleAttrib = des.attributes.itemByName('ImportOffset', 'transomAngle')
            if transomAngleAttrib:
                transomAngle = transomAngleAttrib.value

            numTeeth = '24'
            numTeethAttrib = des.attributes.itemByName('ImportOffset', 'numTeeth')
            if numTeethAttrib:
                numTeeth = numTeethAttrib.value

            # Connect to the variable the command will provide inputs for
            global _roTextBox, _getOffsetFile, _numTeeth, _bowAngle, _transomAngle, _errMessage, _offsetFilename

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
            _roTextBox = inputs.addTextBoxCommandInput('readonly_textBox_1', '', 'Select a file to import', 2, True)
            _roTextBox.isFullWidth = True

            # Add additional UI widgets here
            # Create bool value input with button style that can be clicked.
            _getOffsetFile = inputs.addBoolValueInput('select_file_button', 'Select File', False, 'resources/filebutton', True)

            # Dummy filename
            offsetFilename = ''
            _offsetFilename = inputs.addStringValueInput('offset_filename', '', offsetFilename)

            _bowAngle = inputs.addStringValueInput('bowAngle', 'Bow Angle', bowAngle)  
            _transomAngle = inputs.addStringValueInput('transomAngle', 'Tramnsom Angle', transomAngle)

            # Dummy number of teeth
            _numTeeth = inputs.addStringValueInput('numTeeth', 'Number of Teeth', numTeeth)  

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

'''
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
'''