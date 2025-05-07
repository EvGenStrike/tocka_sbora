from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
def my_internships():
    return render_template('my_internships.html')

@app.route('/all')
def all_internships():
    return render_template('all_internships.html')

if __name__ == '__main__':
    app.run(debug=True)
