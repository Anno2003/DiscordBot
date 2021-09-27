import glob
import nltk
from nltk.stem.lancaster import LancasterStemmer 
import numpy as np
import tflearn
import tensorflow as tf
import random
import json

stemmer = LancasterStemmer()

class Chatbot:
    def __init__(self):
        self.words      = []
        self.classes    = []
        self.documents  = []
        self.trainX     = []
        self.trainY     = []
        
        self.model = None
        
        
        # data structure to hold user context
        self.context ={}
        self.ERROR_THRESHOLD = 0.25
    
    def __clean_up_sentence(self,sentence):
        # tokenize the pattern
        sentence_words = nltk.word_tokenize(sentence)
        # stem each word
        sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
        return sentence_words
    
    def __bow(self,sentence, words, show_details=False):
        # returns bag of words array: 0 or 1 for each word in the bag that exists in the sentence
        sentence_words = self.__clean_up_sentence(sentence)
        bag = [0]*len(words)  
        for s in sentence_words:
            for i,w in enumerate(words):
                if w == s: 
                    bag[i] = 1
                    if show_details:
                        print ("found in bag: %s" % w)
    
        return(np.array(bag))

    def __classify(self,sentence):
        results = self.model.predict([self.__bow(sentence, self.words)])[0]
        results = [[i,r] for i,r in enumerate(results) if r>self.ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append((self.classes[r[0]], r[1]))
        return return_list
    
    def response(self,sentence, userID='123', show_details=False):
        results = self.__classify(sentence)
        if results:
            while results:
                for i in self.intents['intents']:
                    if i['tag'] == results[0][0]:
                        if 'context_set' in i:
                            if show_details: print ('context:', i['context_set'])
                            
                            self.context[userID] = i['context_set']
    
                        if not 'context_filter' in i or \
                            (userID in self.context and 'context_filter' in i and i['context_filter'] == self.context[userID]):
                            if show_details: print ('tag:', i['tag'])
                            return random.choice(i['responses'])
    
                results.pop(0)
    
    def loadIntents(self,intentPath):
        ignoreWords = ['?']
        
        with open('intents.json') as jsonData:
            self.intents = json.load(jsonData)
            
        for intent in self.intents['intents']:
            for pattern in intent['patterns']:
                word = nltk.word_tokenize(pattern)
                self.words.extend(word)
        
                self.documents.append((word,intent['tag']))
        
                if intent['tag'] not in self.classes:
                    self.classes.append(intent['tag'])
        
        self.words = [stemmer.stem(w.lower()) for w in self.words if w not in ignoreWords]
        self.words = sorted(list(set(self.words)))

        self.classes = sorted(list(set(self.classes)))
        
        training    = []
        output      = []
        outputEmpty = [0]*len(self.classes)
        
        for doc in self.documents:
            bag             = []
            patternWords    = doc[0]
            patternWords    = [stemmer.stem(word.lower()) for word in patternWords]
    
            for w in self.words:
                bag.append(1) if w in patternWords else bag.append(0)
    
            outputRow                           = list(outputEmpty)
            outputRow[self.classes.index(doc[1])]    = 1
            training.append([bag,outputRow])
        
        random.shuffle(training)
        training    = np.array(training)

        self.trainX      = list(training[:,0])
        self.trainY      = list(training[:,1])
        
        #build neural network
        net = tflearn.input_data(shape=[None, len(self.trainX[0])])
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, len(self.trainY[0]), activation='softmax')
        net = tflearn.regression(net)
        
        #define model and setup tensorboard
        self.model = tflearn.DNN(net,tensorboard_dir='tflearn_logs')
    
    def trainModel(self):
        tf.compat.v1.reset_default_graph()
        self.model.fit(self.trainX,self.trainY,n_epoch=1000,batch_size=8,show_metric=False)
        self.model.save('model.tflearn')
        
    def loadModel(self):
        if (not glob.glob("./model.tflearn*")):
            self.trainModel()
        else:
            self.model.load('./model.tflearn')
#==========================================
# example usage:
#
#import chatbot
#
#bot = chatbot.Chatbot()
# 
#bot.loadIntents("./intents.json")
#bot.trainModel() # in case intents.json changes
#bot.loadModel() # loadModel automatically trains model if no model.tflearn exist
#
#bot.response("hello there!")

