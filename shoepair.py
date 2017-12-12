import globals
from bs4 import BeautifulSoup as BSoup
from splinter import Browser


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
        globals.print_info("Constructed shoe with \nName: {}\nImg URL: {}".format(self._name, self._image))

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
        globals.print_info("Searching for {}".format(id))
        browser = Browser(headless=headless) # Defaults to firefox
        browser.visit(globals.BASE_SEARCH_SITE + id)
        bes = BSoup(browser.html, "html.parser")
        a_elements = bes.find_all("a")
        for aelem in a_elements:
            if "-" + id in aelem["href"]:
                nbrowser = Browser(headless=headless)
                nbrowser.visit(aelem["href"])
                browser.quit()
                return nbrowser
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
        elem = ShoePair._evaluate_soup_select(soup,
                                              "div[class='product-image product-img-box'] > img[class='product-img']")
        ret_str = globals.NULL_IMAGE_STRING if elem is None else elem["src"]
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
        sel_element = ShoePair._evaluate_soup_select(soup, "div[class='mb-padding product-name hidden-phone'] > h1")
        ret_str = globals.NULL_NAME_STRING if sel_element is None else sel_element.text
        soup.decompose()
        return ret_str
