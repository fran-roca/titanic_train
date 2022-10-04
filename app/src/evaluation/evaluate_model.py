from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import pandas as pd
from datetime import datetime


def evaluate_model(model, X_test, y_test, timestamp, model_name):
    """
        This function allows you to perform an evaluation of the trained model
        and create a dictionary with all the relevant information about it

        Args:
           model (sklearn-object):  Trained model object.
           X_test (DataFrame): Independent variables in test.
           y_test (Series):  Dependent variable in test.
           timestamp (float):  Temporary representation in seconds.
           model_name (str):  Model name

        Returns:
           dict. Dictionary with model info
    """

    # get predictions using the trained model
    y_pred = model.predict(X_test)

    # extract the importance of variables
    feature_importance_values = model.feature_importances_

    # Variable names
    features = list(X_test.columns)
    
    # creation of the model info dictionary
    model_info = {}
    #fi_df = pd.DataFrame({'feature': features, 'importance': feature_importance_values})

    # model overview
    model_info['_id'] = 'model_' + str(int(timestamp))
    model_info['name'] = 'model_' + str(int(timestamp))
    # training date (dd/mm/YY-H:M:S)
    model_info['date'] = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    model_info['model_used'] = model_name
    # objects used in the model (encoders, imputer)
    model_info['objects'] = {}
    model_info['objects']['encoders'] = 'encoded_columns_'+str(int(timestamp))
    model_info['objects']['imputer'] = 'imputer_' + str(int(timestamp))
    # used metrics
    model_info['model_metrics'] = {}
    # model_info['model_metrics']['feature_importances'] = dict(zip(fi_df.area, fi_df.importance))
    model_info['model_metrics']['confusion_matrix'] = confusion_matrix(y_test, y_pred).tolist()
    model_info['model_metrics']['accuracy_score'] = accuracy_score(y_test, y_pred)
    model_info['model_metrics']['precision_score'] = precision_score(y_test, y_pred)
    model_info['model_metrics']['recall_score'] = recall_score(y_test, y_pred)
    model_info['model_metrics']['f1_score'] = f1_score(y_test, y_pred)
    model_info['model_metrics']['roc_auc_score'] = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    # model status (in production or not)
    model_info['status'] = "none"

    return model_info



