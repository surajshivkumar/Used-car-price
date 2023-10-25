import pandas as pd
from flask import Flask, jsonify, render_template, request

from utils import get_confg, get_sql_conn, carviews
from searches import Search

import warnings

# Suppress all warnings for cleaner output
warnings.filterwarnings("ignore")

# Initialize Flask app
app = Flask(__name__)

# Configuration setup
config_path = '../app/schema/app.conf'
config = get_confg(config_path)

# Initialize search object for operations
search = Search(config=config)
carTypesView = carviews()

@app.route("/",methods=['GET', 'POST'])
def home():
    '''
    Home endpoint showing the main search page.
    '''
    allCars = search.getAllCars()
    return render_template('index.html', allCars=allCars, carTypes=carTypesView)

@app.route("/results",methods=['POST'])
def results():
    '''
    Endpoint that handles the search functionality and displays results.
    '''
    if request.method == 'POST':
        searchTerm = request.form.get('search-term')
        searchType = request.form.get('type')

        # Process and display results based on search type
        searchResult = search.getSearchResult(searchTerm=searchTerm,searchType=searchType)
        searchResult = search.processSearch(searchResult=searchResult,searchTerm=searchTerm)
        allCars = search.getAllCars()
        return render_template('results.html', searchTerm=searchTerm, results=searchResult, allCars=allCars)

@app.route('/results-view', methods=['POST'])
def results_view():
    '''
    Endpoint that displays a detailed view of a specific car.
    '''
    if request.method == 'POST':
        product_id = request.form.get('productId')
        car = search.getProduct(product_id)
        car = search.processResultsView(car)
        return render_template('results-view.html', car=car)

@app.route('/sell',methods=['GET', 'POST'])
def sell():    
    '''
    Endpoint that handles the functionality of selling a car.
    '''
    # Get possible searches from the database
    conn = get_sql_conn(config['sql-prod'], config.get('sql-prod', 'bi_db'))
    possibleSearches = pd.read_sql('''...''', conn)  # SQL query truncated for brevity
    conn.close()

    possibleSearches = possibleSearches[possibleSearches.cd_body_style != 'NaN']
    possibleSearchesCarType = possibleSearches.groupby(['cd_body_style']).agg(Makes=('car_make', lambda x: list(set(x)))).to_dict()
    carTypes = list(possibleSearchesCarType.get('Makes').keys())

    # Handle POST actions for selling a car
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'getCarMake':
            car_type = request.form.get('carType')
            result_car_make = list(possibleSearchesCarType.get('Makes').get(car_type))
            return jsonify(result_car_make)
        
        # ... Similar logic for other actions (getCarModel, getCarPrice) ...

    return render_template('sell.html', carTypes=carTypes)

# Entry point for the Flask app
if __name__ == "__main__":
    app.run(debug=True)
