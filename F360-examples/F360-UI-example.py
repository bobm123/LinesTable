#Author-Autodesk Inc.
#Description-Demo command input examples
import adsk.core, adsk.fusion, traceback

_app = None
_ui  = None
_rowNumber = 0

# Global set of event handlers to keep them referenced for the duration of the command
_handlers = []

# Adds a new row to the table.
def addRowToTable(tableInput):
    # Get the CommandInputs object associated with the parent command.
    cmdInputs = adsk.core.CommandInputs.cast(tableInput.commandInputs)
    
    # Create three new command inputs.
    valueInput = cmdInputs.addValueInput('TableInput_value{}'.format(_rowNumber), 'Value', 'cm', adsk.core.ValueInput.createByReal(_rowNumber))
    stringInput =  cmdInputs.addStringValueInput('TableInput_string{}'.format(_rowNumber), 'String', str(_rowNumber))
    spinnerInput = cmdInputs.addIntegerSpinnerCommandInput('spinnerInt{}'.format(_rowNumber), 'Integer Spinner', 0 , 100 , 2, int(_rowNumber))
    
    # Add the inputs to the table.
    row = tableInput.rowCount
    tableInput.addCommandInput(valueInput, row, 0)
    tableInput.addCommandInput(stringInput, row, 1)
    tableInput.addCommandInput(spinnerInput, row, 2)
    
    # Increment a counter used to make each row unique.
    global _rowNumber
    _rowNumber = _rowNumber + 1


# Event handler that reacts to any changes the user makes to any of the command inputs.
class MyCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
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
class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # When the command is done, terminate the script
            # This will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler that reacts when the command definitio is executed which
