import argparse
import os
import sys

import numpy as np
'''
Author: Yuyao Wang
Date: 2019-12-4
'''

###############################################################################################
# Command:
# python3 q2_classifier.py -f1 <train_dataset> -f2 <test_dataset> -o <output_file>
'''
python3 q2_classifier.py \
            -f1 data/train \
            -f2 data/test \
            -o output/q2.csv
'''
###############################################################################################

# parameters
spam_words_count = 0
ham_words_count = 0
spam_emails_count = 0
ham_emails_count = 0
total_emails = 0
total_words = 0
noise_count = 0
spam_unique_words_count = 0
ham_unique_words_count = 0
repeated = 0
laplace_k = 1

total_test_emails = 0
correct_predication = 0
actual_ham = 0
actual_spam = 0
correct_pred_ham = 0
correct_pred_spam = 0
total_pred_ham = 0
total_pred_spam = 0

_args = 7
def check_args(args):
    if len(args) == _args:
        return True
    else:
        return False

def spam_log_probability(words, prob_spam, laplace_smoothing_k, use_laplace_smoothing):
    if not isinstance(laplace_smoothing_k, int) or laplace_smoothing_k < 1:
        print('laplace smoothing k is not valid.')
        sys.exit(0)
    # log(P(words|spam)) + log(P(spam))
    index = 2
    result = np.log(prob_spam)
    while index < len(words):
         key = ('spam', words[index])
         if key in train_vocabulary:
             val = float(train_vocabulary[key])
             result += np.log(float(val/float(spam_words_count)))
         else:
             if use_laplace_smoothing:
                result += np.log(laplace_smoothing_k/float(spam_words_count + (laplace_smoothing_k * spam_unique_words_count)))
             else:
                 result += 0
                 pass
         index += 2
    return result

def ham_log_probability(words, prob_ham, laplace_smoothing_k, use_laplace_smoothing):
    if not isinstance(laplace_smoothing_k, int) or laplace_smoothing_k < 1:
        print('laplace smoothing k is not valid.')
        sys.exit(0)
    index = 2
    result = np.log(prob_ham)
    # log(P(words|ham)) + log(P(ham))
    while index < len(words):
        key = ('ham', words[index])
        if key in train_vocabulary:
            val = float(train_vocabulary[key])
            result += np.log(float(val/float(ham_words_count)))
        else:
            if use_laplace_smoothing:
                result += np.log(laplace_smoothing_k/float(ham_words_count + (laplace_smoothing_k * ham_unique_words_count)))
            else:
                result += 0
                pass
        index += 2
    return result

