# FIR Core Generation 
## Introduction

This is a customizable FIR Core module with various different parameters and features, a list of which is given below.

## Generator Script
This directory contains the generator script which places the RTL to `rapidsilicon/ip/fir_generator/v1_0/<build-name>/src/` directory.

## Parameters
These are the parameters for FIR core along with their keyword and values: -

| Sr.No. | Parameter | Keyword | Value |
|--------|-----------|---------|-------|
| 1. | Input Width | input_width | 1 - 18 |
| 2. | Coefficients | coefficients | `<numbers separated by commas or whitespaces>` |
| 3. | Coefficients File | coefficients_file | 1 / 0 |
| 4. | File Path | file_path | `<path to .txt file with numbers separated by commas or whitespaces>` |


To generate RTL with above parameters, run the following command:
```
./fir_generator_gen.py --build-name=fir_wrapper --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/fir_generator/v1_0/<build-name>/synth/` directory.
<>