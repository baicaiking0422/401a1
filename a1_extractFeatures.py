import numpy as np
import sys
import argparse
import os
import json
import pandas as pd
import re
import time
import string


bgl_2811 = pd.read_csv("/u/cs401/Wordlists/BristolNorms+GilhoolyLogie.csv")
w_2811 = pd.read_csv("/u/cs401/Wordlists/Ratings_Warriner_et_al.csv")
slang_2811 = [line.rstrip('\n').lower() for line in open("/u/cs401/Wordlists/Slang")]
tp_2811 = [line.rstrip('\n').lower() for line in open("/u/cs401/Wordlists/Third-person")]
cocnj_2811 = [line.rstrip('\n').lower() for line in open("/u/cs401/Wordlists/Conjunct")]


def extract1( comment ):
    ''' This function extracts features from a single comment

    Parameters:
        comment : string, the body of a comment (after preprocessing)

    Returns:
        feats : numpy Array, a 173-length vector of floating point features (only the first 29 are expected to be filled, here)
    '''
    #print('TODO')
    # TODO: your code here    
    feats = np.zeros((1,29))
    tokens = comment.split(" ")

    num_pun, num_words, num_cha = 0,0,0
    AoA, IMG, FAM = [],[],[]
    vms,ams,dms = [],[],[]
    
    for count in range(len(tokens)):
        token = tokens[count]
        
        if token == " " or token == "" or token == "\n":
            continue 
        
        sp = token.rstrip("\n").rfind("/")
        # No"/" split
        if sp == -1:
            continue

        word,tag = token[:sp].lower(), token[sp+1:].lower()

        if tag == "_sp" or (word.isspace() and tag.isspace()):
            continue
        if word != "" and tag == "":
            continue

        #1st-person pron
        fp = ['I','me','my','mine','we','us','our','ous']
        if word in fp:
            feats[0][0]+=1
        #2ndpron
        sep = ['you','your','yours','u','ur','urs']
        if word in sep:
            feats[0][1]+=1
        #3repron
        if word in tp_2811:
            feats[0][2]+=1
        #4.coordinating conj
        if word in cocnj_2811:
            feats[0][3]+=1
        #5. past tense v
        if tag == "vbd":
            feats[0][4]+=1
        #6.future test v
        ft = ['\'ll',"will",'gonna']
        if (word in ft) or (count+2 < len(tokens) and 
                            word == 'going' and 
                            tokens[count+1].split("/")[0] == "to" and 
                            tokens[count+2].split("/")[1]=="vb"):
            feats[0][5]+=1 
        #7. commas number
        if tag == ',':
            feats[0][6]+=1
        #8. multi-character punctuation token
        match = re.search(r"\W{2,}",word)
        if len(word) > 1 and match:
            feats[0][7]+=1
        #9. number of common nouns
        cn = ['nn','nns']
        if tag in cn:
            feats[0][8] += 1
        #10. proper n
        ppn = ['nnp','nnps']
        if tag in ppn:
            feats[0][9] += 1
        #11. adv
        adv = ['rb','rbr','rbs']
        if tag in adv:
            feats[0][10]+= 1
            
        #12. wh-
        wh = ['wdt','wp','wp$','wrb']
        if tag in wh:
            feats[0][11] += 1 
            
        #13. slang
        if word in slang_2811:
            feats[0][12] += 1
        
        #14. upper >= 3
        if len(word) >= 3 and word.isupper():
            feats[13]+=1
        #15
        if tag == ".":
            num_pun+=1
        #16
        if all(ch in string.punctuation for ch in word) == False:
            num_cha += len(word)
            num_words += 1
        #17
        #18-23

        word_df = bgl_2811[bgl_2811.WORD == word]
        if not word_df.empty:
            aoa_value = word_df["AoA (100-700)"].values[0]
            img_value = word_df["IMG"].values[0]
            fam_value = word_df["FAM"].values[0]
            AoA.append(aoa_value)
            IMG.append(img_value)
            FAM.append(fam_value)
            
        word_df2 = w_2811[w_2811.Word == word]
        if not word_df2.empty:
            vms_v = word_df2["V.Mean.Sum"].values[0]
            ams_v = word_df2["A.Mean.Sum"].values[0]
            dms_v = word_df2["D.Mean.Sum"].values[0]
            vms.append(vms_v)
            ams.append(ams_v)
            dms.append(dms_v)
                
    
    #17
    if num_pun == 0:
        last = len(tokens) - 1
        if last > 0:
            while tokens[last] == '':
                last -= 1
                if last < 0:
                    break
            if tokens[last] != '\n':
                num_pun+=1
    feats[0][16] += num_pun
    
    #15
    if num_pun != 0:
        feats[0][14] += num_words / num_pun
    #16
    if num_words != 0:
        feats[0][15] += num_cha / num_words
    
    #18-23

    if AoA != []:
        feats[0][17]+=np.mean(AoA)
        feats[0][20]+=np.std(AoA)
    if IMG != []:
        feats[0][18]+=np.mean(IMG)
        feats[0][21]+=np.std(IMG)
    if FAM != []:
        feats[0][19]+=np.mean(FAM)
        feats[0][22]+=np.std(FAM)        
    #24-29
    if vms != []:
        feats[0][23]+=np.mean(vms)
        feats[0][26]+=np.std(vms)
    if ams != []:
        feats[0][24]+=np.mean(ams)
        feats[0][27]+=np.std(ams)
    if dms != []:
        feats[0][25]+=np.mean(dms)
        feats[0][28]+=np.std(dms)

    return feats

