import os
from pathlib import Path
from xml.dom.minidom import parseString


# format xml file and save it to new file with "_new" prefix
def create_pretty_xml(filename):
    with open(filename, 'r', encoding='utf8', errors='ignore') as xmldata:
        xml = parseString(xmldata.read())
        xml_pretty_str = xml.toprettyxml()
        new_xml = os.path.splitext(filename)[0]
        f = open(new_xml + "_new" + ".xml", "w+", encoding='utf8')
        for content in xml_pretty_str:
            f.write(content)
        f.close()
    print(filename + " XML file was formated success. Look at new file with _new suffix")


# iterate through all .xml files in directory
def iterate_dir(directory_in_str):
    path_list = Path(directory_in_str).glob('**/*[!_new].xml')
    for path in path_list:
        path_in_str = str(path)
        create_pretty_xml(path_in_str)
