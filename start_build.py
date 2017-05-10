import time
import os
from xml.dom import minidom

xmldoc = minidom.parse("args.xml")
itemlist = xmldoc.getElementsByTagName("item")
executeTime = itemlist[8].attributes["time"].value
executeScript = itemlist[9].attributes["script"].value

executeTime = executeTime.replace(":", "")
print executeScript
print executeTime
if 235959 > int(executeTime) > 0:
    while True:
        if time.strftime("%H%M%S") == executeTime:
            os.system('python ' + executeScript)
            break
else:
    print "The time that you entered in the xml file is invalid"
