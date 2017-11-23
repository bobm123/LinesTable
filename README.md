## Import Offsets Table

This project is a tool that generate a 3D model of a ship's hull given a table of points in the form of a traditional shipwright's offset or lines table. These tables contain, in theory, all the information needed to model a ships hull, but locating the individual points using 3D modeling tools can be tedious. Two drawing applications are the target for this project: OpenSCAD and Fusion 360. OpenSCAD is designed to define objects grammatically, so seems like a good first step, but has limited ability to handle curves. Fusion 360 includes 3D modeling and design tools with API for both Python and C++. While these can be challenging to use, they unlock a rich array of design features.

Inputs are intended to be CSV (comma seperated values) files containing the offset data. As an interim solution they also include a JSON format of the specific data needed by the applicatoins. To make problem a little easier to handle, the tool is fairly opinionated about the table's format. This shouldn't too much of a restrictions as these tables follow a fairly constant pattern. Some human intervention will inevitably be needed. When necessary this should be easy to do with spreadsheet editing tools. I've been using Google docs to generate the test files, but any application that can produce CSV files should be fine.

Here is an example of a fairly typical table of offsets. This one was taken from a reprint of an article by Howard Chapelle on the Chesepeak Bay Sharpie found 
[here](http://www.duckworksmagazine.com/04/s/articles/chapelle/index.cfm)

![Chesapeake Bay Sharpie Spreadsheet][sharpie_offsets_original]

[sharpie_offsets_original]: https://github.com/bobm123/LinesTable/blob/master/images/ChesapeakeBaySharpie.png

One thing that stands out is that the values are given in units of "feet-inches-eights" or eights of an inch. So an entry of "1-7-4" would be equal to 1 foot, 7 and 4/8 inches for a total of 19.5 inches. This is the first source of confusion the tool will help you deal with; measurements in this format will be converted to decimal inches.

The next is the heights and widths rows. These are usually given once per section with "dittos" for the rest. The import tool will expand column 1 so each row is associated with a height or width measurements. The widths and heights will become the x and y-axis position when the points are imported.

The Heights section tell the vertical distance from a baseline. The baseline can be either above or below the hull's "waterline" so your drawing may appear upside down when imported. 

Widths are another somewhat quaint aspect of these tables. Ship designers normally work with "half hulls" because ships are almost always symmetrical and this reduces work. Therefore the width measurements are typically given in "half breadths to the center line".  These become the x-axis measurements.

The stations are the positions alone the length of the ship where the measurements are taken. These will become the z-axis. These measurements are usually evenly spaced, so may appear as a note one the drawing. These should be entered by hand as a new row if necessary. Other information can be added to the table as a comments row with a leading # in the first column.

Here is the the corresponding spreadsheet for the figure above in Google Docs. From there, download as a .csv file.

![Chesapeake Bay Sharpie Spreadsheet][sharpie_offsets]

[sharpie_offsets]: https://github.com/bobm123/LinesTable/blob/master/images/sharpie-gdocs-screenshop.png

When imported in to Fusion 360, will results in a wire-frame drawing

![Chesapeake Bay Sharpie wireframe][sharpie]

[sharpie]: https://github.com/bobm123/LinesTable/blob/master/images/sharpie-f360-screenshop.png

And after a bit more work tracing and modelling structures that go with the imported hull shape, I came up with this model.

![Chesapeake Bay Sharpie model][sharpie_model]

[sharpie_model]: https://github.com/bobm123/LinesTable/blob/master/images/sharpie-model-f360-screenshop.png

The project in divided into three main python files: the CSV table import in offset_reader.py, the Fusion 360 specific drawing functions in offsets_draw.py and the Fusion 360 extensions script in ImportOffsets.py. The offset_reader.py can also be run as a stand alone script for testsing and will eventually be used to produce an optional OpenSCAD output. In this mode it curently produces a JSON file that can optionally be used to import the coordiantes by the Fusion 360 script.


