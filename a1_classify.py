from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix
from sklearn.feature_selection import f_classif
from sklearn.svm import LinearSVC
from sklearn.model_selection import KFold

import numpy as np
import argparse
import sys
import os
import csv
from random import randint
from scipy import stats

def accuracy( C ):
    ''' Compute accuracy given Numpy array confusion matrix C. Returns a floating point value '''

    accu = np.trace(C) / float(np.sum(C))
    return accu

def recall( C ):
    ''' Compute recall given Numpy array confusion matrix C. Returns a list of floating point values '''
    rec_list = [0.,0.,0.,0.]
    for k in range(4):
        rec_list[k] = C[k][k] / float(np.sum(C[k,:]))
    return rec_list

    

def precision( C ):
    ''' Compute precision given Numpy array confusion matrix C. Returns a list of floating point values '''
    pre_list = [0.,0.,0.,0.]
    for k in range(4):
        pre_list[k] = C[k][k] / float(np.sum(C[:,k]))
    return pre_list

def get_clf(k):

    ## svc
    if k == 1:
        clf = LinearSVC()
    ## svc radial basis function
    if k == 2:
        clf = SVC(gamma=2, max_iter=1000)
    if k == 3:
        clf = RandomForestClassifier(n_estimators=10, max_depth=5)
    if k == 4:
        clf = MLPClassifier(alpha=0.05)
    if k == 5:
        clf = AdaBoostClassifier()
    return clf

def class31(filename):
    ''' This function performs experiment 3.1
    
    Parameters
       filename : string, the name of the npz file from Task 2

    Returns:      
       X_train: NumPy array, with the selected training features
       X_test: NumPy array, with the selected testing features
       y_train: NumPy array, with the selected training classes
       y_test: NumPy array, with the selected testing classes
       i: int, the index of the supposed best classifier
    '''
    print('TODO Section 3.1')
    fp = np.load(filename)
    df = fp["arr_0"]
    X = df[:,0:173]
    y = df[:, 173]
    X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2)

    f = open('a1_3.1.csv', 'w',newline='\n')
    w = csv.writer(f, delimiter = ',')

    iBest = -1
    best_accu = -1

    for i in range(1,6):

        clf = get_clf(i)
        clf_fit = clf.fit(X_train,y_train)
        pre_label = clf.predict(X_test)
        C = confusion_matrix(y_test,pre_label)
        line = []
        line.append(i)
        accu = accuracy(C)
        line.append(accu)
        rec = recall(C)
        prec = precision(C)
        line = line + rec + prec
        line = np.append(line, C)
        w.writerow(line)

        if best_accu < accu:
            best_accu = accu
            iBest = i
    f.write("3.1 comment:\n")
    f.close()
    return (X_train, X_test, y_train, y_test,iBest)


def class32(X_train, X_test, y_train, y_test,iBest):
    ''' This function performs experiment 3.2
    
    Parameters:
       X_train: NumPy array, with the selected training features
       X_test: NumPy array, with the selected testing features
       y_train: NumPy array, with the selected training classes
       y_test: NumPy array, with the selected testing classes
       i: int, the index of the supposed best classifier (from task 3.1)  

    Returns:
       X_1k: numPy array, just 1K rows of X_train
       y_1k: numPy array, just 1K rows of y_train
   '''
    print('TODO Section 3.2')
    train_size = [1000,5000,10000,15000,20000]
    clf = get_clf(iBest)
    accu_list = []
    choice_list = []
    #train_1k = {}

    for size in train_size:
        choice = np.random.choice(X_train.shape[0], size ,replace=False)
        choice_list.append(choice)
        new_x_train = X_train[choice]
        new_y_train = y_train[choice]
        clf.fit(new_x_train,new_y_train)
        pre_label = clf.predict(X_test)
        C = confusion_matrix(y_test,pre_label)
        accu_list.append(accuracy(C))

    new_choice = np.random.choice(X_train.shape[0], 1000, replace=False)
    X_1k = X_train[choice]
    y_1k = y_train[choice]
        #train_1k[size] = [X_1k,y_1k]

    f = open('a1_3.2.csv', 'w', newline='\n')
    w = csv.writer(f, delimiter = ',')
    w.writerow(accu_list)
    f.write("3.2 answer: \n")
    f.close()

    return (X_1k, y_1k)
    
