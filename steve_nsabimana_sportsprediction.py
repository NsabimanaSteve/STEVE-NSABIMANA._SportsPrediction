# -*- coding: utf-8 -*-
"""STEVE_NSABIMANA_SportsPrediction (1) (1).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/138-bfgZeuHMdDL_01vhF6Ly-c1OjJBax

Importing all library and modules that will be used throughout the project
"""

import pandas as pd
import pickle
import os
import zipfile
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from xgboost import XGBRegressor
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, SGDRegressor, BayesianRidge, HuberRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor

from sklearn.ensemble import GradientBoostingRegressor, AdaBoostRegressor, RandomForestRegressor, ExtraTreesRegressor

"""Read the training dataset from the CSV file and store it in a DataFrame."""

dataset = pd.read_csv("C:\\Users\\user\\Downloads\\male_players (legacy).csv")
dataset.head()

"""Split dataset into numerical and categorical features."""

dataset.info()

numerical_features = dataset.select_dtypes(include=['int64', 'float64'])
categorical_features = dataset.select_dtypes(include=['object'])

numerical_features.head()

"""Drop numerical columns with over 30% missing values."""

numerical_features = numerical_features.dropna(thresh=0.7*len(numerical_features), axis=1)
numerical_features.head()

categorical_features.head()

"""Dropping columns with more than 30% missing values for the categorical features."""

categorical_features.info()


categorical_features = categorical_features.dropna(thresh=0.7*len(categorical_features), axis=1)
categorical_features.head()

"""Convert the `dob` column to `cat_age` and the `club_joined` column to `cat_years_in_club` by subtracting the respective years from the current year, as age and years in the club have more relational value than the years of birth and joining."""

categorical_features['dob'] = pd.to_datetime(categorical_features['dob'])
categorical_features['club_joined'] = pd.to_datetime(categorical_features['club_joined_date'])

categorical_features['cat_age'] = categorical_features['dob'].apply(lambda x: 2023 - x.year)
categorical_features['cat_years_in_club'] = categorical_features['club_joined'].apply(lambda x: 2023 - x.year)

categorical_features = categorical_features.drop(['dob', 'club_joined_date'], axis=1)
categorical_features.head()

"""Remove columns with over 90% unique values, as they do not offer learnable patterns for the model."""

mostly_unique = [col for col in categorical_features.columns if categorical_features[col].nunique() >= 0.9 * len(categorical_features)]
categorical_features = categorical_features.drop(mostly_unique, axis=1)
categorical_features.head()

# dissplay the columns start from column 9 to column 36
for col in categorical_features.columns[9:36]:
    categorical_features[col] = categorical_features[col].apply(lambda x: int(x) if isinstance(x, (int, float)) else x)

categorical_features.head()

"""Remove club_logo_url, club_flag_url and national_flag_url columns."""

columns_to_drop = ['club_logo_url', 'club_flag_url', 'nation_flag_url']
columns_to_keep = []

for col in columns_to_drop:
    if col in categorical_features.columns:
        columns_to_keep.append(col)

categorical_features = categorical_features.drop(columns_to_keep, axis=1)
categorical_features

"""Convert the remaining categorical features to numerical by factorizing."""

encodings_map  = {}

for col in categorical_features.select_dtypes(include=['object']).columns:
    encoded_values, unique_categories = pd.factorize(categorical_features[col])
    encodings_map[col] = dict(zip(unique_categories, encoded_values))
    categorical_features[col] = encoded_values

categorical_features.head()

"""Combine the numerical and categorical features to make one dataframe"""

dataset = pd.concat([numerical_features, categorical_features], axis=1)
dataset.head()

dataset.columns

"""Since age  calculated as (2023 - dob), we drop `age` feature from the dataset since `cat_age` accurately represents their current age."""

dataset = dataset.drop('age', axis=1)

"""Assess feature importance using the Random Forest Regressor."""

X = dataset.drop(['overall'], axis=1)
y = dataset['overall']

"""Imputing the missing values in the dataset by filling them with the mean of the column."""

X_imputed = X.fillna(X.mean())
y_imputed = y

X_imputed.shape, y_imputed.shape

import pandas as pd

X_imputed['club_joined'] = pd.to_datetime(X_imputed['club_joined'])

X_imputed['club_joined'] = X_imputed['club_joined'].astype('int64') // 10**9

imputedRegressor = RandomForestRegressor(n_estimators=100, random_state=42)
imputedRegressor.fit(X_imputed, y_imputed)

"""Showing the feature importance of the model in a dataframe format."""

imputed_feature_importances = pd.DataFrame(imputedRegressor.feature_importances_, index=X_imputed.columns, columns=['importance']).sort_values('importance', ascending=False)
imputed_feature_importances *= 100
imputed_feature_importances.head()

"""Retain only the important features for our X (independent variables)."""

y = y_imputed

X = imputed_feature_importances[imputed_feature_importances['importance'] > 1].index
X = X_imputed[X]
X.head()

X.describe()

"""Scaling the data using the StandardScaler."""

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

with open('scaler_model.pkl', 'wb') as file:
    pickle.dump(scaler, file)

X = pd.DataFrame(X_scaled, index=X.index, columns=X.columns)
X.describe()

"""Splitting the data for training and testing using the train_test_split function from sklearn."""

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
X_train.shape, y_train.shape, X_test.shape, y_test.shape

"""Training the models with 16 different regression models and comparing their performance"""

