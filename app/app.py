import pandas as pd
from flask import Flask, jsonify, render_template, request

from utils import get_confg, get_sql_conn, carviews
from searches import Search

import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")


app = Flask(__name__)
config_path = '../app/schema/app.conf'
config = get_confg(config_path)

search = Search(config=config)
carTypesView = carviews()

@app.route("/",methods=['GET', 'POST'])
def home():
    allCars = search.getAllCars()
    return render_template('index.html', allCars = allCars, carTypes = carTypesView)

@app.route("/results",methods=['POST'])
def results():
    if request.method == 'POST':
        searchTerm = request.form.get('search-term')
        searchType = request.form.get('type')
        if (searchType == 'search'):
            searchResult = search.getSearchResult(searchTerm=searchTerm,searchType=searchType)
            searchResult = search.processSearch(searchResult = searchResult,searchTerm = searchTerm)
            allCars = search.getAllCars()
            return render_template('results.html', searchTerm=searchTerm, results=searchResult, allCars=allCars)

        if (searchType == 'carType'):
            # searchTerm = searchTerm.upper() if searchTerm=='suv' else searchTerm.title()
            searchResult = search.getSearchResult(searchTerm=searchTerm,searchType=searchType)
            searchResult = search.processSearch(searchResult = searchResult,searchTerm = searchTerm)
            allCars = search.getAllCars()
            # handle when carType is searched
            return render_template('results.html', searchTerm=searchTerm,results=searchResult, allCars=allCars)

@app.route('/results-view', methods=['POST'])
def results_view():
    if request.method == 'POST':
        product_id = request.form.get('productId')
        car = search.getProduct(product_id)
        car = search.processResultsView(car)
        return render_template('results-view.html', car=car)

@app.route('/sell',methods=['GET', 'POST'])
def sell():    
    conn = get_sql_conn(config['sql-prod'],
                        config.get('sql-prod', 'bi_db'))
    possibleSearches = pd.read_sql('''
                                   select   cd.cd_make as car_make,
                                            cd.cd_model as car_brand,
                                            cd.cd_body_style 
                                    from    car_details cd
                                    ''', conn
                                   )
    conn.close()
    possibleSearches = possibleSearches[possibleSearches.cd_body_style!='NaN']
    possibleSearchesCarType = possibleSearches.groupby(['cd_body_style']).agg(Makes = ('car_make',lambda x:list(set(x)))).to_dict()
    carTypes = list(possibleSearchesCarType.get('Makes').keys())

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'getCarMake':
            car_type = request.form.get('carType')
            result_car_make = list(possibleSearchesCarType.get('Makes').get(car_type))
            return jsonify(result_car_make)
        
        if action == 'getCarModel':
            car_make = request.form.get('carMake')
            car_type = request.form.get('carType')
            possibleSearchesCarModel = possibleSearches[possibleSearches.cd_body_style == car_type].groupby(['car_make']).agg(models = ('car_brand',lambda x:list(set(x)))).to_dict().get('models').get(car_make)
            return jsonify(possibleSearchesCarModel)
        
        if action == 'getCarPrice':
            return jsonify(price=10)
        
    return render_template('sell.html', carTypes=carTypes)

if __name__ == "__main__":
	app.run(debug=True)
