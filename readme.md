Project build using FastAPI to scrape [https://dentalstall.com/shop/](https://dentalstall.com/shop/)

### Prerequisite
Python 3.11.0 


### Project Specifications
Framework - FastApi <br/>
In memory database - Redis <br/>
Using requests library for scraping for this project (note - if project can comprise performance than selenium should be used here as website is using javascript)

### How to run project?
1. Download project
2. (Recommended but not mandatory) Create virtual invironment
> pipenv shell # or via any other method
3. Install dependencies (make sure you are in currect directory which is base directory)
> pip install -r requirements.txt
4. Run server
> uvicorn main:app --reload

