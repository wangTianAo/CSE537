import random
import pickle as pkl
import argparse
import csv
import numpy as np
from math import log
from scipy.stats import chisquare
import pandas as pd
import sys
sys.setrecursionlimit(100000)
totalNumber = 0
class TreeNode():
    def __init__(self, data='T',children=[-1]*5):
        self.nodes = list(children)
        self.data = data

    def save_tree(self,filename):
        obj = open(filename,'w')
        pkl.dump(self,obj)

def load_data(filename,isFeature):
    if isFeature:
        return pd.read_csv(filename, header = None, delim_whitespace = True)
    else:
        return pd.read_csv(filename, header = None)

def getEntropy(trainfeature,label,attr):
    length = len(label)
    attr_total = pd.DataFrame()
    attr_total['attr'] = trainfeature[attr]
    attr_total['output'] = label
    totalEntropy = 0.0
    uniqueAttrTotal = attr_total['attr'].unique()
    for value in uniqueAttrTotal:
        tempAttrTotal = attr_total[attr_total['attr']==value]
        total = tempAttrTotal.shape[0]
        pos = tempAttrTotal['output'].sum()
        neg = total-pos
        posRate = float(pos)/float(total)
        negRate = float(neg)/float(total)
        entropy = 0.0
        if posRate!=0:
            entropy-=posRate*log(posRate,2)
        if negRate!=0:
            entropy-=negRate*log(negRate,2)
        prob = float(total)/attr_total.shape[0]
        totalEntropy+=(prob*entropy)
    return totalEntropy

def LeafNode(label):
    pos = (label==1).sum()
    neg = (label==0).sum()
    if pos>neg:
        return TreeNode('T')
    else:
        return TreeNode('F')

def getMaxPossibleAttr(data,attr):
    trainfeature = data.iloc[:,0:274]
    label = data['output']
    bestAttr = -1
    minGain = 99999
    for singleAttr in attr:
    	gain = getEntropy(trainfeature, label, singleAttr)
    	if (gain < minGain):
            minGain = gain
            bestAttr = singleAttr
    return bestAttr

def ID3_tree(data, pval, attr):
    global totalNumber
    feature = data.iloc[:,0:274]
    label = data.iloc[:,274]
    pos = (label==1).sum()
    neg = (label==0).sum()
    total = pos+neg
    if pos == total:
        totalNumber+=1
        return TreeNode('T')
    if neg == total:
        totalNumber+=1
        return TreeNode('F')
    if(len(attr) == 0):
        totalNumber+=1
        return LeafNode(label)
    node = None
    maxIGAttr = getMaxPossibleAttr(data, attr)
    # print maxIGAttr
    attr.remove(maxIGAttr)

    if split(feature,label,pval,maxIGAttr):
        node = TreeNode(maxIGAttr + 1)
        totalNumber+=1
        for i in range(1,6):
            dataSub = data.loc[data[maxIGAttr] == i]
            if dataSub.empty:
                totalNumber+=1
                node.nodes[i - 1] = LeafNode(label)
            else:
                is_node = ID3_tree(dataSub, pval, attr)
                if is_node:
                    node.nodes[i - 1] = is_node
                else:
                    totalNumber+=1
                    node.nodes[i - 1] = LeafNode(label)
    else:
        return None
    return node

def split(feature,label,pval,attr):
    expected_freq = []
    observed_freq = []
    attr_total = pd.DataFrame()
    attr_total['attr'] = feature[attr]
    attr_total['output'] = label
    pos = (label==1).sum()
    neg = (label==0).sum()
    total = pos+neg
    prob_pos = float(pos)/total
    prob_neg = float(neg)/total
    uniqueAttrTotal = attr_total['attr'].unique()
    for value in uniqueAttrTotal:
    	tempAttr = attr_total[attr_total['attr']==value]
    	totalTemp = tempAttr.shape[0]
    	obspos = tempAttr['output'].sum()
        obsneg = total-obspos
        expectedpos = prob_pos*totalTemp
        expectedneg = prob_neg*totalTemp
        observed_freq += [obspos,obsneg]
        expected_freq += [expectedpos,expectedneg]
    chiSquare, p = chisquare(observed_freq, expected_freq)
    if p<pval:
    	return True
    else:
    	return False

def testSingle(root, example):
    if root.data == 'F':
        return 0
    if root.data == 'T':
        return 1
    next = int(example[int(root.data)-1])-1
    return testSingle(root.nodes[next], example)

def predict(root,feature):
    print("start test")
    predict = []
    for i in range(0,len(feature)): 
        val = testSingle(root, feature[i:i+1])
        predict.append([val])

    with open(outputFile, "wb") as f:
        writer = csv.writer(f)
        writer.writerows(predict)

    print ("Num Nodes = " + str(totalNumber))
    print("Output files generated")

parser = argparse.ArgumentParser()
parser.add_argument('-p', required=True)
parser.add_argument('-f1', required=True)
parser.add_argument('-f2', required=True)
parser.add_argument('-o', required=True)
parser.add_argument('-t', required=True)

args = vars(parser.parse_args())
pval = float(args['p'])
trainFeatFile = args['f1']
trainLabFile = args['f1'].split('.')[0]+ '_label.csv'
testFeatFile = args['f2']
outputFile = args['o']
outputTree = args['t']

features = load_data('featnames.csv',True)
trainFeature = load_data(trainFeatFile, True)
trainLabel = load_data(trainLabFile, False)
testFeature = load_data(testFeatFile, True)
data = pd.DataFrame()
data=trainFeature
data['output']=trainLabel[0]
attr = list(xrange(len(features)))
print("start train")
root = ID3_tree(data, pval, attr)
root.save_tree(outputTree)
predict(root,testFeature)