# -*- coding: utf-8 -*-
"""Core_M2_Week_4_Part_1_Alex_Twenji_IP.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1O_s53NSbZgHGzbgTKFCoboGdabhc2Fq0

# DEFINING THE QUESTION

### a) Specifying the Question

This week's project requires us to implement a K-nearest neighbor (kNN) classifier and calculate the resulting metrics: We will be trying to Determine the Survivors using the features in the dataset

---

## b) Defining the Metric for Success

Being able to accurately predict survivors from the test set.

---

## c) Understanding the context

The RMS Titanic, a luxury steamship, sank in the early hours of April 15, 1912, off the coast of Newfoundland in the North Atlantic after sideswiping an iceberg during its maiden voyage. Of the 2,240 passengers and crew on board, more than 1,500 lost their lives in the disaster. Titanic has inspired countless books, articles and films (including the 1997 “Titanic” movie starring Kate Winslet and Leonardo DiCaprio), and the ships story has entered the public consciousness as a cautionary tale about the perils of human hubris.

---

## d) Experimental Design

1. Read and explore the given datasets.
2. Find and deal with outliers, anomalies, and missing data within the dataset.
3. Perform univariate and bivariate analysis recording your observations.
4. Perform Exploratory Data Analysis.
5. Perforn KNN On Train Set
6. Challenge your solution by providing insights on how you can make improvements in model improvement.
7. Predictions on Test Set with best model.
8. Provide a recommendation based on your analysis. 
 
---

# DATA PREPARATION
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy as sp

# %matplotlib inline

from sklearn import preprocessing

train = pd.read_csv('/content/train_week_9.csv')
test = pd.read_csv('/content/test _week_9.csv')

train.head()

test.head()

train.shape, test.shape

train.info(), test.info()

"""# DATA CLEANING

## Numerical Columns
"""

train.head()

test.head()

train_numeric = ['PassengerId','Survived','Pclass','Age','SibSp','Parch','Fare']
test_numeric = ['PassengerId','Pclass','Age','SibSp','Parch','Fare']

print('Train Set: \n')
for i, col_val in enumerate(train_numeric):
  print(col_val, train[col_val].isnull().sum())

print('\n')
print('Test Set: \n')
for i, col_val in enumerate(test_numeric):
  print(col_val, test[col_val].isnull().sum())

# We can see that the age columns have a lot of missing values, and only 1 fare value 
# is missing in the test set.

age_train = (177/train.shape[0]) * 100
age_test = (86/test.shape[0]) * 100
fare_test = (1/test.shape[0]) * 100
print(age_train, age_test, fare_test)

# We can comfortably drop that missing fare row on the test dataset,
# However, we have to deal with the missing age values.

train.Age.mean(), train.Age.median(), train.Age.mode()

# Since the age group is within a similar range for all central tendancy measures,
# We can use any of them to fill in the missing data.

test.Age.mean(), test.Age.median(), test.Age.mode()

# Although a little more varied, the age group is that of the young adults:
# A young adult is generally a person ranging in age from their early twenties to their thirties
# Since it's the same age-group as the train set, and the train set has more data, we'll use 
# the same metric we used for the train set.

# We decided to use the modes

train['Age'] = train['Age'].fillna(24)
test['Age'] = test['Age'].fillna(21)

print('Train Set: \n')
for i, col_val in enumerate(train_numeric):
  print(col_val, train[col_val].isnull().sum())

print('\n')
print('Test Set: \n')
for i, col_val in enumerate(test_numeric):
  print(col_val, test[col_val].isnull().sum())

# Next we'll get rid of the missing Fare value.

test = test[~(test.Fare.isna())]
test.Fare.isna().sum()

"""## Non-Numeric Columns"""

train.info()

# We'll not use the Name and Ticket columns, since they are each unique in our analysis, so we can focus on 
# Sex, Cabin and Embarked

test.info()

# We'll not use the Name and Ticket columns, since they are each unique in our analysis, so we can focus on 
# Sex, Cabin and Embarked

train.drop(columns=['Name','Ticket'], inplace= True)
test.drop(columns=['Name','Ticket'], inplace= True)

train = train.fillna('unknown')
train[train == 'unknown'].count()

train_cabin_unknown = (687 / train.shape[0]) * 100
train_embarked_unknown = (2/train.shape[0]) * 100

