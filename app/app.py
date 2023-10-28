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
        conn = get_sql_conn(config['sql-prod'], config.get('sql-prod', 'bi_db'))
        similarSearches = pd.read_sql('''select cd_id,si_0,si_1,si_2 from similarity_matrix where cd_id = {id_} '''.format(id_=float(product_id)), conn)
        conn.close()
        similarSearches = similarSearches.drop(['cd_id'],axis=1)
        similarSearches = [int(val) for val in similarSearches.values[0]]
        conn = get_sql_conn(config['sql-prod'], config.get('sql-prod', 'bi_db'))
        similarItems = pd.read_sql('''select cd_make,cd_model,cd_car_price,cd_path_ from car_details where cd_id in {ids} '''.format(ids=tuple(similarSearches)), conn)
        conn.close()
        print(similarItems.T.to_dict())
        return render_template('results-view.html', car=car)

@app.route('/sell',methods=['GET', 'POST'])
def sell():    
    '''
    Endpoint that handles the functionality of selling a car.
    '''
    # Get possible searches from the database
    conn = get_sql_conn(config['sql-prod'], config.get('sql-prod', 'bi_db'))
    possibleSearches = pd.read_sql('''select cd_body_style,cd_make as car_make,cd_model from car_details''', conn)  # SQL query truncated for brevity
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
        if action == 'getCarModel':
            carMake = request.form.get('carMake')
            car_type = request.form.get('carType')
            possibleSearchesCarModel = possibleSearches[(possibleSearches.car_make == carMake) & (possibleSearches.cd_body_style == car_type)].groupby(['car_make']).agg(Models=('cd_model', lambda x: list(set(x)))).to_dict()
            carTypes = list(possibleSearchesCarModel.get('Models').values())[0]
            return jsonify(carTypes)

    return render_template('sell.html', carTypes=carTypes)

# Entry point for the Flask app
if __name__ == "__main__":
    app.run(debug=True)
