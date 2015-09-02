############################################################
# Author: Nebil Ali
# Date: Friday, March 6, 2015
# Desc: Rudementary Spam filter using bag of words
############################################################

student_name = "Nebil Ali"

############################################################
# Imports
############################################################

import email
import operator
from collections import Counter
import math 
import Queue
from os import listdir
from os.path import join

############################################################
# Spam Filter
############################################################

def load_tokens(email_path):
    f = open(email_path)
    message = email.message_from_file(f)
    f.close() 
    lines = email.iterators.body_line_iterator(message)
    return [ word for line in lines for word in line.strip().split()]


#returns log of probabilities of unique tokens in emails
def log_probs(email_paths, smoothing):
    superList = []
    Pw = {}
    superList = [token for email in email_paths for token in load_tokens(email)]
    V = set(superList)
    lenCount = len(superList)
    lenV = len(V)
    cnt = Counter(superList)

    Pw['<UNK>'] = math.log(smoothing/(lenCount +smoothing*(lenV+1)))
    for w in V:
        Pw[w] = math.log((cnt[w]+smoothing)/(lenCount +smoothing*(lenV+1)))
    return Pw

class SpamFilter(object):

    #builds model
    def __init__(self, spam_dir, ham_dir, smoothing):
        spam_emails= [join(spam_dir,f) for f in listdir(spam_dir)]
        ham_emails= [join(ham_dir,f) for f in listdir(ham_dir)]
        
        self.spamDic = log_probs(spam_emails,smoothing)
        self.hamDic = log_probs(ham_emails,smoothing)
        self.a = smoothing
        self.inter = set(self.spamDic.keys()).intersection(set(self.hamDic.keys()))

        spamNum = float(len(spam_emails))
        nSpamNum = float(len(ham_emails))
        
        self.Pspam =spamNum/(spamNum+nSpamNum)
        self.nPspam = nSpamNum/(spamNum+nSpamNum)
        
    
    
    def is_spam(self, email_path):
        docTokens=load_tokens(email_path)
        docCnt = Counter(docTokens) #Number of times words appear in Doc

        spamWordProb = 1
        nSpamWordProb = 1
        wordTemp = "<UNK>"
        for word in docCnt.keys(): 
            if word in self.spamDic: 
                spamWordProb = spamWordProb+self.spamDic[word]*docCnt[word]
            else: 
                spamWordProb = spamWordProb+self.spamDic[wordTemp]*docCnt[word]
            if word  in self.hamDic: 
                nSpamWordProb = nSpamWordProb+self.hamDic[word]*docCnt[word]
            else: 
                nSpamWordProb = nSpamWordProb+self.hamDic[wordTemp]*docCnt[word]
        spamWordProb= spamWordProb*self.Pspam #Pspam = prob of being spam 
        nSpamWordProb = nSpamWordProb*self.nPspam # nPspam = prom of not spam
        if spamWordProb > nSpamWordProb:
            return True
        else : 
            return False

    def most_indicative_spam(self, n):
        ret = []
        intersects = self.inter
        for word in self.spamDic.keys(): 
            if word in intersects: 
                ret.append((word,self.spamDic[word] - math.log( (math.exp(self.spamDic[word])*self.Pspam + math.exp(self.hamDic[word])*self.nPspam) )))    
        return  [key for key, val in sorted(ret, key = operator.itemgetter(1),reverse= True)[:n]]

    def most_indicative_ham(self, n):
        ret = []
        intersects = self.inter
        for word in self.hamDic.keys(): 
            if word in intersects: 
                ret.append((word,self.hamDic[word] - math.log( (math.exp(self.spamDic[word])*self.Pspam + math.exp(self.hamDic[word])*self.nPspam) )))    
        return  [key for key, val in sorted(ret, key = operator.itemgetter(1),reverse= True)[:n]]

############################################################
# Test
############################################################

count = 0
sf = SpamFilter("data/train/spam","data/train/ham",1e-5)
hamDir = "data/dev/ham/dev"
spamDir = "data/dev/spam/dev"

#how many ham emails are detected as ham
for i in range(1,201): 
    if sf.is_spam(hamDir+str(i)) == False: 
        count = count+1

#how many spam emails are detected as spam
for i in range(201,401): 
    if sf.is_spam(spamDir+str(i)) == True: 
        count = count+1


print float(count*100)/400, "% are correctly classified"