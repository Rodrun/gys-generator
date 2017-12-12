"""
Guess Your Sneaker (GYS) Shoe file generator.

Uses Flight Club to retrieve shoe names and images (https://www.flightclub.com/).

Will ask if you'd like to create a execution JSON file. This is a file that contains information to use in order to
generate wanted shoe files. In the execution JSON file, the following values are required:

"site" : Web directory of shoe brand site to use. For example, Air Jordan 1 would be "air-jordans/air-jordan-1". So
if you appended this to "flightclub.com/", you'd get to the Air Jordan 1 catalog page.

"dir" : Directory to place generated shoe files in.

"exclude_list" : List of exclude tags strings. Exclude tags are strings to look for in shoe names. If an exclude tag is
found in a shoe name, that shoe will not have a file generated for it. For example, if "Retro" is found in a shoe name,
the shoe will be skipped. Note that this is case insensitive.

"start" : Starting file number.
"""
import globals
import shoepair

import ast
import re
import requests
import json
from bs4 import BeautifulSoup as BSoup


def create_shoe_pair(idobj, excludetags: list) -> shoepair.ShoePair:
    """
    Create a ShoePair object, excluding any shoes that contain any exclude tags.
    :param idobj: A shoe object in the impressions list. Must contain "name" value.
    :param excludetags: Shoes to exclude based on if they contain a given string.
    :return: ShoePair if not excluded, None otherwise.
    """
    name = idobj["name"]
    for etag in excludetags:
        if re.search(etag, name, re.IGNORECASE):
            globals.print_info("Excluding '{}', found with tag {}".format(name, etag))
            return None
    return shoepair.ShoePair(idobj["id"], excludetags)


def create_all_files(directory: str, shoelist: list, excludetags: list=[], startnum: int = 1) -> int:
    """
    Create all the JSON files necessary with given list.

    The format for file name is  X.json
    - Where X is an integer starting from 1.
    :param directory: Directory to write files to.
    :param shoelist: List of shoe IDs.
    :param excludetags: Exclude tags. See ShoePair.
    :param startnum: Starting file number.
    :return: Last file number used.
    """
    current_filenum = startnum - 1 # Starting file number
    for shoe in shoelist:
        shoepair = create_shoe_pair(shoe, excludetags)
        if shoepair is not None:
            current_filenum += 1 # Increment to next file
            create_file(directory, str(current_filenum), shoepair.get_name, shoepair.get_image)
            globals.print_info("Created file {}.json".format(current_filenum))
    return current_filenum


def create_file(dname: str, name: str, shoename: str, imgval: str) -> None:
    """
    Create a new file.
    :param dname: Directory.
    :param name: Name of file.
    :param shoename: Name of the shoe.
    :param imgval: URL of the shoe image.
    :return: Nothing.
    """
    file = open(dname + name + ".json", "w+")
    file.write(json.dumps({"name": shoename, "img": imgval}))
    file.close()


def get_impressions_list(bsoup : BSoup):
    """
    Get the list from 'impressions' (located in the <script>).
    :param bsoup:
    :return: The found list. If not found, will return a list
     with an object {"name": "NULL"}.
    """
    regex = re.compile("\'impressions\': \[(.*?)\]")
    script_tag = bsoup.find("script", text=regex)
    if script_tag: # Found?
        part = regex.search(script_tag.text)
        if part: # Found?
            globals.print_info("Found impressions list: " + part.group(1))
            return json.loads("[" + part.group(1) + "]")
    return [{"name": "NULL"}]


def create_execution_file(name: str, site: str, dir: str, exclude_list: list, start: int) -> None:
    """
    Create an execution JSON file. This file is read and used to generate shoe files.
    :param name: Name of generation file.
    :param site: Directory of flightclub.com to use.
    :param dir: Directory to place shoe files.
    :param exclude_list: List of exclude tags.
    :param start: Starting file number.
    :return: Nothing.
    """
    file = open(name, "w")
    json.dump(
        {
            "site": site,
            "dir": dir,
            "exclude_list": exclude_list,
            "start": start
        },
        file
    )
    file.close()


def read_execution_file(path: str) -> [str, dict]:
    """
    Read an execution JSON file.
    :param path: Path of the file.
    :return: Two values: error string and loaded dict. Error string may be empty ("") if no problems detected such
     as missing required values. Loaded is a dict that was loaded from the JSON, it will be None if an error string
     other than an empty string is given.
    """
    file = open(path)
    loaded = json.loads(file.read())
    print("Loaded JSON: ", loaded)
    file.close()

    if isinstance(loaded, dict):
        # Check for required values
        if "site" not in loaded:
            return "Missing site value", None
        if "dir" not in loaded:
            return "Missing dir value", None
        if "exclude_list" not in loaded:
            return "Missing exclude_list value", None
        if "start" not in loaded:
            return "Missing start value", None
    else: # Is not a dictionary!
        return "Loaded JSON should be a dict ( {} )!", None
    # Success
    return "", loaded


def prompt_execution_values() -> None:
    """
    Prompt execution JSON file values and create the file.
    :return: Nothing.
    """
    # Get path to write exec file to
    ej_name = str(input("Path to write to: "))
    # Get site directory
    site = globals.BASE_SITE + "/" + str(input("Site directory: " + globals.BASE_SITE + "/"))
    # Get directory to place shoe files
    dir = str(input("Directory to place shoe files: "))
    if dir == "": # Ensure that we don't dump an empty string to the JSON so it can be read
       dir = "./"
    exclude_list = []
    if str(input("Use exclude tags (in list format e.g. '['a', 'b']? [y/N ]: ")) == "y":
        exclude_list = ast.literal_eval("[" +
                                        str(input("List of exclude tags (separated by comma, requires quotations): "))
                                        + "]")
    try:
        start = int(input("Starting file number: "))
    except TypeError:
        globals.print_warn("Invalid value, defaulting to 1")
        start = 1
    create_execution_file(ej_name, site, dir, exclude_list, start)


def execute(expath: str = None) -> [int, bool]:
    """
    Read execution JSON file and generate files.
    :param expath: Path to execution JSON file.
    :return: Last file number generated & True on successful execution, False otherwise.
    """
    print("Guess Your Sneaker File Generator.")
    # Ask to create execution file if expath isn't given already
    gen_json = False
    if expath is None:
        gen_json = False if str(input("Create execution JSON file? [y/N]: ")) != "y" else True

    loaded = None
    if gen_json:
        # Create new execution file
        prompt_execution_values()
        execute()
    else:
        # Load execution JSON file
        try:
            if expath is None:
                expath = str(input("Path to execution JSON: "))
            err, loaded = read_execution_file(expath)
            if err != "":
                print("Error with execution JSON: ", err)
                return False
        except json.JSONDecodeError as je:
            print("JSON Decode Error: ", je)
            return False

    # Get the given shoe brand site
    globals.print_info("Retrieving site...")
    req = requests.get(loaded["site"])
    req.raise_for_status()
    list_soup = BSoup(req.text, "html.parser")
    globals.print_info("Starting generation...")
    lf = create_all_files(str(loaded["dir"]), get_impressions_list(list_soup), loaded["exclude_list"], loaded["start"])
    return [lf, True]
