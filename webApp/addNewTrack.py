#!/usr/bin/env python
# This program adds a new track to a csv file
# for the sonos controller wallbox project. 
# MIT License ( https://opensource.org/licenses/MIT ), Copyright Chris Schaab 2016


import sys
import csv
import cgi
import cgitb
import soco
from tempfile import NamedTemporaryFile
import shutil


cgitb.enable()

#set up some "globals" for this file
form = cgi.FieldStorage()
letter = form.getvalue('letter')
number = form.getvalue('number')
title = form.getvalue('title')
artist = form.getvalue('artist')
explicit = "no"
try:
    # get sonos info, only works if all are on
    for device in soco.discover():
        if device.is_coordinator:
            sonosMain = device
            break
except:
    pass
currentlyPlaying = sonosMain.get_current_track_info()
# Copy the old csv while inserting the change
filename = "/home/cschaab/projects/pytho4pi/lib/database/JukeBoxSongs.csv"
tempfile = NamedTemporaryFile(delete=False)

# you can change temp to test and get a second file, useful for debugging. 

#testfilename = "/home/cschaab/projects/pytho4pi/lib/database/testdatabase.csv"

rownum = 0

#print out html page

print("Content-type: text/html\n")
print("<html>\n")
print("\n")
print("<head>")
#color every other line with gray, makes things easier to read
print( """ <style>
      tr:nth-of-type(odd) {
      background-color:#ccc;
    }
</style>""")
print("</head>")
print("<body>")
print(" <h1> <center> configurating!! </h1> </center>")
print("<hr>")
print("track number and letter  =", number, letter)

hit = False
with open(filename, 'rb') as csvFile, tempfile:
    reader = csv.reader(csvFile, delimiter=',', quotechar='"')
    writer = csv.writer(tempfile, delimiter=',', quotechar='"')
    reader = csv.DictReader(csvFile)

    # write header row
    writer.writerow(['Key-letter', 'Key-number', 'Track Name',
                     'Artist', 'URL', 'Note', 'Explict', 'Loaded', 'meta', '', ''])

#Yes, we scan each row until we find the one we want, what? Every CS major just flipped their lid? 
# This is a 200 row csv file, I can read and write 10,000 of them in the time it took to write this
# comment. 

    for row in reader:
        if(row['Key-letter'] == letter):
            if(row['Key-number'] == number):
                writer.writerow([letter, number, title, artist, currentlyPlaying[
                                'uri'], "WebAdd", explicit, "yes", ""])
                print row
                hit = True
            else:
                writer.writerow([row['Key-letter'], row['Key-number'], row['Track Name'], row[
                                'Artist'], row['URL'], row['Note'], row['Explict'], row['Loaded'], row['meta']])
        else:
            writer.writerow([row['Key-letter'], row['Key-number'], row['Track Name'], row[
                            'Artist'], row['URL'], row['Note'], row['Explict'], row['Loaded'], row['meta']])

#copy temp file to original file

shutil.move(tempfile.name, filename)


#Bad input, could be fixed with input checking. 
if hit == False:
    print("No matching row and letter, be sure to use capital letter!")


print("<HR>")

#Now we print the csv file with the changes so you can confirm it's ok

print("New Table")
reader = csv.reader(
    open("/home/cschaab/projects/pytho4pi/lib/database/JukeBoxSongs.csv"))
print('<table border="1">')

for row in reader:  # Read a single row from the CSV file

    # write header row. assumes first row in csv contains header
    if rownum == 0:
        print('<tr>') 
        for column in row:
            print('<th>' + column + '</th>')
        print('</tr>')

    else:
        print('<tr>')
        for column in row:
            print('<td>' + column + '</td>')
        print('</tr>')

    rownum += 1

print('</table>')
print("</body>")
print("</html>")

#Everything is ok! Exit! If it's not ok, no one cares. 

exit(0)
