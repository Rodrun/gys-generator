# Generate Air Jordans shoe files using gys-generator
import generator
import globals


def within_range(num: int, minimum: int, maximum: int):
    return True if minimum <= num <= maximum else False


print("Air Jordans GYS shoe file generator.")
loaded = None
try:
    # Get min/max jordan shoe brand
    min_jordans = int(input("Min Jordans brand #(1-23): "))
    max_jordans = int(input("Max Jordans brand #(1-23): "))
    if not within_range(min_jordans, 1, 23) or not within_range(max_jordans, 1, 23) or min_jordans > max_jordans:
        raise None
    # Get path to execution JSON
    path = str(input("Execution JSON file to use and modify: "))
    err, loaded = generator.read_execution_file(path)
except ...:
    print("Error encountered, not dealing with it right now!")

JORDANS_SITE = "https://www.flightclub.com/air-jordans/air-jordan-{}"

# Recursive generation
last_file_number = int(input("Starting file #: "))
for brand_num in range(min_jordans, max_jordans + 1):
    globals.print_info("Preparing to generate next shoe files for Air Jordans {}".format(brand_num))
    # Update execution file to generate new files
    generator.create_execution_file(name=path,
                                    site=JORDANS_SITE.format(brand_num),
                                    start=last_file_number,
                                    dir=str(loaded["dir"]),
                                    exclude_list=loaded["exclude_list"])
    last_file_number, success = generator.execute(path)
    last_file_number += 1 # Reflect next file number to start with for next generation
