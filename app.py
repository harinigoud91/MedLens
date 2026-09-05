from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>MedLens</title>
        <style>
            body {
                font-family: Arial;
                text-align: center;
                padding: 100px;
                background: #f4f8fb;
            }
            h1 { color: #1769aa; }
        </style>
    </head>
    <body>
        <h1>MedLens</h1>
        <h2>Medical Report Analysis</h2>
        <p>MedLens is successfully deployed!</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run()