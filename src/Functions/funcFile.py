import numpy as np
from ABIFReader import ABIFReader

def readShapeData(fName):
    dyes=['6-FAM','VIC','NED','ROX']
    Satd=np.array([])
    extFile=fName.split('.')[-1]
    if extFile=="txt":
        data=loadTxtFile(fName)
    else:
        data=readABI(fName)
        reader=ABIFReader(fName)
        if extFile=="fsa":
            try:
                Satd=np.array(reader.getData('Satd',1))
            except:
                Satd=np.array([])
            for i in range(4):
                dyes[i]=str(reader.getData('DyeN',i+1)).replace(' ','')    
    return data,Satd,dyes

def readBaseFile(fName,RNAflag=True):
    """ Read different type of Sequence file. Fasta, Seq, Genbank and plain text
    """
    extension=fName.split('.')[-1]
    if extension=='seq':
        sequence=readSeqSeq(fName)
    elif extension=='txt':
        sequence=readSeqText(fName)
    elif extension=='fasta':
        sequence=readSeqFasta(fName)
    elif extension=='gbk':
        sequence=readSeqGenbank(fName)
    else:
        sequence=''
        print 'This file format can not be read'
        
    validBases='UCAG' if RNAflag else 'TCAG'
    baseSeq=''
    for base in sequence.upper():
        if (base in validBases):
            baseSeq+=base
        elif RNAflag and base=='T':
            baseSeq+='U'
    return baseSeq

def readSeqGenbank(fName):
    inFile=open(fName)
    data=inFile.read()
    # Find the ORIGIN
    orgn=data.find('ORIGIN')
    # Find the first row after that
    start=data.find('1',orgn)
    # Find ending slashes
    end=data.find('//',orgn)
    # split substring into lines
    a=data[start:end].split('\n')
    sequence=''
    for i in a:
        spl=i.split()
        sequence+=''.join(spl[1:])
    inFile.close()
    return sequence
        
def readSeqText(fName):
    sequence=''
    #while 1:
    with open(fName, 'r') as f:
        for line in f.readlines(): 
            if line.endswith('\n'):
                sequence +=line[:-2]
            else:
                sequence +=line
    sequence=''.join(sequence.split())
    return sequence
   
def readSeqFasta(filename):
    """Read fasta data from the given file.  Returns a two-element list,
       the first of which is the fasta information (the first line), the
       rest of which is the sequence, represented as a string."""
    inFile = open(filename)
    info = inFile.readline()
    data = inFile.read()
    inFile.close()
    info = info.replace('\n', '')
    sequence = data.replace('\n', '')
    inFile.close()
    return sequence

def readSeqSeq(fileName):
    inFile=open(fileName)
    data=inFile.readlines()
    info=data[1].split()[0]
    sequence=''
    for i in range(2,len(data)):
        #data[i]=data[i].split()#replace('\n','')
        sequence+=''.join(data[i].split())
    sequence=sequence[:-1]
    inFile.close()
    return sequence

#import os
#dir=os.getcwd()
#fName=dir+"/Data/HIV-976.seq"
##fName=dir+"/Data/NC_006046.gbk"
##fName=dir+"/Data/NC_006046.fasta"
#
#sequence=readBaseFile(fName)
#print sequence

def readABI(fname):
    reader = ABIFReader(fname)
    col0 = reader.getData('DATA',1)
    col1 = reader.getData('DATA',2)
    col2 = reader.getData('DATA',3)
    col3 = reader.getData('DATA',4)
    
    data=np.zeros([len(col0),4],dtype='f4')
    data[:,0]=np.array(col0)
    data[:,1]=np.array(col1)
    data[:,2]=np.array(col2)
    data[:,3]=np.array(col3)
    return data

def readDataTxt(fName):
    fl=open(fName, "r")
    a,data=[],[]
    for line in fl.readlines():
        try:
            a= [float (x) for x in line.split()]
            data.append(a)
        except:
            pass
    dataA=np.array(data)
    fl.close()
    return dataA
                   
 
def loadTxtFile(fName):
    try:
        dataA=np.loadtxt(fName,delimiter='\t')
    except:
        dataA=readDataTxt(fName)
    try:
        NCol=dataA.shape[1]
    except:
        NCol=1
        dataA=dataA.reshape(len(dataA),1)
    if NCol<4:
        data=np.zeros([len(dataA),4])
        for i in np.arange(NCol):
            data[:,i]=dataA[:,i]
        return data
    else:
        return dataA

def saveCurLaneAsTxt(fileName,dDrawData,dChKeys):
    from funcGeneral import maxLenF
    fileName=str(fileName)  
    if fileName.split('.')[-1]!="txt":
        fileName=fileName+'.txt'
    maxLen=maxLenF(dDrawData)
    A=np.zeros([maxLen,len(dChKeys)])
    k=0
    for key in dChKeys:
        A[:len(dDrawData[key]),k]=np.array(dDrawData[key])
        k+=1   
    
    np.savetxt(fileName, A, fmt='%.5f',delimiter = '\t') 