# results in the command being created and this event being fired.
class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            # Connect to the command destroyed event.
            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            # Connect to the input changed event.           
            onInputChanged = MyCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)    

            # Get the CommandInputs collection associated with the command.
            inputs = cmd.commandInputs

            # Create a tab input.
            tabCmdInput1 = inputs.addTabCommandInput('tab_1', 'Tab 1')
            tab1ChildInputs = tabCmdInput1.children

            # Create a read only textbox input.
            tab1ChildInputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', 'This is an example of a read-only text box.', 2, True)

            # Create an editable textbox input.
            tab1ChildInputs.addTextBoxCommandInput('writable_textBox', 'Text Box 2', 'This is an example of an editable text box.', 2, False)
            
            # Create a message that spans the entire width of the dialog by leaving out the "name" argument.
            message = '<div align="center">A "full width" message using <a href="http:fusion360.autodesk.com">html.</a></div>'
            tab1ChildInputs.addTextBoxCommandInput('fullWidth_textBox', '', message, 1, True)            

            # Create a selection input.
            selectionInput = tab1ChildInputs.addSelectionInput('selection', 'Select', 'Basic select command input')
            selectionInput.setSelectionLimits(0)

            # Create a string value input.
            strInput = tab1ChildInputs.addStringValueInput('string', 'Text', 'Basic string command input')

            # Create value input.
            tab1ChildInputs.addValueInput('value', 'Value', 'cm', adsk.core.ValueInput.createByReal(0.0))

            # Create bool value input with checkbox style.
            tab1ChildInputs.addBoolValueInput('checkbox', 'Checkbox', True, '', False)

            # Create bool value input with button style that can be clicked.
            tab1ChildInputs.addBoolValueInput('buttonClick', 'Click Button', False, 'resources/button', True)

            # Create bool value input with button style that has a state.
            tab1ChildInputs.addBoolValueInput('buttonState', 'State Button', True, 'resources/button', True)

            # Create float slider input with two sliders.
            tab1ChildInputs.addFloatSliderCommandInput('floatSlider', 'Float Slider', 'cm', 0, 10.0, True)

            # Create float slider input with two sliders and a value list.
            floatValueList = [1.0, 3.0, 4.0, 7.0]
            tab1ChildInputs.addFloatSliderListCommandInput('floatSlider2', 'Float Slider 2', 'cm', floatValueList)

            # Create float slider input with two sliders and visible texts.
            floatSlider3 = tab1ChildInputs.addFloatSliderCommandInput('floatSlider3', 'Float Slider 3', '', 0, 50.0, False)
            floatSlider3.setText('Min', 'Max')

            # Create integer slider input with one slider.
            tab1ChildInputs.addIntegerSliderCommandInput('intSlider', 'Integer Slider', 0, 10);
            valueList = [1, 3, 4, 7, 11]

            # Create integer slider input with two sliders and a value list.
            tab1ChildInputs.addIntegerSliderListCommandInput('intSlider2', 'Integer Slider 2', valueList)

            # Create float spinner input.
            tab1ChildInputs.addFloatSpinnerCommandInput('spinnerFloat', 'Float Spinner', 'cm', 0.2 , 9.0 , 2.2, 1)

            # Create integer spinner input.
            tab1ChildInputs.addIntegerSpinnerCommandInput('spinnerInt', 'Integer Spinner', 2 , 9 , 2, 3)

            # Create dropdown input with checkbox style.
            dropdownInput = tab1ChildInputs.addDropDownCommandInput('dropdown', 'Dropdown 1', adsk.core.DropDownStyles.CheckBoxDropDownStyle)
            dropdownItems = dropdownInput.listItems
            dropdownItems.add('Item 1', False, 'resources/One')
            dropdownItems.add('Item 2', False, 'resources/Two')

            # Create dropdown input with icon style.
            dropdownInput2 = tab1ChildInputs.addDropDownCommandInput('dropdown2', 'Dropdown 2', adsk.core.DropDownStyles.LabeledIconDropDownStyle);
            dropdown2Items = dropdownInput2.listItems
            dropdown2Items.add('Item 1', True, 'resources/One')
            dropdown2Items.add('Item 2', False, 'resources/Two')

            # Create dropdown input with radio style.
            dropdownInput3 = tab1ChildInputs.addDropDownCommandInput('dropdown3', 'Dropdown 3', adsk.core.DropDownStyles.LabeledIconDropDownStyle);
            dropdown3Items = dropdownInput3.listItems
            dropdown3Items.add('Item 1', True, '')
            dropdown3Items.add('Item 2', False, '')

            # Create dropdown input with test list style.
            dropdownInput4 = tab1ChildInputs.addDropDownCommandInput('dropdown4', 'Dropdown 4', adsk.core.DropDownStyles.TextListDropDownStyle);
            dropdown4Items = dropdownInput4.listItems
            dropdown4Items.add('Item 1', True, '')
            dropdown4Items.add('Item 2', False, '')

            # Create single selectable button row input.
            buttonRowInput = tab1ChildInputs.addButtonRowCommandInput('buttonRow', 'Single Select Buttons', False)
            buttonRowInput.listItems.add('Item 1', False, 'resources/One')
            buttonRowInput.listItems.add('Item 2', False, 'resources/Two')

            # Create multi selectable button row input.
            buttonRowInput2 = tab1ChildInputs.addButtonRowCommandInput('buttonRow2', 'Multi-select Buttons', True)
            buttonRowInput2.listItems.add('Item 1', False, 'resources/One')
            buttonRowInput2.listItems.add('Item 2', False, 'resources/Two')

            # Create tab input 2
            tabCmdInput2 = inputs.addTabCommandInput('tab_2', 'Tab 2')
            tab2ChildInputs = tabCmdInput2.children

            # Create group input.
            groupCmdInput = tab2ChildInputs.addGroupCommandInput('group', 'Group')
            groupCmdInput.isExpanded = True
            groupCmdInput.isEnabledCheckBoxDisplayed = True
            groupChildInputs = groupCmdInput.children
            
            # Create radio button group input.
            radioButtonGroup = groupChildInputs.addRadioButtonGroupCommandInput('radioButtonGroup', 'Radio button group')
            radioButtonItems = radioButtonGroup.listItems
            radioButtonItems.add("Item 1", False)
            radioButtonItems.add("Item 2", False)
            radioButtonItems.add("Item 3", False)
            
            # Create image input.
            groupChildInputs.addImageCommandInput('image', 'Image', "resources/image.png")
            
            # Create direction input 1.
            directionCmdInput = tab2ChildInputs.addDirectionCommandInput('direction', 'Direction1')
            directionCmdInput.setManipulator(adsk.core.Point3D.create(0, 0, 0), adsk.core.Vector3D.create(1, 0, 0))
            
            # Create direction input 2.
            directionCmdInput2 = tab2ChildInputs.addDirectionCommandInput('direction2', 'Direction 2', 'resources/One')
            directionCmdInput2.setManipulator(adsk.core.Point3D.create(0, 0, 0), adsk.core.Vector3D.create(0, 1, 0)) 
            directionCmdInput2.isDirectionFlipped = True
            
            # Create distance value input 1.
            distanceValueInput = tab2ChildInputs.addDistanceValueCommandInput('distanceValue', 'DistanceValue', adsk.core.ValueInput.createByReal(2))
            distanceValueInput.setManipulator(adsk.core.Point3D.create(0, 0, 0), adsk.core.Vector3D.create(1, 0, 0))
            distanceValueInput.minimumValue = 0
            distanceValueInput.isMinimumValueInclusive = True
            distanceValueInput.maximumValue = 10
            distanceValueInput.isMaximumValueInclusive = True
            
            # Create distance value input 2.
            distanceValueInput2 = tab2ChildInputs.addDistanceValueCommandInput('distanceValue2', 'DistanceValue 2', adsk.core.ValueInput.createByReal(1))
            distanceValueInput2.setManipulator(adsk.core.Point3D.create(0, 0, 0), adsk.core.Vector3D.create(0, 1, 0))
            distanceValueInput2.expression = '1 in'
            distanceValueInput2.hasMinimumValue = False
            distanceValueInput2.hasMaximumValue = False
            
            # Create table input
            tableInput = tab2ChildInputs.addTableCommandInput('table', 'Table', 3, '1:1:1')
            addRowToTable(tableInput)

            # Add inputs into the table.            
            addButtonInput = tab2ChildInputs.addBoolValueInput('tableAdd', 'Add', False, '', True)
            tableInput.addToolbarCommandInput(addButtonInput)
            deleteButtonInput = tab2ChildInputs.addBoolValueInput('tableDelete', 'Delete', False, '', True)
            tableInput.addToolbarCommandInput(deleteButtonInput)
            
            # Create angle value input.
            angleValueInput = tab2ChildInputs.addAngleValueCommandInput('angleValue', 'AngleValue', adsk.core.ValueInput.createByString('30 degree'))
            angleValueInput.setManipulator(adsk.core.Point3D.create(0, 0, 0), adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 0, 1))
            angleValueInput.hasMinimumValue = False
            angleValueInput.hasMaximumValue = False
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        # Get the existing command definition or create it if it doesn't already exist.
        cmdDef = _ui.commandDefinitions.itemById('cmdInputsSample')
        if not cmdDef:
            cmdDef = _ui.commandDefinitions.addButtonDefinition('cmdInputsSample', 'Command Inputs Sample', 'Sample to demonstrate various command inputs.')

        # Connect to the command created event.
        onCommandCreated = MyCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        # Execute the command definition.
        cmdDef.execute()

        # Prevent this module from being terminated when the script returns, because we are waiting for event handlers to fire.
        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))