train_cabin_unknown, train_embarked_unknown

# There are too many unknowns in the Cabin column so we'll have to drop this column.
# For the Embarked column, we'll only drop the 2 rows with null values.

test = test.fillna('unknown')
test[test == 'unknown'].count()

test_cabin_unknown = (326 / train.shape[0]) * 100
test_cabin_unknown

# The values missing are also a lot so we'll have to drop the cabin column in the 
# test dataset as well. This is justified since our training data will not include 
# this column as well.

train.drop(columns=['Cabin'], inplace= True)
test.drop(columns=['Cabin'], inplace= True)

train = train[train.Embarked != 'unknown']

"""The Dataset is now relatively clean

# DATA ANALYSIS

## UNIVARIATE ANALYSIS

### a) Train Dataset
"""

train.info()

# We'll analyze the Numerical columns

train_numeric = ['PassengerId','Survived','Pclass','Age','SibSp','Parch','Fare']

fig, ax = plt.subplots(len(train_numeric), figsize= (8,40))

for i, col_val in enumerate(train_numeric):
  sns.boxplot(y = train[col_val], ax= ax[i])
  ax[i].set_title('Box plot - {}'.format(col_val), fontsize= 10)
  ax[i].set_xlabel(col_val, fontsize= 8)
plt.show()

# We can see that apart from PassengerId, Survived and Pclass, all the other numeric
# columns have outliers.

Quantile_1 = train.quantile(.25)
Quantile_3 = train.quantile(.75)
IQR_values = Quantile_3 - Quantile_1

anomalies = ((train < Quantile_1 - 1.5* IQR_values) | (train > Quantile_3 + 1.5 * IQR_values)).sum()
anomalies

percent_anomalies = (anomalies.sum() / train.shape[0])*100
percent_anomalies

"""The outliers seem like reasonable data that cannot be removed as this would affect the analysis, since the rows involved are roughly 49% of the data.

---

### b) Test Dataset
"""

test.info()

test_numeric = ['PassengerId','Pclass','Age','SibSp','Parch','Fare']

fig, ax = plt.subplots(len(test_numeric), figsize= (8,40))

for i, col_val in enumerate(test_numeric):
  sns.boxplot(y = test[col_val], ax= ax[i])
  ax[i].set_title('Box plot - {}'.format(col_val), fontsize= 10)
  ax[i].set_xlabel(col_val, fontsize= 8)
plt.show()

# We can see that apart from PassengerId and Pclass, all the other numeric
# columns have outliers.

Quantile_1 = test.quantile(.25)
Quantile_3 = test.quantile(.75)
IQR_values = Quantile_3 - Quantile_1

anomalies = ((test < Quantile_1 - 1.5* IQR_values) | (test > Quantile_3 + 1.5 * IQR_values)).sum()
anomalies

percent_anomalies = (anomalies.sum() / test.shape[0])*100
percent_anomalies

"""The outliers seem like reasonable data that cannot be removed as this would affect the analysis, since the rows involved are roughly 42% of the data.

---

### c) Univariate Analysis Recommendation

The anomalies look like reasonable data that could be due to some skewness in the data. This will further be investigated in the Bivariate Analysis amd Summary statistics sections.

---

## BIVARIATE ANALYSIS

### a) Train Dataset
"""

train.info()

sns.pairplot(train)

# PassengerId is a unique identifier that can be dropped

train = train.drop(columns= ['PassengerId'])

plt.figure(figsize=(20,10))
sns.heatmap(train.corr(), annot= True)

"""We can see that there are no variables that are highly correlated.

---

### b) Test Dataset
"""

test.info()

sns.pairplot(test)

# PassengerId is a unique identifier that can be dropped

test = test.drop(columns= ['PassengerId'])

plt.figure(figsize=(20,10))
sns.heatmap(test.corr(), annot= True)

"""We can see that there are no variables that are highly correlated.

----

### c) Bivariate Analysis Recommendation

The lack of highly correlated variables indicates poor multicolinearity among the variables, which will be good when it comes to machine learning modeling.

---

## SUMMARY STATISTICS

### a) Train Dataset
"""

train.describe()

# Central Tendancies

# mean

train_numeric = ['Survived','Pclass','Age','SibSp','Parch','Fare']

