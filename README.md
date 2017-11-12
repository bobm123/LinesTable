Import Offsets Table

A tool to generate a 3D body (hull) given a table of points in the form of a traditional shipwright's offset or lines table. These table are basically spreadsheets but locating the individual points that they represent using 3D modeling tools can be tedious. Two drawing applications are the target for this project: OpenSCAD and Fusion 360. OpenSCAD is designed to define objects grammatically, so seems like a good first step, but has limited ability to handle curves. Fusion 360 includes 3D modeling and design tools with API for both Python and C++. While these can be 

Input intended to be a CSV file containing the offset data. To make problem a little easier to handle, the tool is fairly opinionated about the table's format. This shouldn't too much of a restrictions as these tables follow a fairly constant pattern. Some human intervention will inevitably be needed, but where necessary should be easily done with spreadsheet editing tools.

<fig 1>

Here is an example of a fairly typical table of offsets. One thing that stands out is that the values are given in units of "fee-inch-eights" or eights of an inch. So an entry of "1-7-4" would be equal to 1 foot, 7 and 4/8 inches for a total of 19.5 inches. This is the first source of confusion the tool will help you deal with; measurements in this format will be converted to decimal inches.

The next is the heights and widths rows. These are usually given once per section with "dittos" for the rest. The import too will expand column 1 so each row is associated with a height or width measurements. The widths and heights will become the x and y-axis position when the points are imported.

The Heights section tell the vertical distance from a baseline. The baseline can be either above or below the hull's "waterline" so your drawing may appear upside down when imported. 

Widths are another somewhat quaint aspect of these tables. Ship designers normally work with "half hulls" because ships are almost always symmetrical and this reduces work. Therefor the width measurements are typically given in "half breadths to the center line".  These become the x-axis measurements 

The stations are the positions alone the length of the ship where the measurements are taken. These will become the z-axis. These measurements are usually evenly spaced, so may appear as a note one the drawing. The should be entered in the table by hand if necessary. Other information can be added to the table as a comments row with a leading # in the first column. 

Here is the the corresponding .csv file for the figure above.

<Table 1>

When imported in to Fusion 360, will results in a wireframe drawing

![Chesapeak Bay Sharpie wireframe][sharpie]

[sharpie]: https://github.com/bobm123/LinesTable/blob/master/images/sharpie-f360-screenshop.png

