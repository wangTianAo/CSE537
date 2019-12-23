import csv
import argparse
import re
import math

class NaiveBayesClassifier:
	def __init__(self):
		self.spamdict = {} # Dictionary of spam words with frequencies
		self.hamdict = {} # Dictionary of ham words with frequencies
		self.wordprobdict = {} # Dictionary of log probabiltiies for each word
		self.spamcount = 0 # Count of spam mails
		self.hamcount = 0 # Count of ham mails

	# Training method
	def train(self, traindata):
		for line in traindata:
			linedata = line.split(' ')
			if linedata[1] == 'spam':
				# If spam email, add words to spam dictionary
				self.addtospam(linedata)
				self.spamcount+=1
			else:
				# If ham email, add words to ham dictionary
				self.addtoham(linedata)
				self.hamcount+=1
		# Calculate total number of emails
		self.totalcount = self.spamcount+self.hamcount  # Total count of mails
		self.wordcount = len(self.wordprobdict) # Total number of words

	def addtospam(self,line):
		# Starting from i=2, because line[0] has email and line[1] has category
		i = 2
		while i < len(line):
			self.wordprobdict[line[i]] = 0
			if line[i] in self.spamdict:
				# Add frequency if word already exists
				self.spamdict[line[i]] += int(line[i+1])
			else:
				# Create new entry in dictionary if word does not exist
				self.spamdict[line[i]] = int(line[i+1])
			i+=2

	def addtoham(self,line):
		# Starting from i=2, because line[0] has email and line[1] has category
		i = 2
		while i < len(line):
			self.wordprobdict[line[i]] = 0
			if line[i] in self.hamdict:
				# Add frequency if word already exists
				self.hamdict[line[i]] += int(line[i+1])
			else:
				# Create new entry in dictionary if word does not exist
				self.hamdict[line[i]] = int(line[i+1])
			i+=2

	# Smoothing method - Additive (Laplace) smoothing
	def smooth(self,sp):
		# Log probability with smoothing parameter calculated for words not available in training data set
		self.logham = math.log(sp / (self.hamcount + sp * self.wordcount))
		self.logspam = math.log(sp / (self.spamcount + sp * self.wordcount))
		for word in self.wordprobdict:
			# Add smoothing parameter to word's probability for words in training data set
			totham = sp 
			totspam = sp

			if word in self.hamdict:
				totham += self.hamdict[word]
			if word in self.spamdict:
				totspam += self.spamdict[word]
			
			# Normalize for added smoothing parameter
			totham /= (self.hamcount + sp * self.wordcount)
			totspam /= (self.spamcount + sp * self.wordcount)
			
			# Calculate and store the log of probabilities and word in ham and spam dictionaries
			self.wordprobdict[word] = (math.log(totham), math.log(totspam))

	def test(self, line):
		totlogspam = 0.0
		totlogham = 0.0

		i = 2
		while i < len(line):
			if line[i] in self.wordprobdict:
				# If word is available in dictionary, calculate word probabilities
				wordlogham, wordlogspam =  self.wordprobdict[line[i]]
				for j in range(int(line[i+1])):
					totlogham +=  wordlogham
					totlogspam += wordlogspam
			else:
				# If word is not available in dictionary, add normalized probability from smoothing parameter
				totlogham += self.logham
				totlogspam += self.logspam
			i+=2
        
		# If probability of P(spam|w) > P(ham|w), will return True
		return totlogspam > totlogham

def main():
	#Taking input arguments from command line
	parser = argparse.ArgumentParser()
	parser.add_argument('-f1', required=True)
	parser.add_argument('-f2', required=True)
	parser.add_argument('-o', required=True)

	args = vars(parser.parse_args())

	trainfile = args['f1']
	testfile = args['f2']
	outputfile = args['o']

	# Initialization of clasifier object
	classifier = NaiveBayesClassifier()
	with open(trainfile) as tr:
		traindata = tr.readlines()
	# Train the classifier from the emails in training dataset
	classifier.train(traindata)
	print('Training completed')

	smoothparam = 55.0
	classifier.smooth(smoothparam)
	print('Smoothing coefficient:', smoothparam)

	# Testing the classifier on the emails in test dataset
	with open(testfile) as te:
		testdata = te.readlines()

	testdatasize = 0
	# Keep adding entries to output file (.csv)
	with open(outputfile, "w") as csv_file:
		acc = 0
		for line in testdata:
			linedata = line.split(' ')
			testdatasize+=1
			# Get email tag
			email = linedata[0]
			# Get category to measure accuracy
			res = linedata[1]
			if classifier.test(linedata):
				predres = 'spam'
			else:
				predres = 'ham'
			if predres == res:
				# If predicted category is actual category increase accuracy score
				acc+=1
			writer = csv.writer(csv_file, delimiter=',')
			writer.writerow((email, predres))
			# print(res, predres)
	# Calculate accuracy percentage
	accuracy = float(acc) / testdatasize
	print('Prediction Accuracy:'+'{:.2%}'.format(accuracy))

if __name__ == "__main__":
	main()