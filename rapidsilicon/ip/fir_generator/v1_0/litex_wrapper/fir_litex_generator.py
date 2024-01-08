#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2023 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#

import datetime
import logging
import math
import struct
from migen import *
import re

# Extracting Numbers from the string obtained from the generator
def extract_numbers(input_string, coefficients_file):
    if (not coefficients_file):
        # Use a regular expression to find all numbers (positive or negative)
        # that are separated by commas or whitespaces
        pattern = r'[-+]?\d*\.?\d+'
        numbers = re.findall(pattern, input_string)

        # Convert the found strings to numbers (float or int)
        numbers = [float(num) if '.' in num else int(num) for num in numbers]

        return numbers
    else:
        try:
            with open(input_string, 'r') as file:
                content = file.read()
                # Use regular expression to find all numbers (positive or negative)
                numbers = [float(num) if '.' in num else int(num) for num in re.findall(r'[-+]?\d*\.?\d+', content)]
                return numbers
        except FileNotFoundError:
            return []
        
# Checking if the list of numbers has any negative or fractional number
def check_negative_or_fractional(number):
    negative_fractional = number < 0 # or number % 1 != 0
    return negative_fractional

# Converting fractional or signed number into fixed binary and then back to decimal
def decimal_to_fixed_point(decimal_number, integer=4, fraction=4):
    integer_part = bin(int(abs(decimal_number)))[2:]
    binary_integer = integer_part.zfill(integer)
    fractional_part = bin(int((abs(decimal_number) - int(abs(decimal_number))) * 2**fraction))[2:]
    binary_fraction = fractional_part.zfill(fraction)
    binary_result = str(binary_integer) + str(binary_fraction)
    if (decimal_number < 0):
        inverted_bits = ''.join('1' if bit == '0' else '0' for bit in binary_result)
        binary_result = bin(int(inverted_bits, 2) + 1)[2:]
    return int(binary_result, 2)

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# FIR Generator ---------------------------------------------------------------------------------------
class FIR(Module):
    def __init__(self, input_width, coefficients, coefficients_file):

        if (coefficients != ""):
            coefficients = extract_numbers(coefficients, coefficients_file)

        self.logger = logging.getLogger("FIR")
        self.logger.propagate = True
        self.logger.info(f"=================== PARAMETERS ====================")
        
        # Data Width
        self.logger.info(f"DATA_WIDTH_IN       : {input_width}")
        self.logger.info(f"DATA_WIDTH_OUT       : {38}")
        self.logger.info(f"Coefficients       : {coefficients}")

        self.logger.info(f"===================================================")

        self.data_in = Signal(bits_sign=(input_width, True))
        self.data_out = Signal(bits_sign=(38, True))

        self.z = Array(Signal() for _ in range (len(coefficients)))
        self.delay_b = Array(Signal() for _ in range (len(coefficients)))

        for i in range (len(coefficients)):
            self.delay_b[i] = Signal(bits_sign=(input_width, True), name=f"delay_b_{i}")
            self.z[i] = Signal(bits_sign=(38, True), name=f"z_{i}")

        for i in range(len(coefficients)):
            coefficients[i] = decimal_to_fixed_point(coefficients[i], 8, 8)     # Currently using a notation of Q8.8
            if (i == 0):
                self.specials += Instance("DSP38",

                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP
                    p_DSP_MODE     =  "MULTIPLY_ADD_SUB",
                    p_OUTPUT_REG_EN = "TRUE",
                    p_INPUT_REG_EN = "TRUE",
                    p_COEFF_0       = C(coefficients[i], 20),

                    # Reset
                    i_CLK           = ClockSignal(),
                    i_RESET        = ResetSignal(),

                    # IOs
                    i_A             = C(0, 20),
                    i_B             = self.data_in,
                    o_Z             = self.z[i],  
                    i_FEEDBACK      = C(4, 3),
                    i_UNSIGNED_A    = 0,
                    i_UNSIGNED_B    = 0,
                    o_DLY_B         = self.delay_b[i],
                    i_LOAD_ACC      = 1,
                    i_ACC_FIR       = C(0, 6),
                    i_ROUND         = 0,
                    i_SATURATE      = 0,
                    i_SHIFT_RIGHT   = C(0, 6),
                    i_SUBTRACT      = 0
                )
            elif (i == len(coefficients) - 1):
                self.specials += Instance("DSP38",

                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP
                    p_DSP_MODE     =  "MULTIPLY_ADD_SUB",
                    p_OUTPUT_REG_EN = "FALSE",
                    p_INPUT_REG_EN = "TRUE",
                    p_COEFF_0       = C(coefficients[i], 20),

                    # Reset
                    i_CLK           = ClockSignal(),
                    i_RESET        = ResetSignal(),

                    # IOs
                    i_A             = self.z[i - 1][0:20],
                    i_B             = self.delay_b[i - 1],
                    o_Z             = self.data_out,  
                    i_FEEDBACK      = C(4, 3),
                    i_UNSIGNED_A    = 0,
                    i_UNSIGNED_B    = 0,
                    i_LOAD_ACC      = 1,
                    i_ACC_FIR       = C(0, 6),
                    i_ROUND         = 0,
                    i_SATURATE      = 0,
                    i_SHIFT_RIGHT   = C(0, 6),
                    i_SUBTRACT      = 0
                )
            else:
                self.specials += Instance("DSP38",

                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP
                    p_DSP_MODE     =  "MULTIPLY_ADD_SUB",
                    p_OUTPUT_REG_EN = "TRUE",
                    p_INPUT_REG_EN = "TRUE",
                    p_COEFF_0       = C(coefficients[i], 20),

                    # Reset
                    i_CLK           = ClockSignal(),
                    i_RESET        = ResetSignal(),

                    # IOs
                    i_A             = self.z[i - 1][0:20],
                    i_B             = self.delay_b[i - 1],
                    o_Z             = self.z[i],  
                    i_FEEDBACK      = C(4, 3),
                    i_UNSIGNED_A    = 0,
                    i_UNSIGNED_B    = 0,
                    o_DLY_B         = self.delay_b[i],
                    i_LOAD_ACC      = 1,
                    i_ACC_FIR       = C(0, 6),
                    i_ROUND         = 0,
                    i_SATURATE      = 0,
                    i_SHIFT_RIGHT   = C(0, 6),
                    i_SUBTRACT      = 0
                )
