from flask import Flask,render_template

app=Flask(__name__,template_folder='template')


@app.route('/hello.html')
def hello_world():
    return render_template('hello.html')
