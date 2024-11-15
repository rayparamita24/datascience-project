# -*- coding: utf-8 -*-
"""bayesian_optimization.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1WhzdmKafZDhR2SckZmR9aUMz91ElpB3W
"""

# Commented out IPython magic to ensure Python compatibility.
# Commented out IPython magic to ensure Python compatibility.
get_ipython().system('wget https://raw.githubusercontent.com/Zahlii/colab-tf-utils/master/utils.py')
!pip install mxnet
!pip install bayesian-optimization

from utils import *

import time
import numpy as np
import pandas as pd

import datetime
import seaborn as sns

import matplotlib.pyplot as plt
# %matplotlib inline
from timeit import default_timer as timer
import math
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import xgboost as xgb
import warnings
warnings.filterwarnings("ignore")

import csv






# Modeling
import lightgbm as lgb

# Evaluation of the model
from sklearn.model_selection import KFold

MAX_EVALS =30
N_FOLDS = 10
import csv
import matplotlib.pyplot as plt
import seaborn as sns

# %matplotlib inline

from hyperopt import STATUS_OK


def parser(x):
    return datetime.datetime.strptime(x,'%d-%m-%Y')
dataset_ex_df = pd.read_csv('AIRTEL_LOCKDOWN1.csv', header=0, parse_dates=[0], date_parser=parser)
data=dataset_ex_df[['Date','Airtel','Nifty-50','Currency Change','MACD','ADX','RSI','William %R','CCI','Moneycontrol','Economics Times','Financial Express']]
y = data['Airtel']
X=data.iloc[:, 2:5]
train_samples = int(X.shape[0] * 0.65)
train = X.iloc[:train_samples]
test = X.iloc[train_samples:]
y_train = y.iloc[:train_samples]
y_test = y.iloc[train_samples:]
features = np.array(train)
test_features = np.array(test)
labels = y_train


def objective(params, n_folds = N_FOLDS):
    """Objective function for Gradient Boosting Machine Hyperparameter Optimization"""

    # Keep track of evals
    global ITERATION

    ITERATION += 1

    # Retrieve the subsample if present otherwise set to 1.0
    subsample = params['boosting_type'].get('subsample', 1.0)

    # Extract the boosting type
    params['boosting_type'] = params['boosting_type']['boosting_type']
    params['subsample'] = subsample

    # Make sure parameters that need to be integers are integers
    for parameter_name in ['num_leaves', 'subsample_for_bin', 'min_child_samples']:
        params[parameter_name] = int(params[parameter_name])

    start = timer()

    d_train = xgb.DMatrix( train, y_train)

# Running cross validation on your xgboost model
    cv_results = xgb.cv(params, d_train, nfold = n_folds, num_boost_round = 500,
                        early_stopping_rounds = 25, metrics = 'rmse', seed = 0)


    run_time = timer() - start

    # Extract the best score
    loss = min(cv_results['test-rmse-mean'])

    # Boosting rounds that returned the highest cv score
    n_estimators = int(np.argmin(cv_results['test-rmse-mean']) + 1)

    # Write to the csv file ('a' means append)
    of_connection = open(out_file, 'a')
    writer = csv.writer(of_connection)
    writer.writerow([loss, params, ITERATION, n_estimators, run_time])

    # Dictionary with information for evaluation
    return {'loss': loss, 'params': params, 'iteration': ITERATION,
            'estimators': n_estimators,
            'train_time': run_time, 'status': STATUS_OK}


from hyperopt import hp
from hyperopt.pyll.stochastic import sample
# Create the learning rate
learning_rate = {'learning_rate': hp.loguniform('learning_rate', np.log(0.005), np.log(0.2))}

learning_rate_dist = []

# Draw 10000 samples from the learning rate domain
for _ in range(10000):
    learning_rate_dist.append(sample(learning_rate)['learning_rate'])

plt.figure(figsize = (8, 6))
sns.kdeplot(learning_rate_dist, color = 'red', linewidth = 2, shade = True);
plt.title('Learning Rate Distribution', size = 18);
plt.xlabel('Learning Rate', size = 16); plt.ylabel('Density', size = 16);

# boosting type domain
boosting_type = {'boosting_type': hp.choice('boosting_type',
                                            [{'boosting_type': 'gbdt', 'subsample': hp.uniform('subsample', 0.5, 1)},
                                             {'boosting_type': 'dart', 'subsample': hp.uniform('subsample', 0.5, 1)},
                                             {'boosting_type': 'goss', 'subsample': 1.0}])}

# Draw a sample
params = sample(boosting_type)
# Retrieve the subsample if present otherwise set to 1.0
subsample = params['boosting_type'].get('subsample', 1.0)

# Extract the boosting type
params['boosting_type'] = params['boosting_type']['boosting_type']
params['subsample'] = subsample

# Define the search space
space = {
    'class_weight': hp.choice('class_weight', [None, 'balanced']),
    'boosting_type': hp.choice('boosting_type', [{'boosting_type': 'gbdt', 'subsample': hp.uniform('gdbt_subsample', 0.5, 1)},
                                                 {'boosting_type': 'dart', 'subsample': hp.uniform('dart_subsample', 0.5, 1)},
                                                 {'boosting_type': 'goss', 'subsample': 1.0}]),
    'num_leaves': hp.quniform('num_leaves', 30, 150, 1),
    'learning_rate': hp.loguniform('learning_rate', np.log(0.01), np.log(0.2)),
    'subsample_for_bin': hp.quniform('subsample_for_bin', 20000, 300000, 20000),
    'min_child_samples': hp.quniform('min_child_samples', 20, 500, 5),
    'reg_alpha': hp.uniform('reg_alpha', 0.0, 1.0),
    'reg_lambda': hp.uniform('reg_lambda', 0.0, 1.0),
    'colsample_bytree': hp.uniform('colsample_by_tree', 0.6, 1.0)
}
# Sample from the full space
x = sample(space)

# Conditional logic to assign top-level keys
subsample = x['boosting_type'].get('subsample', 1.0)
x['boosting_type'] = x['boosting_type']['boosting_type']
x['subsample'] = subsample

from hyperopt import tpe

# optimization algorithm
tpe_algorithm = tpe.suggest
from hyperopt import Trials

# Keep track of results
bayes_trials = Trials()
# File to save first results
out_file = 'gbm_trials.csv'
of_connection = open(out_file, 'w')
writer = csv.writer(of_connection)

# Write the headers to the file
writer.writerow(['loss', 'params', 'iteration', 'estimators', 'train_time'])
of_connection.close()

from hyperopt import fmin
# Global variable
global  ITERATION
ITERATION = 0
# Run optimization
best = fmin(fn = objective, space = space, algo = tpe.suggest, max_evals = MAX_EVALS, trials = bayes_trials)
# Sort the trials with lowest loss (highest AUC) first
bayes_trials_results = sorted(bayes_trials.results, key = lambda x: x['loss'])
bayes_trials_results[:2]
results = pd.read_csv('gbm_trials2.csv')
# Sort with best scores on top and reset index for slicing
results.sort_values('loss', ascending = True, inplace = True)



# Create a new dataframe for storing parameters
bayes_params = pd.DataFrame(columns = list(ast.literal_eval(results.loc[0, 'params']).keys()),
                            index = list(range(len(results))))

# Add the results with each parameter a different column
for i, params in enumerate(results['params']):
    bayes_params.loc[i, :] = list(ast.literal_eval(params).values())

bayes_params['loss'] = results['loss']
bayes_params['iteration'] = results['iteration']

df = pd.DataFrame(bayes_params)

# saving the dataframe
df.to_csv('bayes2.csv')