for i, col_val in enumerate(train_numeric):
  print('The mean of ' + str(col_val) + ' is ' + str(train[col_val].mean()))

# median

for i, col_val in enumerate(train_numeric):
  print('The median of ' + str(col_val) + ' is ' + str(train[col_val].median()))

# mode

for i, col_val in enumerate(train_numeric):
  print('The mode of ' + str(col_val) + ' is ' + str(train[col_val].mode()))

# The modes are unimodal showing that the data was gathered from the same population.

# range

for i, col_val in enumerate(train_numeric):
  print('The range of ' + str(col_val) + ' is ' + str(train[col_val].max()-train[col_val].min()))

# standard deviation

for i, col_val in enumerate(train_numeric):
  print('The deviation of ' + str(col_val) + ' is ' + str(train[col_val].std()))

# variables with higher range showcase higher standard deviation from the mean.

# variance

for i, col_val in enumerate(train_numeric):
  print('The variance of ' + str(col_val) + ' is ' + str(train[col_val].var()))

# As expected, variables with higher standard deviation, also have higher variance.

# skewness

for i, col_val in enumerate(train_numeric):
  print('The skewness of ' + str(col_val) + ' is ' + str(train[col_val].skew()))

# Only Pclass has negative skewness.

# kurtosis

for i, col_val in enumerate(train_numeric):
  print('The kurtosis of ' + str(col_val) + ' is ' + str(train[col_val].kurt()))

# Only Survived and Pclass have negative kurtosis

"""Survived and Pclass are showcasing a plutokurptic tendency with left-skewed data.

---

### b) Test Dataset
"""

test.describe()

# Central Tendancies

# mean

test_numeric = ['Pclass','Age','SibSp','Parch','Fare']

for i, col_val in enumerate(test_numeric):
  print('The mean of ' + str(col_val) + ' is ' + str(test[col_val].mean()))

# median

for i, col_val in enumerate(test_numeric):
  print('The median of ' + str(col_val) + ' is ' + str(test[col_val].median()))

# mode

for i, col_val in enumerate(test_numeric):
  print('The mode of ' + str(col_val) + ' is ' + str(test[col_val].mode()))

# The modes are unimodal showing that the data was gathered from the same population.

# range

for i, col_val in enumerate(test_numeric):
  print('The range of ' + str(col_val) + ' is ' + str(test[col_val].max()-test[col_val].min()))

# standard deviation

for i, col_val in enumerate(test_numeric):
  print('The deviation of ' + str(col_val) + ' is ' + str(test[col_val].std()))

# variables with higher range showcase higher standard deviation from the mean.

# variance

for i, col_val in enumerate(test_numeric):
  print('The variance of ' + str(col_val) + ' is ' + str(test[col_val].var()))

# As expected, variables with higher standard deviation, also have higher variance.

# skewness

for i, col_val in enumerate(test_numeric):
  print('The skewness of ' + str(col_val) + ' is ' + str(test[col_val].skew()))

# Only Pclass has negative skewness.

# kurtosis

for i, col_val in enumerate(test_numeric):
  print('The kurtosis of ' + str(col_val) + ' is ' + str(test[col_val].kurt()))

# Only Pclass has negative kurtosis

"""Pclass is showcasing a plutokurptic tendency with left-skewed data.

---

### c) Summary Stats Recommendation

Most of the skewness of the data is positive, indicating a mostly positively skewed dataset on most variables. This means that most distributions have longer tails to the right i.e. right-skewed / leptokurtic. Same goes for kurtosis as The data has mostly positive kurtosis indicating that most variables distributions have heavier tails and taller peaks than the normal distribution.

---

## EXPLORATORY DATA ANALYSIS

### Train Dataset
"""

train.info()

train['Age'].hist(bins = 10)

# As expected, most of the people are between 20 and 30 years old

train_survive = train[train.Survived == 1]

train_survive['Age'].hist(bins=10)

# Most of those who aurvived are also in the same age group.

train_survive['Fare'].hist(bins=10)

# Most of the survivors had paid a lower fee.

train['Fare'].hist(bins = 10)

# However, in total there were a lot more people who paid the lower fares.

"""### Test Dataset"""

test.info()

test['Age'].hist(bins = 10)