regression_models = {
    'RandomForestRegressor': RandomForestRegressor(n_estimators=100, random_state=42),
    'LinearRegression': LinearRegression(),
    'Ridge': Ridge(),
    'Lasso': Lasso(),
    'ElasticNet': ElasticNet(),
    'SGDRegressor': SGDRegressor(),
    'BayesianRidge': BayesianRidge(),
    'HuberRegressor': HuberRegressor(),
    'SVR': SVR(),
    'DecisionTreeRegressor': DecisionTreeRegressor(),
    'KNeighborsRegressor': KNeighborsRegressor(),
    'MLPRegressor': MLPRegressor(),
    'GradientBoostingRegressor': GradientBoostingRegressor(),
    'AdaBoostRegressor': AdaBoostRegressor(),
    'ExtraTreesRegressor': ExtraTreesRegressor(),
    'XGBRegressor': XGBRegressor()
}

mse = {}
mae = {}
r2 = {}

for name, model in regression_models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse[name] = mean_squared_error(y_test, y_pred)
    mae[name] = mean_absolute_error(y_test, y_pred)
    r2[name] = r2_score(y_test, y_pred)

"""Converting perfomance data into a dataframe"""

accuracy = pd.DataFrame([mse, mae, r2], index=['MSE', 'MAE', 'R2']).T
accuracy = accuracy.sort_values('R2', ascending=False)
accuracy

"""Plot the accuracy of the models"""

plt.figure(figsize=(20, 10))
plt.plot(accuracy['MSE'], label='MSE')
plt.plot(accuracy['MAE'], label='MAE')
plt.plot(accuracy['R2'], label='R2')
plt.xticks(rotation=90)
plt.legend()
plt.show()

"""Given that the Random Forest Regressor shows the lowest mean absolute error and the highest R2 score, we will proceed with this algorithm. Next, we need to optimize the model's hyperparameters for optimal performance and train it on the entire training dataset.

Training the model using the best parameters and the entire training dataset.
"""

from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
from scipy.stats import randint, uniform

param_dist = {
    'n_estimators': randint(100, 200),
    'max_depth': [None, 5],
    'min_samples_split': randint(2, 5),
    'min_samples_leaf': randint(1, 5),
    'max_features': ['sqrt', 'log2']
}

random_search = RandomizedSearchCV(
    estimator=RandomForestRegressor(random_state=42),
    param_distributions=param_dist,
    n_iter=10,
    cv=5,
    random_state=42,
    n_jobs=-1,
    verbose=1
)

X = pd.concat([X_train, X_test])
y = pd.concat([y_train, y_test])


random_search.fit(X, y)

print(random_search.best_params_)

"""Read the test dataset from the CSV file and store it in a DataFrame."""

model_with_best_params = RandomForestRegressor(max_depth=20, max_features='sqrt', min_samples_leaf=1, min_samples_split=2, n_estimators=500, n_jobs=-1, random_state=42)
model_with_best_params.fit(X, y)

test_data = pd.read_csv("C:\\Users\\user\\Downloads\\players_22.csv")
test_data.head()

"""Compute the current age of the players in the test dataset, which corresponds to the cat_age feature in the training dataset."""

test_data['cat_age'] = 2023 - pd.to_datetime(test_data.dob).dt.year
test_data.cat_age.head()

"""Create a subset of the data containing only the columns used for training the model."""

needed_columns = ['value_eur','release_clause_eur','cat_age','potential','movement_reactions']
test_features = test_data[needed_columns]
test_features.head()

test_features.info()

test_overall = test_data.overall
test_overall.head()

"""Fill in the missing values in the dataset by replacing them with the mean value of each respective column."""

test_features = test_features.fillna(test_features.mean())

test_features.head()

"""Scale the data using the previously saved StandardScaler object."""

with open('scaler_model.pkl', 'rb') as file:
    loaded_scaler = pickle.load(file)  # Load the saved scaler
test_features = loaded_scaler.transform(test_features)

"""Predicting the overall rating of the players in the test dataset."""

y_predicion = model_with_best_params.predict(test_features)
y_predicion

"""Printing the metrics of the model."""

mae = mean_absolute_error(test_overall, y_predicion)
r2 = r2_score(test_overall, y_predicion)
mse = mean_squared_error(test_overall, y_predicion)

print(f'MAE: {mae}')
print(f'R2: {r2}')
print(f'MSE: {mse}')

"""Visualize the actual and predicted values to observe their correlation by using graph(by plotting )"""

plt.figure(figsize=(20, 10))
plt.plot(test_overall, label='Actual')
plt.plot(y_pred, label='Predicted')
plt.xlabel('Player')
plt.ylabel('Overall')
plt.legend()
plt.show()

comparison = pd.DataFrame({'Actual': test_overall, 'Predicted': y_pred})
comparison.tail(10)

"""The model achieves an excellent R2 score of 0.978 and a very low mean absolute error of 0.69.

Saving the model for deployment in the web app using pickle.
"""

with open('model.pkl', 'wb') as f:
    pickle.dump(model_with_best_params, f)

"""To reduce its size to less than 100MB for uploading to GitHub, we will compress the large raw model (over 300MB) using gzip."""

zip_filename = "model.zip"
model_filename = "model.pkl"

with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as archive:
    archive.write(model_filename)

print(f"{model_filename} has been zipped to {zip_filename}")

"""Deleting the raw model to save space."""

file_path = 'model.pkl'

if os.path.exists(file_path):
    os.remove(file_path)
    print(f"{file_path} has been removed")









