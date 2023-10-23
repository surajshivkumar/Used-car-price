from flask import Flask , render_template,request,jsonify
import pandas as pd
from utils import get_sql_conn,get_confg
app = Flask(__name__)
config_path = '../app/schema/app.conf'
config = get_confg(config_path)
    
car_types = ['suv', 'sedan', 'convertible']

car_make_map = {
    'suv': ['bmw', 'jeep'],
    'sedan': ['ford', 'mercedes'],
    'convertible': ['fiat', 'volvo']
}

car_model_map = {
    'bmw': ['5 series'],
    'jeep': ['wrangler'],
    'ford': ['c70']
}

@app.route("/",methods=['GET', 'POST'])
def hello_world():
    conn = get_sql_conn(config['sql-prod'],
                        config.get('sql-prod', 'bi_db'))
    cars = pd.read_sql('''select distinct concat(car_make,' ',car_brand) as cars from all_cars''',conn)
    conn.close()
    if request.method == 'POST':
        search_term = request.form.get('search-term')
        # print(f"carType: {search_term}")
        return render_template('results.html', val = search_term)

    cars['cars'] = cars.apply(lambda x: x.str.title())
    cars = cars.values.ravel().tolist()

    return render_template('index.html', val = cars)


@app.route("/results",methods=['POST'])
def results():
    searchTerm = request.form.get('search-term')
    conn = get_sql_conn(config['sql-prod'],
                    config.get('sql-prod', 'bi_db'))
    searchResult = pd.read_sql('''select cd_mileage_miles as mileage,
                                            cd_year as Year,
                                            cd_make as Make,
                                            cd_car_price as Price,
                                            cd_path_ as path,
                                            cd_model as Model
                                    from car_details cd 
                                    where upper(cd_make) = '{make}' and upper(cd_model) = '{brand}' '''.format(make = searchTerm.split(' ')[0].upper(), 
                                                                                                                    brand= ' '.join(searchTerm.split(' ')[1:]).upper() ),conn)
    conn.close()
    print(searchResult.columns)
    searchResult = searchResult.drop_duplicates(['make','year','model'])
    searchResult['search'] = searchTerm
    searchResult['path'] = searchResult.path
    searchResult = searchResult.sort_values(['mileage'],ascending=True)
    searchResult['path'] = searchResult.path.apply(lambda car: car.split('.')[0] + '.webp')
    searchResult = [term for term in searchResult.T.to_dict().values()]
    
    return render_template('results.html', searchTerm=searchTerm, results=searchResult)


@app.route('/results-view')
def results_view():
    return render_template('results-view.html')

@app.route('/sell',methods=['GET', 'POST'])
def sell():    
    print('first')
    conn = get_sql_conn(config['sql-prod'],
                        config.get('sql-prod', 'bi_db'))
    possibleSearches = pd.read_sql('''select cd.cd_make as car_make,cd.cd_model as car_brand,cd.cd_body_style from car_details cd''',conn)
    conn.close()
    possibleSearches = possibleSearches[possibleSearches.cd_body_style!='NaN']
    possibleSearchesCarType = possibleSearches.groupby(['cd_body_style']).agg(Makes = ('car_make',lambda x:list(set(x)))).to_dict()
    carTypes = list(possibleSearchesCarType.get('Makes').keys())
    print('carTypes', carTypes)

    model = ['test']
    if request.method == 'POST':
        action = request.form.get('action')
        print('action', action)
        if action == 'getCarMake':
            car_type = request.form.get('carType')
            result_car_make = list(possibleSearchesCarType.get('Makes').get(car_type))
            return jsonify(result_car_make)
        
        if action == 'getCarModel':
            car_make = request.form.get('carMake')
            car_type = request.form.get('carType')
            print('check make, type', car_make, car_type)
            possibleSearchesCarModel = possibleSearches[possibleSearches.cd_body_style == car_type].groupby(['car_make']).agg(models = ('car_brand',lambda x:list(set(x)))).to_dict().get('models').get(car_make)
            print('Check == car_type\n: ', possibleSearches[possibleSearches.cd_body_style == car_type])
            print('\n\npossibleSearches\n: ', possibleSearches)
            print('possibleSearchesCarModel', possibleSearchesCarModel)
            return jsonify(possibleSearchesCarModel)
        
        if action == 'getCarPrice':
            return jsonify(price=10)
        
    return render_template('sell.html', car_types=carTypes)
    

@app.route('/get_car_make/<car_type>')
def get_car_make(car_type):
    if car_type in car_make_map:
        return jsonify(car_make_map[car_type])
    else:
        return jsonify([])

@app.route('/get_car_model/<car_make>')
def get_car_model(car_make):
    if car_make in car_model_map:
        return jsonify(car_model_map[car_make])
    else:
        return jsonify([])

if __name__ == "__main__":
	app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000)
