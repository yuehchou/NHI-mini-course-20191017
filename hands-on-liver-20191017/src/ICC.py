import sys, os
import numpy as np
import pandas as pd
from nipype.algorithms.icc import *
from tqdm import tqdm

# #################################################
# Setting
StartFeatures=22
threshold=0.8

try:
    OutputFile=sys.argv[1]
    Files=sys.argv[2:]
except:
    print("Cannot compute ICC")
    print('Should use this commmand "python [python file] [Output file] [Excel file 1] [Excel file 2] ... [Excel file N]"')
    sys.exit()
FeatureFiles=[file for file in Files if file.endswith('.xlsx')]
if len(FeatureFiles) < 2:
    print("[Error] Files should include at least 2 excel files")
    sys.exit()
else:
    print("Calculate ICC by using excel files: ",FeatureFiles)

# #################################################
# Load Features
print("Load all files...")
DF=[]
for file in tqdm(FeatureFiles):
    try:
        DF.append(np.array(pd.read_excel(file)))
        print("Load file ",file)
    except:
        print("[Error] Fail to load file ",file)
        continue
if len(DF) < 2:
    print("Successful loaded files should be at least 2")
    sys.exit()
else:
    print("Done")

# #################################################
# Extract ICC
print("Start calculating ICC...")
icc_features={}
icc_features['Features name']=DF[0][0,StartFeatures:]
icc_features['ICC value']=[]
icc_features['Variance between subjects']=[]
icc_features['Variance of error']=[]
icc_features['Features >= '+str(threshold)]=[]
icc_features['ICC value >= '+str(threshold)]=[]
num_file=len(DF)
for i in tqdm(range(StartFeatures,DF[0].shape[1])):
    Y=[]
    for j in range(1,DF[0].shape[0]):
        temp=[]
        case=DF[0][j,0]
        for k in range(num_file):
            try:
                index=np.where(DF[k][:,0]==case)[0][0]
                temp.append(DF[k][index,i])
            except:
                None
        if num_file==len(temp):
            Y.append(temp)
    Y=np.array(Y)
    Y=Y.astype(float)
    result=ICC_rep_anova(Y)
    icc_features['ICC value'].append(result[0])
    icc_features['Variance between subjects'].append(result[1])
    icc_features['Variance of error'].append(result[2])
print("Done")

# #################################################
# Select features
print("Selecting the ICC value >= ",threshold,"...")
for i in tqdm(range(len(icc_features['ICC value']))):
    if icc_features['ICC value'][i] >= threshold:
        icc_features['Features >= '+str(threshold)].append(icc_features['Features name'][i])
        icc_features['ICC value >= '+str(threshold)].append(icc_features['ICC value'][i])
print("Done")

# #################################################
# Save ICC values
maxlen=0
for item in icc_features:
    if maxlen < len(icc_features[str(item)]):
        maxlen = len(icc_features[str(item)])
for item in icc_features:
    if len(icc_features[str(item)]) < maxlen:
        for i in range(maxlen-len(icc_features[str(item)])):
            icc_features[str(item)].append('')

p=pd.DataFrame(icc_features)
p.to_excel(OutputFile)
print('Save ICC values to ',OutputFile)