if __name__ == '__main__':

    # configs
    parser = argparse.ArgumentParser(description='Spam Classifier')
    parser.add_argument('-f1', help='File name of training dataset')
    parser.add_argument('-f2', help='File name of test dataset')
    parser.add_argument('-o', help='Output file name')

    args = parser.parse_args()
    # print(args)
    args_dict = vars(args)

    train_file = args_dict['f1']
    test_file = args_dict['f2']
    output_file = args_dict['o']

    # dic
    train_vocabulary = {}

    if check_args(sys.argv):
        print("-------------------------------")
        print("Spam classifier running.")
        print("Train file:", train_file)
        print("Test file:", test_file)
        print("Output file:", output_file)
        print("-------------------------------")
        pass
    else:
        print("Invalid arguments.")
        print("Command: python q2_classifier.py --help for help.")
        sys.exit(0)

    #----------------------Training-----------------------------------
    if not os.path.exists(train_file) or not os.path.exists(test_file):
        print('Exist no', train_file,' or ', test_file)
        sys.exit(0)

    else:
        print("Training and test data detected.")
        print("Training...")
        size = 0
        with open(train_file) as tf:
            line = tf.readline()
            while line:
                size += 1
                line = tf.readline()
        tf.close()
        print("size of training data:",size)

        instance = 0
        with open(train_file) as tf:
            line = tf.readline()
            # Email
            while line:
                instance += 1
                words = line.split(' ')
                # print(words)
                # sys.exit(0)
                # label of a sample
                label = words[1]
                if label == 'spam':
                    spam_emails_count += 1
                elif label == 'ham':
                    ham_emails_count += 1
                else:
                    # print(label)
                    noise_count += 1

                # Words
                index = 2
                while index < len(words):
                    total_words += 1
                    key = (words[1], words[index])
                    val = words[index+1]

                    if label == 'spam':
                        spam_words_count += 1
                    elif label == 'ham':
                        ham_words_count += 1
                    else:
                        pass

                    if key not in train_vocabulary:
                        train_vocabulary[key] = float(val)
                        if label == 'spam':
                            spam_unique_words_count += 1
                        elif label == 'ham':
                            ham_unique_words_count += 1
                        else:
                            pass
                    else:
                        repeated += 1
                        train_vocabulary[key] += float(val)
                    index += 2
                # printProgress(instance, size, prefix='Training:', suffix='Complete', barLength=50)
                line = tf.readline()
                # print(label)
        tf.close()

        #----------------------Printing-----------------------------------
        total_emails = spam_emails_count + ham_emails_count + noise_count
        print("Number of spam emails:", spam_emails_count)
        print("Number of ham emails:", ham_emails_count)
        print("Noise:", noise_count)
        print("-------------------------------")
        print("Number of emails:", total_emails)
        print("Number of spam words", spam_words_count)
        print("Number of ham words", ham_words_count)
        print("Number of unique spam words", spam_unique_words_count)
        print("Number of unique ham words", ham_unique_words_count)
        print("Number of words in total:",total_words)

        # print(repeated + spam_unique_words_count + ham_unique_words_count)
        spam_probability = float(float(spam_words_count)/float(total_words))
        ham_probability = float(float(ham_words_count)/float(total_words))
        print("Probability of spam = {0:1.3f} ".format(spam_probability))
        print("Probability of ham= {0:1.3f} ".format(ham_probability))

        #----------------------Output-----------------------------------
        print("-------------------------------")
        if not os.path.exists(output_file):
            print("writing output file")
            pass
        else:
            print(output_file, ' exist')
            os.remove(output_file)
            print('Old file has deleted, writing new output file.')
        output_file = open(output_file, 'w')

        #----------------------Testing-----------------------------------
        print("-------------------------------")
        print("Testing...")
        # print(train_vocabulary)
        with open(test_file) as ttf:
            line = ttf.readline()
            while line:
                words = line.split(' ')
                total_emails += 1
                actual_label = words[1]
                if actual_label == 'spam':
                    actual_spam += 1
                elif actual_label == 'ham':
                    actual_ham += 1
                else:
                    pass
                spam_score = \
                    spam_log_probability(words=words,
                                         prob_spam=spam_probability,
                                         laplace_smoothing_k=laplace_k,
                                         use_laplace_smoothing=True)
                ham_score = \
                    ham_log_probability(words=words,
                                        prob_ham=ham_probability,
                                        laplace_smoothing_k=laplace_k,
                                        use_laplace_smoothing=True)
                if spam_score > ham_score:
                    predicate_label = 'spam'
                    output_file.write(words[0]+", spam\n")
                    total_pred_spam += 1
                else:
                    predicate_label = 'ham'
                    output_file.write(words[0] + ", ham\n")
                    total_pred_ham += 1

                if predicate_label == actual_label:
                    correct_predication += 1
                    if predicate_label == 'spam':
                        correct_pred_spam += 1
                    elif predicate_label == 'ham':
                        correct_pred_ham += 1
                    else:
                        pass
                total_test_emails += 1
                line = ttf.readline()
        output_file.close()

    print("Total number of emails:", total_test_emails)
    print("Number of correct prediction:", correct_predication)
    print("Actual number of spam:", actual_spam)
    print("Number of prediction for spam:", total_pred_spam)
    print("Number of correct prediction for spam:", correct_pred_spam)
    print("Overall Accuracy: {0:1.2f} %".format(correct_predication*100/total_test_emails))
    print("Spam Classification Accuracy: {0:1.2f} %".format(correct_pred_spam*100/total_pred_spam))