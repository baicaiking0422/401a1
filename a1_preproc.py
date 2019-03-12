import sys
import argparse
import os
import json

import re

###### MY IMPORT #########
import html
import spacy
import string
##########################

indir = '/u/cs401/A1/data/';

abbr = [line.rstrip('\n') for line in open("/u/cs401/Wordlists/abbrev.english")]
abbr2 = [line.rstrip('\n') for line in open("/u/cs401/Wordlists/pn_abbrev.english")]
abbr_all = abbr + abbr2
stopwords_2811 = [line.rstrip('\n') for line in open("/u/cs401/Wordlists/StopWords")]
nlp_2811 = spacy.load('en', disable=['parser','ner'])


def preproc1( comment , steps=range(1,11)):
    ''' This function pre-processes a single comment

    Parameters:                                                                      
        comment : string, the body of a comment
        steps   : list of ints, each entry in this list corresponds to a preprocessing step  

    Returns:
        modComm : string, the modified comment 
    '''

    modComm = ''
    if 1 in steps:
        modComm = comment.replace('\n',' ').replace('\r',' ')
    if 2 in steps:
        if min(steps) == 2:
            chg = comment
        else:
            chg = modComm
        modComm = html.unescape(chg)
    if 3 in steps:
        if min(steps) == 3:
            chg = comment
        else:
            chg = modComm
        chg = chg.replace('\n','')
        pattern1 = r"http\S+"
        chg = re.sub(pattern1,"",chg)
        pattern2 = r"www\.\S+"
        modComm = re.sub(pattern2,"",chg)
    if 4 in steps:
        if min(steps) == 4:
            chg = comment
        else:
            chg = modComm
        modList = chg.strip().split(" ")
        modList = re.findall(r"[\wn't]+|[!\"#$%&\'()*+,-./:;<=>?@[\\\]^_`{|}~]*", chg)
        newList = []
        
        i = 0
        while i < len(modList):
            if ((i+2) <= len(modList)-1) and modList[i] == '.' and modList[i+2] == '.':
                checker = modList[i-1]+modList[i]+modList[i+1]+modList[i+2]
                for item in abbr_all:
                    if checker == item:
                        newList.pop()
                        newList.append(checker)
                        i += 3
            newList.append(modList[i])
            i += 1
        modComm = ' '.join(newList).strip()
    
    if 5 in steps:
        if min(steps) == 5:
            chg = comment
        else:
            chg = modComm
            
        chg = chg.split(" ")
        for i in range(len(chg)):
            if len(chg[i]) >= 3:
                if chg[i][-2] == "'" and chg[i][-1] == "t":
                    chg[i] =" ".join(re.split(r"(n't)",chg[i])[:-1])
                elif chg[i][-1] == "'":
                    chg[i] =" ".join(re.split(r"(')",chg[i])[:-1])
                elif (chg[i][-2] == "'") and (chg[i][-1] == "s"):
                    chg[i] = " ".join(re.split(r"('s)",chg[i])[:-1])
                elif (chg[i][-2] == "'") and (chg[i][-1] == "m"):
                    chg[i] = " ".join(re.split(r"('m)",chg[i])[:-1])
                elif (chg[i][-2] == "'") and (chg[i][-1] == "d"):
                    chg[i] = " ".join(re.split(r"('d)",chg[i])[:-1])
                elif (chg[i][-2] == "'") and (chg[i][-1] == "n"):
                    chg[i] = " ".join(re.split(r"('n)",chg[i])[:-1]) 
                elif (chg[i][-3] == "'") and (chg[i][-2:] == "re"):
                    chg[i] = " ".join(re.split(r"('re)",chg[i])[:-1])
                elif (chg[i][-3] == "'") and (chg[i][-2:] == "ve"):
                    chg[i] = " ".join(re.split(r"('ve)",chg[i])[:-1])
                elif (chg[i][-3] == "'") and (chg[i][-2:] == "ll"):
                    chg[i] = " ".join(re.split(r"('ll)",chg[i])[:-1])   
                elif chg[i][1] == "'" and (chg[i][0] == "t"):
                    chg[i] = " ".join(re.split(r"(t')",chg[i]))
                elif chg[i][1] == "'" and (chg[i][0] == "y"):
                    chg[i] = " ".join(re.split(r"(y')",chg[i]))             
                else:
                    continue
        modComm = ' '.join(chg).strip()
    if 6 in steps:
        if min(steps) == 6:
            chg = comment
        else:
            chg = modComm
        punc = [item for item in string.punctuation]
        ut = nlp_2811(chg)
        newList = []
        for i in range(len(ut)):
            token = ut[i].text
            tag = ut[i].tag_
            if i>0 and token in punc and ut[i-1].text in punc and tag == ut[i-1].tag_:
                position = newList[-1].rfind("/")
                if position == -1:
                    last_text = newList[-1]
                last_text = newList[-1][:position]
                newList.pop()
                new = last_text + token +'/'+ tag
            elif token == ' ':
                continue
            else: 
                new = token + '/'+ tag  
            newList.append(new) 

        modComm = ' '.join(newList)
        #########
    if 7 in steps:
        if min(steps) == 7:
            chg = comment
        else:
            chg = modComm

        modList = chg.split(" ")        
        for stop in stopwords_2811:
            i = len(modList) - 1
            while i >= 0:
                if modList[i] == "":
                    i-=1
                    continue
                position = modList[i].rfind("/")
                if position == -1:
                    w = modList[i]
                w = modList[i][:position]
                if len(w)!= 0 and w.lower() == stop:
                    modList.pop(i)
                i -= 1  
        modComm = ' '.join(modList)
        
    if 8 in steps:
        if min(steps) == 8:
            chg = comment
        else:
            chg = modComm
        modList = chg.replace("\r"," ").replace("\n"," ").split(" ")
        newList = []
        punc = [item for item in string.punctuation]
        for i in range(len(modList)):
            if modList[i] == '':
                continue
            position = modList[i].rfind("/")
            if position == -1:
                fore = modList[i]
                back = '/'
            else:
                fore = modList[i][:position]
                back = modList[i][position:]
            #'/'
            if len(fore) == 0 or fore[0] in punc:
                newList.append(modList[i])
                continue
            #if fore is word
            utt = nlp_2811(fore)
            if utt[0].lemma_[0] == "-" and utt[0].text[0] != "-":
                newList.append(fore+back)
            else:
                newList.append(utt[0].lemma_+back)

        modComm = ' '.join(newList)
        
    if 9 in steps:
        if min(steps) == 9:
            chg = comment
        else:
            chg = modComm   
        
        modList = chg.split(" ")
        newList = []
        punc = [".","!","?"]
        for i in range(len(modList)):
            if (modList[i] == '') or (modList[i][0] not in punc):
                newList.append(modList[i])
            else:
                utt = modList[i-1].split("/")
                if len(utt) == 0:
                    continue
                token = utt[0]+ '.'
                if token in abbr_all:
                    newList.append(modList[i])
                else:
                    newList.append(modList[i])
                    newList.append("\n")
        modComm = " ".join(newList)
    if 10 in steps:
        if min(steps) == 10:
            chg = comment
        else:
            chg = modComm
        modComm = chg.lower()
    return modComm

