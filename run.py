from flask import Flask
import os
from app.src.models import train_model
from app import ROOT_DIR
import warnings

warnings.filterwarnings('ignore')

# Initialize app under Flask framework
app = Flask(__name__)

# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))


# Using the decorator @app.route to manage routers
# root path "/"
@app.route('/', methods=['GET'])
def root():
    """
        Function to manage the output of the root path.

        Returns:
           dict.  Output message
    """
    # We do not do anything. We only return info
    return {'Project':'Titanic - Train'}


# route to run the train pipeline
@app.route('/train-model', methods=['GET'])
def train_model_route():
    """
        Training pipeline launch function.

        Returns:
           dict.  Output message
    """
    # Path for local data upload
    df_path = os.path.join(ROOT_DIR, 'data/data.csv')

    # Run the training pipeline of our model
    train_model.training_pipeline(df_path)

    # Anything we want can be returned (training success message, metrics, etc.)
    return {'TRAINING_MODEL': 'Successfully trained'}


# main
if __name__ == '__main__':
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=True)
