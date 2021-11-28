# cs221project

First I extracted the urls for train and test misinformation and non-misinformation articles by running the following commands:

\# create list of training non-misinformation articles

python3 get_urls.py true real    

\# create list of training misinformation articles

python3 get_urls.py true fake    

\# create list of testing non-misinformation articles

python3 get_urls.py false real    

\# create list of testing misinformation articles

python3 get_urls.py false fake    

To preprocess the data, I did the following:

\# create bag-of-words features for training set

python3 preprocessSentences.py -p data -o train    

\# create bag-of-words features for testing set

python3 preprocessSentences.py -p data -o test -v data/train_vocab_5.txt    

\# create n-grams features for training set (used for both bigrams and trigrams)

python3 ngrams_pre.py -p data -o ng2tr5

\# create n-grams features for testing set (used for both bigrams and trigrams)

python3 ngrams_pre.py -p data -o ng2te5 -v data/ng2tr5_vocab_5.txt    

\# create bigram and unigram features for training set

python3 uni_and_ngram_pre.py -p data -o ung2tr5

\# create bigram and unigram features for testing set

python3 uni_and_ngram_pre.py -p data -o ung2te5 -v data/ung2tr5_vocab_5.txt    





I ran the following to train and test my non-GCN ML models:

\# train and test baseline classifier (SVM with RBF kernel) with bag-of-words feature set

python3 svm_bow.py

\# train and test SVM classifier with linear kernel with bag-of-words feature set

python3 svm_bow_lin.py

\# train and test logistic regression classifier with bag-of-words feature set

python3 lr_bow.py

\# train and test random forest classifier with bag-of-words feature set

python3 rf_bow.py

\# train and test random forest classifier with bigram/trigram/unigram+bigram feature sets

python3 rf_ng.py


For the GCN classifier with a hyperlink graph structure, I ran the following commands:

\# crawl websites in dataset

sudo go run website_all_crawl.go

\# creates visualization of hyperlink graph structure

python3 visualization.py

\# create edges in hyperlink graph for GCN

python3 processLinks.py

\# train and test GCN with hyperlink graph structure

python3 link_pyg.py


For the GCN classifier with a tf-idf graph structure, I ran the following commands:

\# create tf-idf similarity matrix

python3 tfidf-pre.py

\# train and test GCN with tf-idf graph structure

python3 tfidf_pyg.py




I also ran these commands for further analysis:

\# calculate the average quantitative scores for the GCN trials

python3 compute_averages.py

\# find articles with specific features

python3 analyze_results.py  