def class33(X_train, X_test, y_train, y_test, i, X_1k, y_1k):
    ''' This function performs experiment 3.3
    
    Parameters:
       X_train: NumPy array, with the selected training features
       X_test: NumPy array, with the selected testing features
       y_train: NumPy array, with the selected training classes
       y_test: NumPy array, with the selected testing classes
       i: int, the index of the supposed best classifier (from task 3.1)  
       X_1k: numPy array, just 1K rows of X_train (from task 3.2)
       y_1k: numPy array, just 1K rows of y_train (from task 3.2)
    '''
    print('TODO Section 3.3')
    num_feat = [5,10,20,30,40,50]

    f = open('a1_3.3.csv', 'w',newline='\n')
    w = csv.writer(f, delimiter = ',')

    accu_list = []
    X_32k = []
    X_32k_test = []

    #1
    for k in num_feat:
        selector = SelectKBest(f_classif,k)
        X_new = selector.fit_transform(X_train, y_train)
        pp = selector.pvalues_
        feature_idx = selector.get_support(indices=True)
        best_k = [k]
        for idx in feature_idx:
            best_k.append(pp[idx])

        w.writerow(best_k)
        if k == 5:
            X_32k = X_new
            X_32k_test = X_test[:,feature_idx]

    #2
    p2 = []
    clf = get_clf(i)
    clf_fit = clf.fit(X_32k,y_train)
    pre_label = clf.predict(X_32k_test)
    C = confusion_matrix(y_test,pre_label)
    p2.append(accuracy(C))


    selector_1k = SelectKBest(f_classif, k=5)
    X_1k_new = selector_1k.fit_transform(X_1k,y_1k)
    pp_1k = selector_1k.pvalues_
    feature_idx_1k = selector_1k.get_support(indices=True)


    clf_1k = get_clf(i)
    clf_fit_1k = clf_1k.fit(X_1k_new,y_1k)

    pre_label_1k = clf_1k.predict(X_test[:,feature_idx_1k])
    C_1k = confusion_matrix(y_test,pre_label_1k)
    p2.append(accuracy(C_1k))
    w.writerow(p2)


    #3
    a = "3.3(a):" + "," + "1k features at k = 5: " + "," +  "," + "32k features at k = 5: " + "," + "," + "\n"
    f.write(a)
    b = "3.3(b):" + "," + "1k p-value at k = 5: " + "," +  "," + "32k p-value at k = 5: " + "," + "," + "\n"
    f.write(b)
    f.write("3.3(c): \n")

    f.close()
    return



def class34( filename, i ):
    ''' This function performs experiment 3.4
    
    Parameters
       filename : string, the name of the npz file from Task 2
       i: int, the index of the supposed best classifier (from task 3.1)  
        '''
    print('TODO Section 3.4')
    fp = np.load(filename)
    df = fp["arr_0"]
    X = df[:,0:173]
    y = df[:, 173]
    kf = KFold(n_splits=5,shuffle=True)

    f = open('a1_3.4.csv', 'w',newline='\n')
    w = csv.writer(f, delimiter = ',')

    all_accu = []
    for train_index, test_index in kf.split(X):
        X_train, X_test = X[train_index],X[test_index]
        y_train, y_test = y[train_index],y[test_index]
        accu_list = []
        for k in range(1,6):
            clf = get_clf(k)
            clf.fit(X_train, y_train)
            pre_label = clf.predict(X_test)
            C = confusion_matrix(y_test,pre_label)
            accu_list.append(accuracy(C))

        all_accu.append(accu_list)
        w.writerow(accu_list)

    s_list = []
    new_arr = np.array(all_accu)
    best_i = new_arr[:, i-1]
    for col in range(5):
        if col != i-1:
            S = stats.ttest_rel(best_i, new_arr[:, col])
            s_list.append(S.pvalue)
    w.writerow(s_list)
    f.write("3.4 answer: \n")
    f.close()
    return





    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process each .')
    parser.add_argument("-i", "--input", help="the input npz file from Task 2", required=True)
    args = parser.parse_args()

    # TODO : complete each classification experiment, in sequence.
    # Section 3.1
    X_train, X_test, y_train, y_test,iBest = class31(args.input)
    X_1k,y_1k = class32(X_train, X_test, y_train, y_test,iBest)
    class33(X_train, X_test, y_train, y_test,iBest,X_1k,y_1k)
    class34(args.input, iBest)


