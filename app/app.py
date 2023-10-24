from flask import Flask , render_template,request,jsonify
import pandas as pd
from utils import get_sql_conn,get_confg
app = Flask(__name__)
config_path = '../app/schema/app.conf'
config = get_confg(config_path)

carTypesView = [
    {
        'key': 'pickups',
        'value': 'Pickups',
    },
    {
        'key': 'suv',
        'value': 'SUV',
    },
    {
        'key': 'hatchback',
        'value': 'Hatchback',
    },
    {
        'key': 'coupe',
        'value': 'Coupe',
    },
    {
        'key': 'sedan',
        'value': 'Sedan',
    },
    {
        'key': 'convertible',
        'value': 'Convertible',
    },
    {
        'key': 'minivan',
        'value': 'Minivan',
    },
    {
        'key': 'wagon',
        'value': 'Wagon',
    },
]

def getAllCars() -> list:
    conn = get_sql_conn(config['sql-prod'],
                        config.get('sql-prod', 'bi_db'))
    cars = pd.read_sql('''select distinct concat(car_make,' ',car_brand) as cars from all_cars''',conn)
    conn.close()

    cars['cars'] = cars.apply(lambda x: x.str.title())
    return cars.values.ravel().tolist()

def getSearchResult(searchTerm: str) -> list:
    res = []
    conn = get_sql_conn(config['sql-prod'],
                    config.get('sql-prod', 'bi_db'))
    res = pd.read_sql('''select cd_mileage_miles as mileage,
                                            cd_year as Year,
                                            cd_make as Make,
                                            cd_car_price as Price,
                                            cd_path_ as path,
                                            cd_model as Model
                                    from car_details cd 
                                    where upper(cd_make) = '{make}' and upper(cd_model) = '{brand}' '''.format(make = searchTerm.split(' ')[0].upper(), 
                                                                                                                    brand= ' '.join(searchTerm.split(' ')[1:]).upper() ),conn)
    conn.close()
    return res

@app.route("/",methods=['GET', 'POST'])
def home():
    allCars = getAllCars()
    return render_template('index.html', allCars = allCars, carTypes = carTypesView)

@app.route("/results",methods=['POST'])
def results():
    if request.method == 'POST':
        searchTerm = request.form.get('search-term')
        searchType = request.form.get('type')
        if (searchType == 'search'):
            searchResult = getSearchResult(searchTerm)
            searchResult = searchResult.drop_duplicates(['make','year','model'])
            searchResult['search'] = searchTerm
            searchResult['path'] = searchResult.path
            searchResult = searchResult.sort_values(['mileage'],ascending=True)
            searchResult['path'] = searchResult.path.apply(lambda car: car.split('.')[0] + '.webp')
            searchResult = [term for term in searchResult.T.to_dict().values()]

            for car in searchResult:
                path_parts = car['path'].split('.')
                new_path = path_parts[0] + '.webp'
                car['path'] = new_path

            allCars = getAllCars()
            return render_template('results.html', searchTerm=searchTerm, results=searchResult, allCars=allCars)

        if (searchType == 'carType'):
            # handle when carType is searched
            return render_template('results.html', searchTerm=searchTerm)

@app.route('/results-view')
def results_view():
    return render_template('results-view.html')

@app.route('/sell',methods=['GET', 'POST'])
def sell():    
    conn = get_sql_conn(config['sql-prod'],
                        config.get('sql-prod', 'bi_db'))
    possibleSearches = pd.read_sql('''select cd.cd_make as car_make,cd.cd_model as car_brand,cd.cd_body_style from car_details cd''',conn)
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
