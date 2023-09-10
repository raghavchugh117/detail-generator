import logging


logging.basicConfig(format='%(process)d - %(processName)s - %(thread)d - %(asctime)s - %(levelname)s - %(message)s',
                    filemode='a+',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='detail_generator.log',
                    level=logging.INFO)

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import random
import csv
import datetime
import argparse
import os


class GenerateRandomNames:
    def __init__(self):
        """
            Initializes all the variables.
        """
        self.driver = None
        self.chrome_options = None
        self.gender_dropdown = None
        self.name_set_dropdown = None
        self.country_dropdown = None
        self.url = "https://www.fakenamegenerator.com/"
        self.__details_list = None
        self.__info_dict = {
            "NAME": None,
            "ADDRESS": None,
            "PHONE": None,
            "COUNTRY_CODE": None,
            "BIRTHDAY": None,
            "AGE": None,
            "EMAIL_ADDRESS": None,
            "USERNAME": None,
            "PASSWORD": None,
            "WEBSITE": None,
            "COMPANY": None,
            "OCCUPATION": None,
            "HEIGHT": None,
            "WEIGHT": None,
            "BLOOD_TYPE": None,
            "FAVORITE_COLOR": None,
            "VEHICLE": None
        }
        self.__keys_list = None

    def setup(self):
        """
        Setups the environment.
        """
        self.chrome_options = Options()
        logging.info("Setting Chrome to Headless mode.")
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        logging.info("Opening Browser.")
        self.driver = webdriver.Chrome(r'chromedriver.exe', options=self.chrome_options)
        self.driver.maximize_window()
        logging.info("Going to URL.")
        self.driver.get(self.url)
        self.refresh_dropdown_elements()
        self.__details_list = []
        self.__keys_list = list(self.__info_dict.keys())

    def refresh_dropdown_elements(self):
        """
        Refreshes dropdown variables to remove stale elements.
        """
        self.gender_dropdown = Select(self.driver.find_element_by_id('gen'))
        self.name_set_dropdown = Select(self.driver.find_element_by_id('n'))
        self.country_dropdown = Select(self.driver.find_element_by_id('c'))

    def run(self, number_of_names):
        """
        Runs the whole process.
            :param number_of_names: Number of data to fetch
        """
        name_set_length = len(self.name_set_dropdown.options) - 1
        country_length = len(self.country_dropdown.options) - 1
        count = 0
        while len(self.__details_list) < number_of_names:
            self.gender_dropdown.select_by_index(0)
            self.name_set_dropdown.select_by_index(random.randint(0, name_set_length))
            self.country_dropdown.select_by_index(random.randint(0, country_length))
            generate_button = self.driver.find_element_by_id("genbtn")
            generate_button.click()
            self.driver.implicitly_wait(5)

            name_class = self.driver.find_element_by_css_selector('div.address')
            name = name_class.find_elements_by_tag_name('h3')[0].text
            self.__info_dict["NAME"] = name
            address = name_class.find_element_by_css_selector('div.adr').text
            self.__info_dict["ADDRESS"] = address
            info_list = self.driver.find_elements_by_css_selector('dl.dl-horizontal')
            for info in info_list:
                key = info.find_element_by_tag_name('dt').text.upper().replace(" ", "_")
                if key in self.__keys_list:
                    info_text = info.find_element_by_tag_name('dd').text
                    self.__info_dict[key] = info_text.split('\n')[0]

            self.__details_list.append(self.__info_dict.copy())
            self.refresh_dropdown_elements()
            count += 1
            logging.info("Successfully generated detail number:{}".format(str(count)))
            if count % 15 == 0:
                print("{} details fetched.".format(str(count)))

    @property
    def details_list(self):
        """
            Returns details list.
        """
        return self.__details_list

    @property
    def keys_list(self):
        """
            Returns list of keys.
        """
        return self.__keys_list

    def teardown(self):
        """
            Teardown function.
        """
        self.driver.close()


def save_to_csv(data, keys):
    """
        Save data to CSV.
    """
    with open(filename, mode=mode, encoding='utf8', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        if header:
            dict_writer.writeheader()
        dict_writer.writerows(data)
    logging.info("Data written successfully to file.")


if __name__ == "__main__":

    logging.info("------------------------------------------------------------------------------------------")
    logging.info("Starting execution of file details_generator.py")

    my_parser = argparse.ArgumentParser(description='Get random names with details and save in CSV!',
                                        epilog='Enjoy the program! :)',
                                        formatter_class=argparse.RawTextHelpFormatter)

    # Add the arguments
    my_parser.add_argument('-nr',
                           '--numrecords',
                           type=int,
                           help='number of records to fetch',
                           required=False)

    my_parser.add_argument('-f',
                           '--filename',
                           type=str,
                           help='the path to store csv file',
                           required=False)

    my_parser.add_argument('-a',
                           dest='mode',
                           action='store_true',
                           help="Append to file, Overwrite is default")

    # Execute the parse_args() method
    args = my_parser.parse_args()

    try:
        if args.filename is None or len(args.filename) == 0:
            filename = "details.csv"
        else:
            filename = args.filename

        if args.numrecords is None:
            num_records = 100
        else:
            num_records = args.numrecords

        if not args.mode:
            mode = 'w+'
        else:
            mode = 'a+'
        header = True
        filename = os.path.normpath(filename)
        if os.path.exists(filename) and mode == 'a+':
            header = False

        logging.info("Parameters to fetch data:")
        logging.info("Number of Records -> numrecords: {}".format(str(num_records)))

        # print(filename, num_records, mode)

        logging.info("Create object and defining variables.")
        generate_names = GenerateRandomNames()
        logging.info("---------------------------------")
        logging.info("Running setup function.")
        logging.info("---------------------------------")
        generate_names.setup()

        start_time = datetime.datetime.now()
        logging.info("---------------------------------")
        logging.info("Fetching data.")
        logging.info("---------------------------------")
        generate_names.run(number_of_names=num_records)
        end_time = datetime.datetime.now()
        logging.info("---------------------------------")
        logging.info("Running teardown function.")
        logging.info("---------------------------------")
        generate_names.teardown()

        logging.info("---------------------------------")
        logging.info("Starting to write data to file.")
        logging.info("---------------------------------")
        logging.info("Parameters to save data to file:")
        logging.info("File Name -> filename: {}".format(filename))
        logging.info("Mode to write data -> mode: {}".format(mode))
        logging.info("Write Headers -> header: {}".format(header))

        save_to_csv(data=generate_names.details_list,
                    keys=generate_names.keys_list)
        # print(generate_names.details_list)
        logging.info("---------------------------------")
        logging.info("!!!Operation Completed Successfully!!!")
        logging.info("Time taken to complete operation: {}".format(str(end_time - start_time)))

    except Exception as exp:
        logging.error(exp)
        raise Exception(exp)
