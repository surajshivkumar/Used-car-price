from flask import Flask , render_template,request

app = Flask(__name__)

@app.route("/",methods=['GET', 'POST'])
def hello_world():
    return render_template('index.html', val = {'key': 'hello'})

if __name__ == "__main__":
	app.run(debug=True)
