<p align="center">
  <a href="" rel="noopener">
 <img width=720px height=400px src="https://drive.google.com/uc?export=view&id=18eA1_Z0zp6Bii4Im_jczZRhFrUwKeiZd" alt="Project logo - stable diffusion"></a>
</p>

<h1 align="center">Titanic train</h1>

<div align="center">

</div>

<p align="center"> This project has been designed to be the training system for the titanic project.
    <br> 
</p>

---

## 📝 Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Deployment](#deployment)
- [Usage](#usage)
- [Built Using](#built_using)
- [Authors](#authors)

## 🧐 About <a name = "about"></a>

Whit this project we are train to predict if someone is a survivor or not. Also we are train to cover all the steps needed to have a machine learning model in production. This project includes 2 modules, one for training and other for the inference. Titanic project has been configured to be deployed on [IBM Cloud](https://www.ibm.com/cloud) 

## 🏁 Getting Started <a name = "getting_started"></a>

### Prerequisites

- flask>=1.1.2
- pandas>=1.2.4
- scikit-learn>=0.24.2
- ibm-cos-sdk>=2.10.0
- cloudant>=2.14.0

### Installing

1. Clone the repo
   ```sh
   git clone https://github.com/fran-roca/titanic_train
   ```
2. Install NPM packages
   ```sh
   pip install -r requirements.txt
   ```
## 🎈 Usage <a name="usage"></a>

Once it is deployed, you can use postman to call to the endpoint (/train-model) and train the model, it will be saved in IBM Cloud if metrics are better than your current production model or if it's the first time you are running it.

## 🚀 Deployment <a name = "deployment"></a>

See more information about the IBM Cloud deployment in [IBM Cloud tutorials](https://developer.ibm.com/components/cloud-ibm/tutorials/)

## ⛏️ Built Using <a name = "built_using"></a>

- [IBM Cloudant](https://www.ibm.com/cloud/cloudant) - Database
- [Flask](https://flask.palletsprojects.com/) - Web Framework
- [Python](https://www.python.org/) - Programming language

## ✍️ Authors <a name = "authors"></a>

- [@fran-roca](https://github.com/fran-roca) - Idea & Initial work