# As expected, most of the people are between 20 and 30 years old

test['Fare'].hist(bins = 10)

# Most of the people paid the lower fares.

"""# MODELING

## PREPARATION
"""

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix

train.info()

le = preprocessing.LabelEncoder()
train.Sex = le.fit_transform(train.Sex)
train.Embarked = le.fit_transform(train.Embarked)
train.info()

X = train.drop(columns=['Survived'])
y = train.Survived

"""## 80:20 Model Split"""

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state= 10)

scaler = StandardScaler()
scaler.fit(X_train)

X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

error = []

# Calculating error for K values between 1 and 20

for i in range(1, 21):
    knn = KNeighborsClassifier(n_neighbors=i)
    knn.fit(X_train, y_train)
    pred_i = knn.predict(X_test)
    error.append(np.mean(pred_i != y_test))

# Plotting the above

plt.figure(figsize=(12, 6))
plt.plot(range(1, 21), error, color='red', linestyle='dashed', marker='o',
         markerfacecolor='blue', markersize=10)
plt.title('Error Rate K Value')
plt.xlabel('K Value')
plt.ylabel('Mean Error')

# From below we can see that the best K values are 10 and 12

# using KNN of 10

clf = KNeighborsClassifier(n_neighbors= 10)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

# using KNN of 12

clf = KNeighborsClassifier(n_neighbors= 12)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Results are similar to KNN of 10, therefore we can use either.

"""## 70:30 Model Split"""

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state= 10)

scaler = StandardScaler()
scaler.fit(X_train)

X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

error = []

# Calculating error for K values between 1 and 20

for i in range(1, 21):
    knn = KNeighborsClassifier(n_neighbors=i)
    knn.fit(X_train, y_train)
    pred_i = knn.predict(X_test)
    error.append(np.mean(pred_i != y_test))

# Plotting the above

plt.figure(figsize=(12, 6))
plt.plot(range(1, 21), error, color='red', linestyle='dashed', marker='o',
         markerfacecolor='blue', markersize=10)
plt.title('Error Rate K Value')
plt.xlabel('K Value')
plt.ylabel('Mean Error')

# From below we can see that the best K values is 9

# using KNN of 9

clf = KNeighborsClassifier(n_neighbors= 9)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Results are worse than the 80:20 split.

"""## 60:40 Model Split"""

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.40, random_state= 10)

scaler = StandardScaler()
scaler.fit(X_train)

X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

error = []

# Calculating error for K values between 1 and 20

for i in range(1, 21):
    knn = KNeighborsClassifier(n_neighbors=i)
    knn.fit(X_train, y_train)
    pred_i = knn.predict(X_test)
    error.append(np.mean(pred_i != y_test))

# Plotting the above

plt.figure(figsize=(12, 6))
plt.plot(range(1, 21), error, color='red', linestyle='dashed', marker='o',
         markerfacecolor='blue', markersize=10)
plt.title('Error Rate K Value')
plt.xlabel('K Value')
plt.ylabel('Mean Error')

# From below we can see that the best K values are 6 and 13

# using KNN of 6

clf = KNeighborsClassifier(n_neighbors=6)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

# using KNN of 13

clf = KNeighborsClassifier(n_neighbors= 13)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Results are the worst compared to the other splits.

"""## OPTIMIZING 80:20 MODEL

The 80:20 Model Split had the highest Precision, Recall and F1 score values with either KNN k values of 10 or 12. This is the model that we will ooptimize before making the predictions on our test dataset.
"""

from sklearn.model_selection import GridSearchCV

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state= 10)

scaler = StandardScaler()
scaler.fit(X_train)

X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

#List Hyperparameters that we want to tune.
n_neighbors = list(range(10,13))
p=[1,2]

#Convert to dictionary
hyperparameters = dict(n_neighbors=n_neighbors, p=p)

#Create new KNN object
clf_2 = KNeighborsClassifier()

#Use GridSearch
clf_2 = GridSearchCV(clf_2, hyperparameters, cv=5)

#Fit the model
best_model = clf_2.fit(X_train, y_train)
#Print The value of best Hyperparameters
print('Best leaf_size:', best_model.best_estimator_.get_params()['leaf_size'])
print('Best p:', best_model.best_estimator_.get_params()['p'])
print('Best n_neighbors:', best_model.best_estimator_.get_params()['n_neighbors'])

