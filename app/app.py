from flask import Flask , render_template,request
import pandas as pd
from utils import get_sql_conn,get_confg
app = Flask(__name__)
config_path = '/Users/suraj/Documents/used_car/app/schema/app.conf'
config = get_confg(config_path)


@app.route("/",methods=['GET', 'POST'])
def hello_world():
    conn = get_sql_conn(config['sql-prod'],
                        config.get('sql-prod', 'bi_db'))
    cars = pd.read_sql('''select distinct concat(car_make,' ',car_brand) as cars from all_cars''',conn)
    conn.close()
    cars['cars'] = cars.apply(lambda x: x.str.title())
    cars = cars.values.ravel().tolist()

    return render_template('index.html', val = cars)


@app.route("/recommend",methods=['GET', 'POST'])
def recommend():
    results = request.form.get('search-term')
    # titles,imgs = authors_recommendations(results)[0], authors_recommendations(results)[1]
    # titles = [i for i in titles]
    # imgs = [i for i in imgs]
    return results
if __name__ == "__main__":
	app.run(debug=True)
