#!/usr/bin/python3
import sys
import csv
import pickle
import mysql.connector
import requests
import threading
import numpy as np
import pandas as pd
import urllib.parse as parse
from urllib.parse import unquote
from sklearn import model_selection
from nltk.tokenize import word_tokenize
from sklearn.linear_model import LogisticRegression
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from tensorflow.python.tools.saved_model_cli import preprocess_input_exprs_arg_string

np.random.seed(42)

f1 = '/opt/security/lib/DecisionTreeClassifier.sav'
f2 = '/opt/security/lib/SVC.sav'
f3 = '/opt/security/lib/GaussianNB.sav'
f4 = '/opt/security/lib/KNeighborsClassifier.sav'
f5 = '/opt/security/lib/RandomForestClassifier.sav'
f6 = '/opt/security/lib/MLPClassifier.sav'

# load the models from disk
loaded_model1 = pickle.load(open(f1, 'rb'))
loaded_model2 = pickle.load(open(f2, 'rb'))
loaded_model3 = pickle.load(open(f3, 'rb'))
loaded_model4 = pickle.load(open(f4, 'rb'))
loaded_model5 = pickle.load(open(f5, 'rb'))
loaded_model6 = pickle.load(open(f6, 'rb'))
model = Doc2Vec.load("/opt/security/lib/d2v.model")


# Create a function to convert an array of strings to a set of features
def getVec(text):
    features = []
    for i, line in enumerate(text):
        test_data = word_tokenize(line.lower())
        v1 = model.infer_vector(test_data)
        featureVec = v1
        lineDecode = unquote(line)
        lowerStr = str(lineDecode).lower()
        feature1 = int(lowerStr.count('link'))
        feature1 += int(lowerStr.count('object'))
        feature1 += int(lowerStr.count('form'))
        feature1 += int(lowerStr.count('embed'))
        feature1 += int(lowerStr.count('ilayer'))
        feature1 += int(lowerStr.count('layer'))
        feature1 += int(lowerStr.count('style'))
        feature1 += int(lowerStr.count('applet'))
        feature1 += int(lowerStr.count('meta'))
        feature1 += int(lowerStr.count('img'))
        feature1 += int(lowerStr.count('iframe'))
        feature1 += int(lowerStr.count('marquee'))
        # add feature for malicious method count
        feature2 = int(lowerStr.count('exec'))
        feature2 += int(lowerStr.count('fromcharcode'))
        feature2 += int(lowerStr.count('eval'))
        feature2 += int(lowerStr.count('alert'))
        feature2 += int(lowerStr.count('getelementsbytagname'))
        feature2 += int(lowerStr.count('write'))
        feature2 += int(lowerStr.count('unescape'))
        feature2 += int(lowerStr.count('escape'))
        feature2 += int(lowerStr.count('prompt'))
        feature2 += int(lowerStr.count('onload'))
        feature2 += int(lowerStr.count('onclick'))
        feature2 += int(lowerStr.count('onerror'))
        feature2 += int(lowerStr.count('onpage'))
        feature2 += int(lowerStr.count('confirm'))
        # add feature for ".js" count
        feature3 = int(lowerStr.count('.js'))
        # add feature for "javascript" count
        feature4 = int(lowerStr.count('javascript'))
        # add feature for length of the string
        feature5 = int(len(lowerStr))
        # add feature for "<script"  count
        feature6 = int(lowerStr.count('script'))
        feature6 += int(lowerStr.count('<script'))
        feature6 += int(lowerStr.count('&lt;script'))
        feature6 += int(lowerStr.count('%3cscript'))
        feature6 += int(lowerStr.count('%3c%73%63%72%69%70%74'))
        # add feature for special character count
        feature7 = int(lowerStr.count('&'))
        feature7 += int(lowerStr.count('<'))
        feature7 += int(lowerStr.count('>'))
        feature7 += int(lowerStr.count('"'))
        feature7 += int(lowerStr.count('\''))
        feature7 += int(lowerStr.count('/'))
        feature7 += int(lowerStr.count('%'))
        feature7 += int(lowerStr.count('*'))
        feature7 += int(lowerStr.count(';'))
        feature7 += int(lowerStr.count('+'))
        feature7 += int(lowerStr.count('='))
        feature7 += int(lowerStr.count('%3C'))
        # add feature for http count
        feature8 = int(lowerStr.count('http'))

        # append the features
        featureVec = np.append(featureVec, feature1)
        featureVec = np.append(featureVec, feature2)
        featureVec = np.append(featureVec, feature3)
        featureVec = np.append(featureVec, feature4)
        featureVec = np.append(featureVec, feature5)
        featureVec = np.append(featureVec, feature6)
        featureVec = np.append(featureVec, feature7)
        featureVec = np.append(featureVec, feature8)
        features.append(featureVec)
    return features


# Grab links
conn = mysql.connector.connect(host='localhost', database='app', user='diego', password='dCb#1!x0%gjq')
cursor = conn.cursor()
cursor.execute('select reason from escalate')
r = [i[0] for i in cursor.fetchall()]
conn.close()
data = []
for i in r:
    data.append(i)
Xnew = getVec(data)

# 1 DecisionTreeClassifier
ynew1 = loaded_model1.predict(Xnew)
# 2 SVC
ynew2 = loaded_model2.predict(Xnew)
# 3 GaussianNB
ynew3 = loaded_model3.predict(Xnew)
# 4 KNeighborsClassifier
ynew4 = loaded_model4.predict(Xnew)
# 5 RandomForestClassifier
ynew5 = loaded_model5.predict(Xnew)
# 6 MLPClassifier
ynew6 = loaded_model6.predict(Xnew)


# show the sample inputs and predicted outputs
def assessData(i):
    score = ((.175 * ynew1[i]) + (.15 * ynew2[i]) + (.05 * ynew3[i]) + (.075 * ynew4[i]) + (.25 * ynew5[i]) + (
                .3 * ynew6[i]))
    if score >= .5:
        try:
            preprocess_input_exprs_arg_string(data[i], safe=False)
        except:
            pass


for i in range(len(Xnew)):
    t = threading.Thread(target=assessData, args=(i,))
    #     t.daemon = True
    t.start()
