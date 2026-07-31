from flask import Flask, request, jsonify
import xmltodict
import requests
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "API funcionando!"

@app.route("/lerxml", methods=["POST"])
def lerxml():
    dados = request.get_json(silent=True)

    if not dados or "url" not in dados:
        return jsonify({"erro": "Envie um JSON com a chave 'url' apontando para o arquivo XML."}), 400

    url = dados.get("url")

    # Bubble costuma retornar URLs de arquivo sem o esquema (ex: "//cdn.bubble.io/...")
    if url.startswith("//"):
        url = "https:" + url

    try:
        resposta = requests.get(url, timeout=15)
        resposta.raise_for_status()  # lança erro se status != 200
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": f"Falha ao baixar o XML da URL informada: {str(e)}"}), 502

    conteudo_xml = resposta.content  # bytes, formato que xmltodict espera

    try:
        resultado = xmltodict.parse(conteudo_xml)
    except Exception as e:
        return jsonify({"erro": f"Falha ao interpretar o XML: {str(e)}"}), 422

    return jsonify(resultado)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
