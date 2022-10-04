from ..data.make_dataset import make_dataset
from ..evaluation.evaluate_model import evaluate_model
from app import ROOT_DIR, cos, client
from sklearn.ensemble import RandomForestClassifier
from cloudant.query import Query
import time


def training_pipeline(path, model_info_db_name='titanic_db'):
    """
        Function to manage the complete training pipeline
        of the model.

        Args:
            path (str):  Data path.

        Kwargs:
            model_info_db_name (str):  database to store
            the model info.
    """

    # Loading training settings
    model_config = load_model_config(model_info_db_name)['model_config']
    # Dependent variable to use
    target = model_config['target']
    # Columns to remove
    cols_to_remove = model_config['cols_to_remove']

    # timestamp used to version the model and objects
    ts = time.time()

    # loading and transformation of train and test data
    train_df, test_df = make_dataset(path, ts, target, cols_to_remove)

    # split of independent and dependent variables
    y_train = train_df[target]
    X_train = train_df.drop(columns=[target]).copy()
    y_test = test_df[target]
    X_test = test_df.drop(columns=[target]).copy()

    # model definition (Random Forest)
    model = RandomForestClassifier(n_estimators=model_config['n_estimators'],
                                   max_features=model_config['max_features'],
                                   random_state=50,
                                   n_jobs=-1)

    print('---> Training a model with the following configuration:')
    print(model_config)

    # Fitting the model with the training data
    model.fit(X_train, y_train)

    # saving the modil in IBM COS
    print('------> Saving the model {} object on the cloud'.format('model_'+str(int(ts))))
    save_model(model, 'model',  ts)

    # Evaluation of the model and collection of relevant information
    print('---> Evaluating the model')
    metrics_dict = evaluate_model(model, X_test, y_test, ts, model_config['model_name'])

    # Save the information of the model in the documentary database
    print('------> Saving the model information on the cloud')
    info_saved_check = save_model_info(model_info_db_name, metrics_dict)

    # Model info save check
    if info_saved_check:
        print('------> Model info saved SUCCESSFULLY!!')
    else:
        if info_saved_check:
            print('------> ERROR saving the model info!!')

    # Selection of the best model for production
    print('---> Putting best model in production')
    put_best_model_in_production(metrics_dict, model_info_db_name)


def save_model(obj, name, timestamp, bucket_name='deposittitanic'):
    """
        Function to save the model in IBM COS

        Args:
            obj (sklearn-object): Trained model object.
            name (str):  Object name to use in saving.
            timestamp (float):  Temporary representation in seconds.

        Kwargs:
            bucket_name (str):  IBM COS repository to use.
    """
    cos.save_object_in_cos(obj, name, timestamp)


def save_model_info(db_name, metrics_dict):
    """
        Function to save model info in IBM Cloudant

        Args:
            db_name (str):  Database name.
            metrics_dict (dict):  Model info.

        Returns:
            boolean. Check if the document has been created.
    """
    db = client.get_database(db_name)
    client.create_document(db, metrics_dict)

    return metrics_dict['_id'] in db


def put_best_model_in_production(model_metrics, db_name):
    """
        Function to put the best model into production.

        Args:
            model_metrics (dict):  Model info.
            db_name (str):  Database info.
    """

    # connection to the chosen database
    db = client.get_database(db_name)
    # query to bring the document with the info of the model in production
    query = Query(db, selector={'status': {'$eq': 'in_production'}})
    res = query()['docs']
    #  id of the model in production
    best_model_id = model_metrics['_id']

    # in case there is a model in production
    if len(res) != 0:
        # a comparison is made between the trained model and the model in production
        best_model_id, worse_model_id = get_best_model(model_metrics, res[0])
        # the worst model (between both) is marked as "NOT in production"
        worse_model_doc = db[worse_model_id]
        worse_model_doc['status'] = 'none'
        # the markup in the DB is updated
        worse_model_doc.save()
    else:
        # first trained model automatically goes to production
        print('------> FIRST model going in production')

    # the best model is marked as "YES in production"
    best_model_doc = db[best_model_id]
    best_model_doc['status'] = 'in_production'
    # the markup in the DB is updated
    best_model_doc.save()


def get_best_model(model_metrics1, model_metrics2):
    """
        Function to compare models.

        Args:
            model_metrics1 (dict):  First model info.
            model_metrics2 (str):  Second model info.

        Returns:
            str, str. Ids of the best and worst model in the comparison.
    """

    # model comparison using the AUC score metric.
    auc1 = model_metrics1['model_metrics']['roc_auc_score']
    auc2 = model_metrics2['model_metrics']['roc_auc_score']
    print('------> Model comparison:')
    print('---------> TRAINED model {} with AUC score: {}'.format(model_metrics1['_id'], str(round(auc1, 3))))
    print('---------> CURRENT model in PROD {} with AUC score: {}'.format(model_metrics2['_id'], str(round(auc2, 3))))

    # the order of the output should be (best model, worst model)
    if auc1 >= auc2:
        print('------> TRAINED model going in production')
        return model_metrics1['_id'], model_metrics2['_id']
    else:
        print('------> NO CHANGE of model in production')
        return model_metrics2['_id'], model_metrics1['_id']


def load_model_config(db_name):
    """
        Function to load model info from IBM Cloudant.

        Args:
            db_name (str):  Database name.

        Returns:
            dict. Document with model configuration.
    """
    db = client.get_database(db_name)
    query = Query(db, selector={'_id': {'$eq': 'titanic_config'}})
    return query()['docs'][0]
