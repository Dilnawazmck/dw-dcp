## **Text Analytics**

An analytics platform that uses NLP algorithms to provide insights from the survey data.
It uses python FastAPI framework at the backend to expose REST APIs and uses Postgres Database.
It uses React-Redux framework at the frontEnd to fetch REST APIs.

### **Requirements Backend**
1. Python 3.7.9
2. pip package manager
3. Nltk english stopwords
4. Gensim "glove-wiki-gigaword-300" package
5. Spacy "en_core_web_lg" package

### Instructions(Backend)

1. Clone the repo https://github.com/McK-Internal/OHI-Text_Analytics.git
    `git clone https://github.com/McK-Internal/OHI-Text_Analytics.git`
2. Go to project directory
    `$ cd OHI-Text_Analytics`
3. Create a virtual environment for the project and activate it 
    `$ python3 -m venv venv
     $ source venv/bin/activate`
4. Install all python dependencies
    `$ pip install -r requirements.txt
     $ python -m nltk.downloader stopwords
     $ python -m spacy download en_core_web_lg
     $ python -m gensim.downloader --download glove-wiki-gigaword-300`   
5. Create a .env file from a copy of env.sample inside backend directory
6. To run the project:
    `$ uvicorn app.main:app --host=0.0.0.0 --port=8000 --workers=8`
   
### To run tests
This project uses pytest.

```bash
pytest -v app/tests/
```

### To get coverage

```bash
 pytest --cov=app app/tests/
```
    
### **Requirements FrontEnd**
1. node `^5.0.0`
2. yarn package manager

### Instructions(FrontEnd)

1. Clone the repo https://github.com/McK-Internal/OHI-Text_Analytics_FE.git
    `git clone https://github.com/McK-Internal/OHI-Text_Analytics_FE.git`
2. Go to project directory/frontend
    `$ cd OHI-Text_Analytics_FE`
3. Install all frontEnd dependencies
    `$ yarn install`
4. Create a .env file from a copy of env.sample inside frontend directory
    `update the API path in .env file : REACT_APP_API_BASEPATH=http://apiPathToUse/api`
5. Create front-end build:
    `$ yarn build`
