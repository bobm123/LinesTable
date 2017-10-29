#Author-Robert Marchese
#Description-Working on the User Interface for Import Offsets script here
import adsk.core, adsk.fusion, traceback

# Globals
_app = None
_ui  = None

# Global set of event handlers to keep them referenced for the duration of the command
_handlers = []

# Command inputs
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

            # Determine what changed from changedInput.id and act on it
            # For example
            #if changedInput.id == 'pressureAngle':
            #    if _pressureAngle.selectedItem.name == 'Custom':
            #        _pressureAngleCustom.isVisible = True
            #    else:
            #        _pressureAngleCustom.isVisible = False                    

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
            
            _errMessage.text = 'Add some parameters'
            eventArgs.areInputsValid = False

            # Make sure user inputs are reasonable
            #if not _numTeeth.value.isdigit():
            #    _errMessage.text = 'The number of teeth must be a whole number.'
            #    eventArgs.areInputsValid = False
            #    return
            #else:    
            #    numTeeth = int(_numTeeth.value)
            # 
            #if numTeeth < 4:
            #    _errMessage.text = 'The number of teeth must be 4 or more.'
            #    eventArgs.areInputsValid = False
            #    return
                
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

            # Connect to the variable the command will provide inputs for
            global _errMessage

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
            roTextBox = inputs.addTextBoxCommandInput('readonly_textBox_1', '', 'Select a file to import', 2, True)
     
            # Add additional UI widgets here

            _errMessage = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
            _errMessage.isFullWidth = True

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def run(context):
    ui = None
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
