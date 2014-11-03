#gene data analysis thing
#written by g@greyltc.com

import os #for interacting with the file system
import xlrd #for reading excel files
import sys #for exit()
import numpy #for array
import csv #for reading and writing csv files

#number of repeats of the same experiment (defines how many values are averaged)
REPEATS=2

#get a list of files in this directory
files = os.listdir()

supportedFileTypes=['.xls','.xlsx','.csv','.ods']

print ("Looking in %s for files ending in %s"% (os.getcwd(),supportedFileTypes))


noFile = True
for fileName in files:
    for extension in supportedFileTypes:
        if os.path.splitext(fileName)[1] == extension:
            noFile = False
            break
#mess needed here to break out of nested for loop :-(    
    else:
        continue
    break

if noFile:
    print('Could not find a data file to process.')
    sys.exit(-1)

#we'll operate on the first file with a valid extension we find
print ("Operating on file: %s"% fileName)

#if we found an excel file:
if extension is '.xls' or '.xlsx':
    workbook = xlrd.open_workbook(fileName)
    sheets = workbook.sheet_names()
    sheetName = sheets[-1]
    print("Operating on worksheet: %s"% sheetName)
    worksheet = workbook.sheet_by_name(sheetName)
    headerRowTypes = worksheet.row_types(0)
    # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
    refs = []
    whichCol = -1
    for cellType in reversed(headerRowTypes):
        if cellType == 0:
            break
        refs.append({'label':str(worksheet.cell_value(0,whichCol)),'data':worksheet.col_values(whichCol)[1:]})
        whichCol -= 1
        
    nRefs = len(refs)
    if nRefs >= (worksheet.ncols - 1): #check for proper location of blank column splitting ref from gene data
        print ("This tool requires a blank column between gene data and reference data.")
        print ("Reference data columns must also be to the right of gene data columns.")
        sys.exit (-3)
    
    #initialize data container array
    dataRows = worksheet.nrows-1
    dataCols = worksheet.ncols-2-nRefs
    geneData = numpy.empty((dataRows,dataCols))
    
    #read in data from excel sheet row by row
    for row in range(1,worksheet.nrows):
        geneData[row-1,:] = numpy.array(worksheet.row_values(row)[1:-(nRefs+1)])
        
    geneLabels = worksheet.row_values(0)[1:-(nRefs+1)]
    sampleLabels = worksheet.col_values(0)[1:]
    
    #let's make sure all labels are stored as strings
    geneLabels = [str(i) for i in geneLabels]
    sampleLabels = [str(i) for i in sampleLabels]
    

#if we found a .csv file:
if extension is '.csv':
    print(".csv files are not yet supported")
    sys.exit(-1)
    #refs = (list of dicts containing 'label', 'data' )
    #geneData = array of experimentally measured values


#if we found an .ods file:
if extension is '.ods':
    print(".ods files are not yet supported")
    sys.exit(-1)
    #refs = (list of dicts containing 'label', 'data' )
    #geneData = array of experimentally measured values
    print("Operating on worksheet: %s"% sheet)

if geneData.shape[0]%(2*REPEATS):
    print ("ERROR: number of data rows is not evenly divisible by 2*REPEATS")
    sys.exit(-2)

nSamples = geneData.shape[0]//(2*REPEATS)

# initialize output array
folds = numpy.empty((nSamples*len(refs),geneData.shape[1]))

rowLabels = list()
# do the analysis
for iref in range(len(refs)):
    refLabel = refs[iref]['label']
    for isam in range(nSamples):
        sampleOffset = isam*2*REPEATS
        sampleLabel = sampleLabels[sampleOffset+2]
        rowLabels.append(sampleLabel + ' vs ' + refLabel) 
        for igene in range(geneData.shape[1]):
            geneControlMean = numpy.mean(geneData[sampleOffset:sampleOffset+REPEATS,igene])
            geneSamleMean = numpy.mean(geneData[sampleOffset+REPEATS:sampleOffset+2*REPEATS,igene])
            refControlMean = numpy.mean(refs[iref]['data'][sampleOffset:sampleOffset+REPEATS])
            refSampleMean = numpy.mean(refs[iref]['data'][sampleOffset+REPEATS:sampleOffset+2*REPEATS])
            dCT_Sam = geneSamleMean - refSampleMean
            dCT_Cont = geneControlMean - refControlMean
            ddCT = dCT_Sam - dCT_Cont
            fold = 2**-ddCT
            folds[iref*nSamples+isam,igene] = fold


outputList = list()
# output formatting
geneLabels.insert(0,'sample')
for i in range(len(rowLabels)):
    outputList.append(dict(zip(geneLabels,[rowLabels[i]]+list(folds[i,:]))))

outFileName = os.path.splitext(fileName)[0] + '.out.csv'

with open(outFileName, 'w',newline='') as outfile:
    writer = csv.DictWriter(outfile, geneLabels, dialect="excel-tab")
    writer.writeheader()
    writer.writerows(outputList)

print("See tab-delimited output file: %s"% outFileName)
sys.exit(0)
    
#print (folds)
#print (geneLabels)
#print (rowLabels)
