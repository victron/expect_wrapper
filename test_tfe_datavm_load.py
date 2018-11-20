import unittest
import re
from unittest.mock import patch
from datetime import datetime

import os
from string import ascii_lowercase, printable, whitespace, digits

from tfe_datavm_load import parse_file, select_log
import tfe_datavm_load

cwd = os.getcwd()
test_file = os.path.join(cwd, "tests_data", "test_tfe_input.txt")

# https://stackoverflow.com/questions/4481954/python-trying-to-mock-datetime-date-today-but-not-working
class NewDate(datetime):
    @staticmethod
    def now():
        return datetime(2018, 11, 19, 13, 30, 12)



class Testparse_file(unittest.TestCase):
    @patch("tfe_datavm_load.datavm_number", 2) # in reason test file has only 2 output
    def setUp(self):
        script = os.path.realpath(__file__)
        wdir = os.path.dirname(script)
        test_file = os.path.join(wdir, "logs", "test_tfe_input.txt")
        self.result = parse_file(test_file)
        
    def test_1_result_format(self):
        self.assertEqual(len(self.result), 2)
        self.assertIsInstance(self.result, tuple)
        self.assertIsInstance(self.result[0], tuple)
        self.assertIsInstance(self.result[1], tuple)

    def test_2_result_types(self):
        tup0 = self.result[0]
        tup1 = self.result[1]
        self.assertTrue(len(tup0) == len(tup1), msg="number in tups should be equal")
        for i in tup0:
            self.assertTrue(type(i) == str), "all types should be str, i= {}".format(i)
        for i in tup1:
            self.assertTrue(type(i) == int), "all types should be int, i= {}".format(i)
    
    def test_3_result_ranges(self):
        tup0 = self.result[0]
        tup1 = self.result[1]

        # ERROR:
        if len(tup0) == 1:
            if tup0[0].startswith("ERROR:"):
                print("section =========> ERROR; tup0= {}".format(tup0))
                return

        for word in tup0:
            self.assertEqual(len(word.split("-")), 3)
            self.assertTrue(word.startswith("vmme"))
            self.assertTrue(word.startswith("vmme00"))
            self.assertIn(word.split("-")[0], ["vmme001", "vmme002"])

            self.assertEqual(word.split("-")[1], "data")

            sword2 = word.split("-")[2] 
            self.assertEqual(len(sword2.split("/")), 2)
            self.assertIn(sword2.split("/")[0], digits)
            self.assertIn(sword2.split("/")[0], [str(i) for i in range(5)])

            self.assertEqual(len(sword2.split("/")[1]), 4, msg="word= {}".format(word))
            for char in sword2.split("/")[1]:
                self.assertIn(char, digits)

            for char in word:
                self.assertNotIn(char, whitespace)

        for i in tup1:
            self.assertGreaterEqual(i, 0)
            self.assertLessEqual(i, 100)


class Test_select_log(unittest.TestCase):
    @patch("tfe_datavm_load.os.path")
    @patch("tfe_datavm_load.os.listdir")
    def setUp(self, mock_listdir, mock_path):
        # mocking crrent time
        tfe_datavm_load.datetime = NewDate  
        # test_list of files
        mock_listdir.return_value = ["aaa.aa","ww.log", "ss.log", "vmdata_2018-11-19_13-25.log", 
        "vmdata_2018-11-19_13-24.log", "vmdata_2018-11-19_12-26.log", "vmdata_2018-11-19_14-20.log",
        "vmdata_2018-11-18_14-26.log", "vmdata_2018-11-20_14-26.log", "vmdata_2017-11-19_14-25.log",
        "vmdata__2018-11-19_13-25.log", "vmdata_2018-_11-19_13-25.log", "vmdata_2018-11-19-13-25.log",] 
        mock_path.isfile.return_value = True
        self.result = select_log()

    def test_1_format(self):
        self.assertIsInstance(self.result, str)
        self.assertTrue(self.result.endswith(".log"))
        self.assertTrue(self.result.startswith("vmdata_"))
        patern = "vmdata_[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}.log"
        self.assertTrue(bool(re.match(patern, self.result)))
    
    def test_2_times(self):
        self.assertEqual(self.result, "vmdata_2018-11-19_13-25.log")

    @patch("tfe_datavm_load.os.path")
    @patch("tfe_datavm_load.os.listdir")
    def test_3_empty_dir(self, mock_listdir, mock_path):
        mock_listdir.return_value = []
        mock_path.isfile.return_value = True
        self.assertIsNone(select_log())
        mock_path.isfile.return_value = False
        self.assertIsNone(select_log())

if __name__ == "__main__":
    # unittest.main()

    # Run only the tests in the specified classes

    test_classes_to_run = [Testparse_file, Test_select_log]

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(big_suite)