def main( args ):

    allOutput = []
    for subdir, dirs, files in os.walk(indir):
        for file in files:
            fullFile = os.path.join(subdir, file)
            #print(file)
            print( "Processing " + fullFile)
            #print(args.max)

            data = json.load(open(fullFile))
            count = 0
            for line in data:
                # if count % 1000 == 0:
                #     print(count)
                j = json.loads(line)
                new = {}
                result = preproc1(j["body"])
                new["id"],new["body"],new["cat"] = j["id"], result, file
                allOutput.append(new)
                count += 1
                if count == int(args.max):
                    break            
            # TODO: select appropriate args.max lines
            # TODO: read those lines with something like `j = json.loads(line)`
            # TODO: choose to retain fields from those lines that are relevant to you
            # TODO: add a field to each selected line called 'cat' with the value of 'file' (e.g., 'Alt', 'Right', ...) 
            # TODO: process the body field (j['body']) with preproc1(...) using default for `steps` argument
            # TODO: replace the 'body' field with the processed text
            # TODO: append the result to 'allOutput'
            
    fout = open(args.output, 'w')
    fout.write(json.dumps(allOutput))
    fout.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process each .')
    parser.add_argument('ID', metavar='N', type=int, nargs=1,
                        help='your student ID')
    parser.add_argument("-o", "--output", help="Directs the output to a filename of your choice", required=True)
    parser.add_argument("--max", help="The maximum number of comments to read from each file", default=10000)
    args = parser.parse_args()
    #print(args)

    if (int(args.max) > 200272):
        print( "Error: If you want to read more than 200,272 comments per file, you have to read them all." )
        sys.exit(1)
        
    main(args)
