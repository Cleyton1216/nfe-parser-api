from flask import Flask, request, jsonify
from flask_cors import CORS
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem (necessário para o Bubble)

NFE_NS = "http://www.portalfiscal.inf.br/nfe"

def get_text(element, tag, ns=NFE_NS):
    """Pega o texto de um elemento filho com namespace"""
    if element is None:
        return ""
    child = element.find(f"{{{ns}}}{tag}")
    return child.text if child is not None else ""

@app.route('/')
def home():
    return jsonify({
        "status": "API NFe Parser rodando!",
        "endpoints": {
            "POST /parse-nfe": "Envie o conteúdo XML da NF-e no body (form-data: file=xml)"
        }
    })

@app.route('/parse-nfe', methods=['POST'])
def parse_nfe():
    """
    Recebe um arquivo XML da NF-e e retorna JSON estruturado.

    Como usar no Bubble (API Connector):
    - Method: POST
    - URL: https://SEU-APP.onrender.com/parse-nfe
    - Body type: Form-data
    - Key: file (tipo File)
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado. Use a key 'file' no form-data."}), 400

        file = request.files['file']
        xml_content = file.read().decode('utf-8')

        # Parse do XML
        root = ET.fromstring(xml_content)

        # Dados da nota
        infNFe = root.find(f".//{{{NFE_NS}}}infNFe")
        ide = root.find(f".//{{{NFE_NS}}}ide")
        emit = root.find(f".//{{{NFE_NS}}}emit")
        dest = root.find(f".//{{{NFE_NS}}}dest")
        icms_tot = root.find(f".//{{{NFE_NS}}}ICMSTot")

        # Extrair produtos
        dets = root.findall(f".//{{{NFE_NS}}}det")
        produtos = []

        for det in dets:
            prod = det.find(f"{{{NFE_NS}}}prod")
            rastro = prod.find(f"{{{NFE_NS}}}rastro") if prod is not None else None

            if prod is not None:
                produtos.append({
                    "item": det.get("nItem", ""),
                    "codigo_fornecedor": get_text(prod, "cProd"),
                    "ean": get_text(prod, "cEAN"),
                    "nome": get_text(prod, "xProd"),
                    "ncm": get_text(prod, "NCM"),
                    "cfop": get_text(prod, "CFOP"),
                    "unidade": get_text(prod, "uCom"),
                    "quantidade": get_text(prod, "qCom"),
                    "valor_unitario": get_text(prod, "vUnCom"),
                    "valor_total": get_text(prod, "vProd"),
                    "lote": get_text(rastro, "nLote") if rastro is not None else "",
                    "data_fabricacao": get_text(rastro, "dFab") if rastro is not None else "",
                    "data_validade": get_text(rastro, "dVal") if rastro is not None else ""
                })

        resultado = {
            "sucesso": True,
            "nota_fiscal": {
                "numero": get_text(ide, "nNF"),
                "serie": get_text(ide, "serie"),
                "chave": infNFe.get("Id", "").replace("NFe", "") if infNFe is not None else "",
                "data_emissao": get_text(ide, "dhEmi"),
                "valor_total": get_text(icms_tot, "vNF") if icms_tot is not None else ""
            },
            "emitente": {
                "nome": get_text(emit, "xNome"),
                "cnpj": get_text(emit, "CNPJ"),
                "fantasia": get_text(emit, "xFant")
            },
            "destinatario": {
                "nome": get_text(dest, "xNome"),
                "cnpj": get_text(dest, "CNPJ")
            },
            "produtos": produtos,
            "total_itens": len(produtos)
        }

        return jsonify(resultado)

    except ET.ParseError as e:
        return jsonify({"error": f"XML inválido: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Erro ao processar: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
