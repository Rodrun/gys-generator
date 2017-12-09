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
"""
import ast
import re
import requests
import json
from bs4 import BeautifulSoup as BSoup
from splinter import Browser

# Constants
NULL_NAME_STRING = "NoNameFound"
NULL_IMAGE_STRING = "NoImageURLFound"
BASE_SITE = "https://www.flightclub.com"
BASE_SEARCH_SITE = BASE_SITE + "/catalogsearch/result/?q="
PRINT_INFO = True


def print_info(output):
    if PRINT_INFO:
        print("-[---]- INFO: ", output, " -[---]-")


def print_warn(output):
    print("-[!!!]- WARNING: ", output, " -[!!!]-")


class ShoePair:
    """
    Final shoe name and image URL object.
    """
    _excluded = False
    _name = ""
    _image = ""

    def __init__(self, id: str, excludetags: list=[]):
        """
        Find the name and image of a shoe.
        :param id: Shoe ID (found in shoe list).
        :param excludetags: Filter out shoes that contain a string (tag).
        """
        brow = self._search(id)
        self._name = self._get_shoe_name(brow)
        self._image = self._get_shoe_image(brow)
        print_info("Constructed shoe with \nName: {}\nImg URL: {}".format(self._name, self._image))

        brow.quit()

    @property
    def is_excluded(self) -> bool:
        """
        Is it excluded? (Filtered through excludetags, meaning img was not looked for)
        :return: True if excluded, False otherwise.
        """
        return self._excluded

    @property
    def get_name(self) -> str:
        """
        Get the name of the shoe.
        :return: Shoe name string.
        """
        return self._name

    @property
    def get_image(self) -> str:
        """
        Get the image URL.
        :return: Image URL string.
        """
        return self._image

    @staticmethod
    def _search(id: str, headless=False) -> Browser:
        """
        'Search' for the shoe and scrape the first result data (should be accurate due to the fact that it searches by
        id).
        :param id: In a shoe object given by the 'impressions' list, the 'id' value.
        :param webdriver: WebDriver to use. Default is firefox.
        :param headless: Browse headless?
        :return: Browser object with current link at the shoe page.
        """
        # Search
        browser = Browser(headless=headless) # Defaults to firefox
        browser.visit(BASE_SEARCH_SITE + id)
        return browser

    @staticmethod
    def _evaluate_soup_select(beautiful: BSoup, tag: str):
        """
        BeautifulSoup select and evaluate whether the returned length is != 0.

        Example: BeautifulSoup.select('a')
        :param beautiful: BeautifulSoup object to use.
        :param tag: Selector string. E.g. 'a[class='xy']'
        :return: The first element of select(), otherwise None.
        """
        elem = beautiful.select(tag)
        print(elem)
        if len(elem) == 0:
            return None
        return elem[0]

    # NOTE: It just works if you create a new BeautifulSoup object rather than sharing one... Just leave it.

    @staticmethod
    def _get_shoe_image(bs: Browser) -> str:
        """
        Get the image of the shoe.
        :param bes: Browser to use.
        :return: Shoe image URL.
        """
        soup = BSoup(bs.html, "html.parser")
        elem = ShoePair._evaluate_soup_select(soup, "img[class='product-img']")
        ret_str = NULL_IMAGE_STRING if elem is None else elem["src"]
        soup.decompose() # Destroy
        return ret_str

    @staticmethod
    def _get_shoe_name(bs: Browser) -> str:
        """
        Get the shoe name.
        :param bs: Browser to use.
        :return: Name of shoe.
        """
        soup = BSoup(bs.html, "html.parser")
        sel_element = ShoePair._evaluate_soup_select(soup, "p[class='result-title text-ellipsis']")
        ret_str = NULL_NAME_STRING if sel_element is None else sel_element.text
        soup.decompose()
        return ret_str


def create_shoe_pair(idobj, excludetags: list) -> ShoePair:
    """
    Create a ShoePair object, excluding any shoes that contain any exclude tags.
    :param idobj: A shoe object in the impressions list. Must contain "name" value.
    :param excludetags: Shoes to exclude based on if they contain a given string.
    :return: ShoePair if not excluded, None otherwise.
    """
    name = idobj["name"]
    for etag in excludetags:
        if re.search(etag, name, re.IGNORECASE):
            print_info("Excluding '{}', found with tag {}".format(name, etag))
            return None
    return ShoePair(name, excludetags)


def create_all_files(directory: str, shoelist: list, excludetags: list=[], startnum: int = 1) -> None:
    """
    Create all the JSON files necessary with given list.

    The format for file name is  X.json
    - Where X is an integer starting from 1.
    :param directory: Directory to write files to.
    :param shoelist: List of shoe IDs.
    :param excludetags: Exclude tags. See ShoePair.
    :param startnum: Starting file number.
    :return: Nothing.
    """
    current_filenum = startnum - 1 # Starting file number
    for shoe in shoelist:
        shoepair = create_shoe_pair(shoe, excludetags)
        if shoepair is not None:
            current_filenum += 1 # Increment to next file
            create_file(directory, str(current_filenum), shoepair.get_name, shoepair.get_image)
            print_info("Created file {}.json".format(current_filenum))


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
            print_info("Found impressions list: " + part.group(1))
            return json.loads("[" + part.group(1) + "]")
    return [{"name": "NULL"}]


def create_execution_file(name: str, site: str, dir: str, exclude_list: list) -> None:
    """
    Create an execution JSON file. This file is read and used to generate shoe files.
    :param name: Name of generation file.
    :param site: Directory of flightclub.com to use.
    :param dir: Directory to place shoe files.
    :param exclude_list: List of exclude tags.
    :return: Nothing.
    """
    file = open(name, "w")
    json.dump(
        {
            "site": site,
            "dir": dir,
            "exclude_list": exclude_list
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

    site_check = False
    dir_check = False
    excludelist_check = False
    if isinstance(loaded, dict):
        # Check for required values
        if "site" in loaded:
            site_check = True
        if "dir" in loaded:
            dir_check = True
        if "exclude_list" in loaded:
            excludelist_check = True

        # Alert for any missing required values
        if not site_check:
            return "Missing site value", None
        if not dir_check:
            return "Missing dir value", None
        if not excludelist_check:
            return "Missing exclude_list value", None
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
    site = BASE_SITE + "/" + str(input("Site directory: " + BASE_SITE + "/"))
    # Get directory to place shoe files
    dir = str(input("Directory to place shoe files: "))
    if dir == "": # Ensure that we don't dump an empty string to the JSON so it can be read
       dir = "./"
    exclude_list = []
    if str(input("Use exclude tags (in list format e.g. '['a', 'b']? [y/N ]: ")) == "y":
        exclude_list = ast.literal_eval("[" +
                                        str(input("List of exclude tags (separated by comma, requires quotations): "))
                                        + "]")
    create_execution_file(ej_name, site, dir, exclude_list)


def execute() -> None:
    execute_again = False # Call execute() again?

    print("Guess Your Sneaker File Generator.")
    gen_json = False if str(input("Create execution JSON file? [y/N]: ")) != "y" else True
    if gen_json:
        prompt_execution_values()
        execute_again = True
    else:
        loaded = None
        try:
            err, loaded = read_execution_file(str(input("Path to read execution JSON: ")))
            if err != "":
                print("Error with execution JSON: ", err)
                execute_again = True
        except json.JSONDecodeError as je:
            print("JSON Decode Error: ", je)

    if execute_again:
        execute()
    else:

        # Get the given shoe brand site
        print_info("Retrieving site...")
        req = requests.get(loaded["site"])
        req.raise_for_status()
        list_soup = BSoup(req.text, "html.parser")
        print_info("Starting generation...")
        create_all_files(str(loaded["dir"]), get_impressions_list(list_soup), loaded["exclude_list"])


# ############################### Our godly call ############################### #
execute()
