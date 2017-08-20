#!/usr/bin/env python
# This is the first of two files that gets some info from a user
#and updates a csv file. Released under the MIT License, copyright 2016 Chris Schaab. 


import sys
import csv
import cgitb
import soco

cgitb.enable()

#Change to your csv file, make sure that permissions of the running webserver are able to edit it! 
reader = csv.reader(
    open("/home/cschaab/projects/pytho4pi/lib/database/JukeBoxSongs.csv"))


rownum = 0

try:
    # get sonos info, only works if all are on
    for device in soco.discover():
        if device.is_coordinator:
            sonosMain = device
            break
except:
    pass

print("Content-type: text/html\n")
print("<html>\n")
print("\n")
print("<head>")
#Color ever other row gray
print( """ <style>
      tr:nth-of-type(odd) {
      background-color:#ccc;
    }
</style>""")
print("</head>")
print("<body>")
print(" <h1> <center> Welcome to config-o-matic! </h1> </center>")
print("<hr>")
print("sonosMain = ", sonosMain)
print("<br> Currently playing: ")
print sonosMain.get_current_track_info()
print("<HR>")
#Iput info form multiline print
print("If you want to set current track to a letter and number pair, enter them below. Just the letter and number in each box")
print("""<form action="/cgi/addNewTrack.py" method="POST">
    Letter to set: <input type="text" name="letter" size="1" maxlength="1">
    <br/>
    Number to set: <input type="text" name="number" size="1" maxlength="1">
    <br/>
    Title to set: <input type="text" name="title">
    <br/>
    Artist to set (defualt is web stream) : <input type="text" name="artist" value="Web Stream">
    <br/>
    <input type="submit">
</form>
""")

print('<table border="1">')

#Print out the current csv file. 
for row in reader:  

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

exit(0)
