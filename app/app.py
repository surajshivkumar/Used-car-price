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
    results = request.form.get('search-term')
    type = request.form.get('type')
    if type == 'search':
        # do something
        return render_template('results.html', val = results)

    else:
        # do something
        return render_template('results.html', val = results)
    


@app.route('/results-view')
def results_view():
    return render_template('results-view.html')

@app.route('/sell',methods=['GET', 'POST'])
def sell():    
    if request.method == 'POST':
        # carType = request.form.get('carType')
        return render_template('sell.html', car_types=car_types, price=10)
    
    return render_template('sell.html', car_types=car_types)
    

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
