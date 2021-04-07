#!/usr/bin/python3
import itertools as it
import string
import os
import csv
import time
import sys

class dataGen():
    provinces = (
    ['Newfoundland and Labrador', 'NL', ['A']],
    ['Prince Edward Island', 'PE', ['C']],
    ['Nova Scotia', 'NS', ['B']],
    ['New Brunswick', 'NB', ['E']],
    ['Quebec', 'QC', ['G', 'H', 'J']],
    ['Ontario', 'ON', ['K', 'L', 'M', 'N', 'P']],
    ['Manitoba', 'MB', ['R']],
    ['Saskatchewan', 'SK', ['S']],
    ['Alberta', 'AB', ['T']],
    ['British Columbia', 'BC', ['V']],
    ['Yukon', 'YT', 'X'],
    ['Northwest Territories', 'NT', 'X'],
    ['Nunavut', 'NU', 'Y'],)

    def delay_print(self, *argv):
        output = " ".join(map(str, argv))
        for c in output :
            sys.stdout.write(c)
            sys.stdout.flush()

    def __init__(self):
        self.delay_print('Data generation object created.','\n')

    def computeCodes(self):
        """
        Returns an iterable object of all theoretical postal codes in Canada,
        along with a file name titled postalCodes.txt".
        NOTE* Some codes computed will not be in use yet, so they may return null
        or invalid values when queried.
        return iterable, string
        """
        POST_START = ("".join(start) for start in it.product("ABCEGHJKLMNPRSTVXY", string.digits, string.ascii_uppercase))
        POST_END = ("".join(ending) for ending in it.product(string.digits, string.ascii_uppercase, string.digits))
        return ("".join(code) for code in it.product(POST_START, POST_END)), "postalCodes.txt"

    def computeNumbers(self):
        """
        Returns an iterable object of all of the theoretical phone number objects in Canada,
        along with a file name titled "phoneNumbers.txt"
        NOTE* Some numbers are likely not in use.
        return iterable, string
        """
        AREA_CODE = (
        '368', '403', '587', '780', '825', '236', '250', '604', '672', '778',
        '204', '431', '506', '428', '709', '879', '867', '782', '902', '867',
        '226', '249', '289', '343', '365', '416', '437', '519', '548', '613',
        '647', '705', '807', '905', '782', '902', '354', '367', '418', '438',
        '450', '514', '579', '581', '819', '873', '306', '474', '639', '867',
        '600', '622', '800', '833', '844', '855', '866', '877', '888',)
        PREFIX = ("".join(num) for num in it.product(string.digits, string.digits, string.digits))
        SUBSCRIBER = ("".join(num) for num in it.product(string.digits, string.digits, string.digits, string.digits))
        return ("-".join(phoneNum) for phoneNum in it.product(AREA_CODE, PREFIX, SUBSCRIBER)), "phoneNumbers.txt"

    def toFile(self, iter, fileName, writeType):
        """
        Takes an iterable object and a filename, and writed elements from
        iterable to file.
        return None
        """
        self.delay_print('Starting to write to file:', fileName,'\n')
        file = open(fileName, mode=writeType)
        for thing in iter:
            file.write(str(thing) + '\n')
        self.delay_print('Completed writing to file:', fileName,'\n')
        file.close()

    def toCSV(self, iter, fileName):
        with open(fileName, mode='a') as csvFile:
            writer = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for entry in iter:
                self.delay_print(entry, '\n')
                writer.writerow(entry)

    def progressLoader(self, totalFileName, completedFileName, outputFileName):
        """
        At the moment this program compares two text files, and finds the lines that
        are different from total/reference file and the file that has currently completed
        output. This is done as a measure to allow programs to pickup progress during a
        computationally heavy and time consuming task and pickup where they left off.
        Additionally, this function is setup as a generator as to minimize the memory usage
        reading from particularly long documents.
        *NOTE, csv support needs to be tested/developed still.
        return iterable
        """
        if os.path.exists(totalFileName):
            self.delay_print('Total/Reference File Detected.', '\n')
        elif os.path.exists(totalFileName) == False:
            raise RuntimeError('Total/Reference File Missing.')
        if os.path.exists(completedFileName):
            self.delay_print('Progress File Detected.', '\n')
            self.delay_print('Removing Duplicates.', '\n')
            os.system(' '.join(['sort', '-u', '-o', completedFileName, completedFileName]))
        elif os.path.exists(completedFileName) == False:
            self.delay_print('Progress File Missing.','\n')
            self.delay_print('Compensating. Creating file:', completedFileName,'\n')
            os.system(" ".join(['>', completedFileName]))
            self.delay_print('File created:', completedFileName, '\n')
        self.delay_print('Starting comparison between:', totalFileName, completedFileName,'\n')
        self.delay_print('Standby.', '\n')
        os.system(' '.join(["comm", completedFileName, totalFileName, '-3','|','tr', '-d', r'"\t"', '>', outputFileName]))
        self.delay_print('Comparison completed:', totalFileName, completedFileName, '\n')
        if os.path.exists(outputFileName) == False:
            raise RuntimeError('Something went wrong with', outputFileName, 'creation!')
        #this should hopefully keep memory cost down.
        self.delay_print( outputFileName, 'ready for parsing.', '\n')
        with open(outputFileName) as outputfile:
            for line in outputfile:
                if len(line) > 2:
                    yield line.strip()






        #
