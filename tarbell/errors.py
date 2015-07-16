# -*- coding: utf-8 -*-

"""
tarbell.errors
~~~~~~~~~~~~~~~~~

This modules provides custom errors for Tarbell.
"""

import string


class MergedCellError(Exception):
    def __init__(self, sheetname, ranges):
        """
        Translate merged cells to human readable ranges.
        """

        self.sheetname = sheetname
        self.ranges = ranges
        self.bad_ranges = []

        letters = string.lowercase
        for range in self.ranges:
            row1, row2, col1, col2 = range
            col1 = letters[col1]
            col2 = letters[col2 - 1]
            row1 = row1 + 1
            self.bad_ranges.append(
                "{0}{1}:{2}{3}".format(col1, row1, col2, row2))

    def __str__(self):
        return ("Merged cells found in worksheet '{0}' in ranges {1}"
                .format(self.sheetname, ", ".join(self.bad_ranges)))