def main( args ):

    data = json.load(open(args.input))
    feats = np.zeros( (len(data), 173+1))

    # TODO: your code here
    alt_ids = [line.rstrip('\n').lower() for line in open("/u/cs401/A1/feats/Alt_IDs.txt",'r')]
    left_ids= [line.rstrip('\n').lower() for line in open("/u/cs401/A1/feats/Left_IDs.txt",'r')]
    right_ids=[line.rstrip('\n').lower() for line in open("/u/cs401/A1/feats/Right_IDs.txt",'r')]
    center_ids = [line.rstrip('\n').lower() for line in open("/u/cs401/A1/feats/Center_IDs.txt",'r')]
    
    left_fea=np.load('/u/cs401/A1/feats/Left_feats.dat.npy')
    center_fea=np.load('/u/cs401/A1/feats/Center_feats.dat.npy')
    right_fea=np.load('/u/cs401/A1/feats/Right_feats.dat.npy')
    alt_fea=np.load('/u/cs401/A1/feats/Alt_feats.dat.npy')
    
    cls_list = {"Left": [0,left_ids,left_fea],
                "Center":[1,center_ids,center_fea],
                "Right":[2,right_ids,right_fea],
                "Alt":[3,alt_ids,alt_fea]}

    
    for i in range(len(data)):
        # if i % 5000 == 0:
        #     print("passed: ",i)
        j = data[i]
        
        usrid, cat = j["id"], j["cat"]
        result = extract1(j["body"])
        
        
        row = cls_list[cat][1].index(usrid)
        fea_144 = cls_list[cat][2][row].reshape(1,144)
        cls_id = cls_list[cat][0]
        
        feats[i,0:29] = result
        feats[i,29:173] = fea_144
        feats[i,173] = cls_id
           
    np.savez_compressed( args.output, feats)

    
if __name__ == "__main__": 

    parser = argparse.ArgumentParser(description='Process each .')
    parser.add_argument("-o", "--output", help="Directs the output to a filename of your choice", required=True)
    parser.add_argument("-i", "--input", help="The input JSON file, preprocessed as in Task 1", required=True)
    args = parser.parse_args()
                 

    main(args)

