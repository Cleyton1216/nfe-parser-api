from flask import Flask, request, jsonify
import xmltodict
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "API funcionando!"

@app.route("/lerxml", methods=["POST"])
def lerxml():
    dados = request.get_json()

    xml = dados.get("xml")

    resultado = xmltodict.parse(xml)

    return jsonify(resultado)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