# Applying the above hyperparameters

optimized = KNeighborsClassifier(leaf_size=30,n_neighbors=12, p=1)
optimized.fit(X_train, y_train)

y_pred = optimized.predict(X_test)

print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

"""The Optimized Solution's performance is no better than the Original Model

# CONCLUSION

The precision informs us on the accuracy of the true positive predictions with regards to false positives. The recall informs us on the accuracy of the true positive predictions with regards to false negatives. The f1-score finds the best balance between precision and recall. For this challenge the best accuracy score to work with, in order to beat the accuracy paradox of the accuracy score is the f1-score. Using this, the 80:20 split Model is the best Model with KNN n_neighborhood values of either 10 or 12.

---

# CHALLENGING THE SOLUTION
"""

# To try improve the scores, we could try and improve the imbalance of the classes as
# indicated by the lower support values of class 1 in all models.

# import library
from imblearn.over_sampling import RandomOverSampler
from collections import Counter

ros = RandomOverSampler(random_state=42)

# fit predictor and target variablex_ros, 

x_ros, y_ros = ros.fit_resample(X, y)

print('Original dataset shape', Counter(y))
print('Resample dataset shape', Counter(y_ros))

X_train, X_test, y_train, y_test = train_test_split(x_ros, y_ros, test_size=0.20, random_state= 10)

scaler = StandardScaler()
scaler.fit(X_train)

X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

error = []

# Calculating error for K values between 1 and 20

for i in range(1, 21):
    knn = KNeighborsClassifier(n_neighbors=i)
    knn.fit(X_train, y_train)
    pred_i = knn.predict(X_test)
    error.append(np.mean(pred_i != y_test))

# Plotting the above

plt.figure(figsize=(12, 6))
plt.plot(range(1, 21), error, color='red', linestyle='dashed', marker='o',
         markerfacecolor='blue', markersize=10)
plt.title('Error Rate K Value')
plt.xlabel('K Value')
plt.ylabel('Mean Error')

# From below we can see that the best K values are 1 and 9

#List Hyperparameters that we want to tune.
n_neighbors = list(range(1,10))
p=[1,2]

#Convert to dictionary
hyperparameters = dict(n_neighbors=n_neighbors, p=p)

#Create new KNN object
clf_3 = KNeighborsClassifier()

#Use GridSearch
clf_3 = GridSearchCV(clf_3, hyperparameters, cv=5)

#Fit the model
best_model = clf_3.fit(X_train, y_train)
#Print The value of best Hyperparameters
print('Best leaf_size:', best_model.best_estimator_.get_params()['leaf_size'])
print('Best p:', best_model.best_estimator_.get_params()['p'])
print('Best n_neighbors:', best_model.best_estimator_.get_params()['n_neighbors'])

# Applying the above hyperparameters

challenge = KNeighborsClassifier(leaf_size=30,n_neighbors=1, p=1)
challenge.fit(X_train, y_train)

y_pred = challenge.predict(X_test)

print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

# This is the model with the best performance and we can use it to predict the test dataset

test.info()

test.Sex = le.fit_transform(test.Sex)
test.Embarked = le.fit_transform(test.Embarked)
test.info()

predict_unknown = challenge.predict(test)
test['Survived'] = predict_unknown
test.head()

"""# RECOMMENDATION

The Precision and Recall values of our 'challenge the solution' model are the best and this led to better f1-score values indicating that 84% of the Non=Survivors predictions were right, whereas 85% of the Survivors predictions were right. This improvement was due to the improvement in class balance as shown by the support values. Other methods of class imbalance correction should be further researched to see if the results can be improved. We can also notice that as the train split decreases the accuracy scores decrease, indicating the more the data for training, the better the results will be.

---

# FOLLOW UP QUESTIONS

## a) Did we have the right data?

Yes, as our accuracy scores were all above 80%

## b) Do we need other data to answer our question?

Yes, if we had the survived column with the test dataset, we could have checked if our predictions were accurate or if they were fitted to fit the train set

## c) Did we have the right question?

Yes, because the tale of the titanic and it's survivors is so ingrained in pop culture and has even been made into one of the best selling films of all time. It's therefore a good dataset to learn with
"""