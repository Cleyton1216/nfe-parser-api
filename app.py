from flask import Flask, request, jsonify
import xmltodict
import requests
import os
from rapidfuzz import process, fuzz

app = Flask(__name__)

@app.route("/")
def home():
    return "API funcionando!"

@app.route("/buscar_similar_lote", methods=["POST"])
def buscar_similar_lote():
    dados = request.get_json(silent=True)

    if not dados or "produtos" not in dados or "lista" not in dados:
        return jsonify({"erro": "Envie um JSON com as chaves 'produtos' (nomes da nota) e 'lista' (produtos já cadastrados)."}), 400

    produtos_nota = dados.get("produtos")  # lista de nomes vindos do XML
    lista_cadastrados = dados.get("lista")  # lista de nomes já no banco

    resultados = []

    for nome_produto in produtos_nota:
        if not lista_cadastrados:
            resultados.append({
                "nome_nota": nome_produto,
                "encontrado": False,
                "melhor_match": None,
                "score": 0
            })
            continue

        melhor = process.extractOne(
            nome_produto,
            lista_cadastrados,
            scorer=fuzz.token_set_ratio
        )

        if melhor is None:
            resultados.append({
                "nome_nota": nome_produto,
                "encontrado": False,
                "melhor_match": None,
                "score": 0
            })
            continue

        nome_encontrado, score, _ = melhor

        resultados.append({
            "nome_nota": nome_produto,
            "encontrado": score >= 80,
            "melhor_match": nome_encontrado,
            "score": round(score, 1)
        })

    return jsonify({"resultados": resultados})

@app.route("/buscar_similar", methods=["POST"])
def buscar_similar():
    dados = request.get_json(silent=True)

    if not dados or "nome" not in dados or "lista" not in dados:
        return jsonify({"erro": "Envie um JSON com as chaves 'nome' (produto da nota) e 'lista' (produtos já cadastrados)."}), 400

    nome_busca = dados.get("nome")
    lista_produtos = dados.get("lista")  # lista de nomes já cadastrados no banco

    if not lista_produtos:
        return jsonify({"encontrado": False, "melhor_match": None, "score": 0})

    # token_sort_ratio ignora a ordem das palavras, ajuda quando o texto vem
    # com termos extras ou em ordem diferente entre fornecedores
    melhor = process.extractOne(
        nome_busca,
        lista_produtos,
        scorer=fuzz.token_set_ratio
    )

    if melhor is None:
        return jsonify({"encontrado": False, "melhor_match": None, "score": 0})

    nome_encontrado, score, _ = melhor

    return jsonify({
        "encontrado": score >= 80,  # ajuste esse limite conforme os testes
        "melhor_match": nome_encontrado,
        "score": round(score, 1)
    })

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
