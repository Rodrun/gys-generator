# Constants
NULL_NAME_STRING = "NoNameFound"
NULL_IMAGE_STRING = "NoImageURLFound"
BASE_SITE = "https://www.flightclub.com"
BASE_SEARCH_SITE = BASE_SITE + "/catalogsearch/result/?q="
PRINT_INFO = True


def print_info(output):
    """
    Print info message.
    :param output: Message.
    :return:
    """
    if PRINT_INFO:
        print("-[---]- INFO: ", output, " -[---]-")


def print_warn(output):
    """
    Print warning message.
    :param output: Message.
    :return:
    """
    print("-[!!!]- WARNING: ", output, " -[!!!]-")
