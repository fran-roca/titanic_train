import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from ..features.feature_engineering import feature_engineering
from app import cos


def make_dataset(path, timestamp, target, cols_to_remove, model_type='RandomForest'):

    """
        Function to create the dataset used for model training.

        Args:
           path (str):  Data path.
           timestamp (float):  Temporary representation in seconds.
           target (str):  Dependent variable to use.

        Kwargs:
           model_type (str): Type of model used.

        Returns:
           DataFrame, DataFrame. Train and test datasets for the model.
    """

    print('---> Getting data')
    df = get_raw_data_from_local(path)
    print('---> Train / test split')
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=50)
    print('---> Transforming data')
    train_df, test_df = transform_data(train_df, test_df, timestamp, target, cols_to_remove)
    print('---> Feature engineering')
    train_df, test_df = feature_engineering(train_df, test_df)
    print('---> Preparing data for training')
    train_df, test_df = pre_train_data_prep(train_df, test_df, model_type, timestamp, target)

    return train_df.copy(), test_df.copy()


def get_raw_data_from_local(path):

    """
        Function to get the original data from local

        Args:
           path (str):  Data path.

        Returns:
           DataFrame. Dataset with the input data.
    """

    df = pd.read_csv(path)
    return df.copy()


def transform_data(train_df, test_df, timestamp, target, cols_to_remove):

    """
        Function that allows performing the first transformation tasks
        of input data.

        Args:
           train_df (DataFrame):  Train dataset.
           test_df (DataFrame):  Test dataset.
           timestamp (float):  Temporary representation in seconds.
           target (str):  Dependent variable to use.
           cols_to_remove (list): Columns to remove.

        Returns:
           DataFrame, DataFrame. Train and test datasets for the model.
    """

    # Removing unusable columns
    print('------> Removing unnecessary columns')
    train_df = remove_unwanted_columns(train_df, cols_to_remove)
    test_df = remove_unwanted_columns(test_df, cols_to_remove)

    # Removing null values in the target variable
    print('------> Removing missing targets')
    train_df = remove_missing_targets(train_df, target)
    test_df = remove_missing_targets(test_df, target)

    # Type change
    train_df['Pclass'] = train_df['Pclass'].astype(str)
    test_df['Pclass'] = test_df['Pclass'].astype(str)


    # We separate the target variable before encoding
    train_target = train_df[target].copy()
    test_target = test_df[target].copy()
    train_df.drop(columns=[target], inplace=True)
    test_df.drop(columns=[target], inplace=True)

    # Generation of dummies
    print('------> Encoding data')
    train_df = pd.get_dummies(train_df)
    test_df = pd.get_dummies(test_df)
    # alineación de train y test para tener las mismas columnas
    train_df, test_df = train_df.align(test_df, join='inner', axis=1)

    # Saving the resulting columns to IBM COS
    print('---------> Saving encoded columns')
    cos.save_object_in_cos(train_df.columns, 'encoded_columns', timestamp)

    #"we rejoin the target variable to the datasets
    train_df.reset_index(drop=True, inplace=True)
    test_df.reset_index(drop=True, inplace=True)
    train_target.reset_index(drop=True, inplace=True)
    test_target.reset_index(drop=True, inplace=True)
    train_df = train_df.join(train_target)
    test_df = test_df.join(test_target)

    return train_df.copy(), test_df.copy()


def pre_train_data_prep(train_df, test_df, model_type, timestamp, target):
    """
       Function that performs the last transformations on the data
       before training (null imputation and scaling)

        Args:
           train_df (DataFrame):  Train dataset.
           test_df (DataFrame):  Test dataset.
           model_type (str):  Type of model used.
           timestamp (float):  Temporary representation in seconds.
           target (str):  Dependent variable to use.

        Returns:
           DataFrame, DataFrame. Datasets de train y test para el modelo.
    """

    # Separamos la variable objetivo antes de la imputación y escalado
    train_target = train_df[target].copy()
    test_target = test_df[target].copy()
    train_df.drop(columns=[target], inplace=True)
    test_df.drop(columns=[target], inplace=True)

    # imputación de nulos
    print('------> Inputing missing values')
    train_df, test_df = input_missing_values(train_df, test_df, timestamp)

    # restringimos el escalado solo a ciertos modelos
    if model_type.upper() in ['SVM', 'KNN', 'NaiveBayes']:
        print('------> Scaling features')
        train_df, test_df = scale_data(train_df, test_df)

    # volvemos a unir la variable objetivo a los datasets
    train_df.reset_index(drop=True, inplace=True)
    test_df.reset_index(drop=True, inplace=True)
    train_target.reset_index(drop=True, inplace=True)
    test_target.reset_index(drop=True, inplace=True)
    train_df = train_df.join(train_target)
    test_df = test_df.join(test_target)

    return train_df.copy(), test_df.copy()


def input_missing_values(train_df, test_df, timestamp):
    """
        Función para la imputación de nulos

        Args:
           train_df (DataFrame):  Dataset de train.
           test_df (DataFrame):  Dataset de test.
           timestamp (float):  Temporary representation in seconds.

        Returns:
           DataFrame, DataFrame. Train and test datasets for the model.
    """
    # we create the imputer that will use the median as a substitute
    imputer = SimpleImputer(strategy='median')

    # we adjust the medians based on the train data
    train_df = pd.DataFrame(imputer.fit_transform(train_df), columns=train_df.columns)
    # we impute the test data
    test_df = pd.DataFrame(imputer.transform(test_df), columns=test_df.columns)

    # we save the imputator for future new data
    print('------> Saving imputer on the cloud')
    cos.save_object_in_cos(imputer, 'imputer', timestamp)

    return train_df.copy(), test_df.copy()


def remove_unwanted_columns(df, cols_to_remove):
    """
        Function to remove unnecessary variables

        Args:
           df (DataFrame):  Dataset.

        Returns:
           DataFrame. Dataset.
    """
    return df.drop(columns=cols_to_remove)


def remove_missing_targets(df, target):
    """
        Function to remove null values in the target variable

        Args:
           df (DataFrame):  Dataset.

        Returns:
           DataFrame. Dataset.
    """
    return df[~df[target].isna()].copy()


def scale_data(train_df, test_df):
    """
        Variable scaling function

        Args:
           train_df (DataFrame):  Train dataset.
           test_df (DataFrame):  Test dataset.

        Returns:
           DataFrame, DataFrame. Train and test datasets for the model.
    """

    # scaling object in range (0,1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    # fit and transform on train data
    train_df = scaler.fit_transform(train_df)
    # test data scaling
    test_df = scaler.transform(test_df)

    return train_df.copy(), test_df.copy()


