from flask import Flask, request
from my_functions import do_sum, answerer
app = Flask(__name__)

#@app.route("/")
#def hello():
    #return "Hello World2!"

@app.route("/", methods=["GET", "POST"])
def adder_page():
    errors = ""
    if request.method == "POST":
        request_string = None
        try:
            request_string = request.form["question"]
        except:
            errors += "<p>{!r} is not a number.</p>\n".format(request.form["question"])
        if request_string is not None:
            result = answerer(request_string)
            return '''
                <html>
                    <body>
                        <p>The result is {result}</p>
                        <p><a href="/">Click here to calculate again</a>
                    </body>
                </html>
            '''.format(result=result)

    return '''
        <html>
            <body>
                {errors}
                <p>Enter your numbers:</p>
                <form method="post" action=".">
                    <p><input name="question" /></p>
                    <p><input type="submit" value="Do calculation" /></p>
                </form>
            </body>
        </html>
    '''.format(errors=errors)
if __name__ == "__main__":
    app.run(host='130.141.112.137')