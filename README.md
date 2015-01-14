This is a tool written in python to aid in the analysis of some sort of mouse gene data file that I don't fully understand.
To use it, place an input data file in the same directory as the geneCruncher.py script and run the script with python3. Along with python version 3, this tool requires the python 3 numpy and xlrd modules to be installed.
The data files it operates on are subject to several requirements:
* The data file must be an excel file (.xlsx or .xls)
* The data file must contain one blank column separating the gene data and the reference data column(s).
* In addition to this blank column, the data file must contain only the following:
  * A header row describing gene and reference names
  * A header column describing sample names.
  * A block of numerical experimental data values directly under these headings
* The reference data column(s) must be to the right of the gene data column(s).
* The number of data rows must be evenly divisible by REPEATS*2.
  * REPEATS is the number of times each experiment was repeated. This variable can be found at the top of the analysis script and is intended to be edited by the user.

Upon successful analysis, an output file will be generated in the same directory as the input file with the same name as the input file with an extension of .out.csv. This is a tab-separated data file with column headers describing gene names and row headers describing a particular combination of reference and sample. Intersections of the rows and columns contain a number representing the fold for that gene/reference/sample combination.
