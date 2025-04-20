from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS
import bcrypt  # ADICIONADO PARA HASH DA SENHA

app = Flask(__name__)
CORS(app)


def init_db():  # inicia o database.
    with sqlite3.connect("database.db") as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS CADASTRO(
                     nome TEXT NOT NULL,
                     cpf TEXT PRIMARY KEY,
                     nascimento TEXT NOT NULL,
                     email TEXT NOT NULL UNIQUE,
                     celular TEXT NOT NULL,
                     telefone TEXT,
                     senha TEXT NOT NULL)
""")

        conn.execute("""
CREATE TABLE IF NOT EXISTS PRODUTOS(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    img_url TEXT NOT NULL,
    nome TEXT NOT NULL,
    categoria_id INTEGER,
    fabricante TEXT, 
    descricao TEXT,
    dosagem TEXT,
    forma TEXT,
    quantidade INTEGER NOT NULL,
    preco FLOAT NOT NULL,
    lote TEXT NOT NULL,
    validade TEXT NOT NULL,
    controlado BOOL,
    FOREIGN KEY (categoria_id) REFERENCES CATEGORIA(id)
)
""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS CATEGORIA(
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome TEXT NOT NULL)
""")


init_db()


@app.route("/")
def bem_vindo():
    return "<h1>Seja bem vindo!</h1>"


@app.route("/cadastro", methods=["POST"])
def cadastrarUsuario():
    dados = request.get_json()

    nome = dados.get("nome")
    cpf = dados.get("cpf")
    nascimento = dados.get("nascimento")
    email = dados.get("email")
    celular = dados.get("celular")
    telefone = dados.get("telefone")
    senha = dados.get("senha")

    # Gerar hash da senha
    senha_bytes = senha.encode('utf-8')
    senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())

    with sqlite3.connect("database.db") as conn:
        conn.execute("""
    INSERT INTO CADASTRO (nome, cpf, nascimento, email, celular, telefone, senha)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (nome, cpf, nascimento, email, celular, telefone, senha_hash.decode('utf-8')))
        conn.commit()  # COMANDO PARA SALVAR AS MUDANÇAS NO BANCO DE DADOS.

        return jsonify({"sucesso": "Cadastrado com sucesso"}), 201
        # return jsonify({"Mensagem": "Usuário Cadastrado com sucesso"}), 201


@app.route("/usuarios", methods=["GET"])
def listarUsuarios():
    with sqlite3.connect("database.db") as conn:
        usuarios = conn.execute("SELECT * FROM CADASTRO").fetchall()

        usuarios_formatados = []

        for item in usuarios:
            usuarios_dicionario = {
                "nome": item[0],
                "cpf": item[1],
                "nascimento": item[2],
                "email": item[3],
                "celular": item[4],
                "telefone": item[5]
            }
            usuarios_formatados.append(usuarios_dicionario)

        return jsonify(usuarios_formatados), 200


@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    email = dados["email"]
    senha = dados["senha"]

    with sqlite3.connect("database.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CADASTRO WHERE email = ?", (email,))
        usuario = cursor.fetchone()

        if usuario:
            senha_hash = usuario["senha"]
            if bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
                return jsonify({
                    "sucesso": True,
                    "usuario": {
                        "nome": usuario["nome"],
                        "email": usuario["email"],
                        "cpf": usuario["cpf"]
                    }
                })
            return jsonify({"sucesso": False, "mensagem": "Email ou senha inválidos"}), 401
        else:
            return jsonify({"sucesso": False, "mensagem": "Usuário não encontrado"}), 404


@app.route("/cadastrarCategoria", methods=["POST"])
def cadastrarCategorias():
    dados = request.get_json()
    categoria = dados.get("nome")

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO CATEGORIA (nome)
            VALUES (?)
        """, (categoria,))
        conn.commit()

    return jsonify({"mensagem": "Categoria cadastrada com sucesso!"}), 201


@app.route("/categorias", methods=["GET"])
def listarCategorias():
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM CATEGORIA ORDER BY nome ASC")
        categorias = cursor.fetchall()

        categorias_formatadas = []
        for cat in categorias:
            categorias_formatadas.append({
                "id": cat[0],
                "nome": cat[1]
            })

    return jsonify(categorias_formatadas), 200


@app.route("/cadastrarProdutos", methods=["POST"])
def cadastrarProdutos():
    dados = request.get_json()

    img_url = dados.get("img_url")
    nome = dados.get("nome")
    categoria_id = dados.get("categoria")  # categoria_id agora!
    fabricante = dados.get("fabricante")
    descricao = dados.get("descricao")
    dosagem = dados.get("dosagem")
    forma = dados.get("forma")
    quantidade = dados.get("quantidade")
    preco = dados.get("preco")
    validade = dados.get("validade")
    lote = dados.get("lote")
    controlado = dados.get("controlado")

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO PRODUTOS (
                img_url, nome, categoria_id, fabricante, descricao,
                dosagem, forma, quantidade, preco, lote, validade, controlado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            img_url, nome, categoria_id, fabricante, descricao,
            dosagem, forma, quantidade, preco, lote, validade, controlado
        ))

        conn.commit()

    return jsonify({"mensagem": "Produto cadastrado com sucesso!"}), 201


@app.route("/produtosCadastrados", methods=["GET"])
def listarProdutos():
    with sqlite3.connect("database.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                P.id, P.img_url, P.nome, P.fabricante, P.descricao, 
                P.dosagem, P.forma, P.quantidade, P.preco, 
                P.lote, P.validade, P.controlado,
                C.id AS categoria_id, C.nome AS categoria_nome
            FROM PRODUTOS P
            LEFT JOIN CATEGORIA C ON P.categoria_id = C.id
            ORDER BY P.nome ASC
        """)

        produtos = cursor.fetchall()

        produtos_formatados = []

        for item in produtos:
            produtos_dicionario = {
                "id": item["id"],
                "img_url": item["img_url"],
                "nome": item["nome"],
                "fabricante": item["fabricante"],
                "descricao": item["descricao"],
                "dosagem": item["dosagem"],
                "forma": item["forma"],
                "quantidade": item["quantidade"],
                "preco": item["preco"],
                "lote": item["lote"],
                "validade": item["validade"],
                "controlado": item["controlado"],
                "categoria": {
                    "id": item["categoria_id"],
                    "nome": item["categoria_nome"]
                } if item["categoria_id"] else None
            }
            produtos_formatados.append(produtos_dicionario)

        return jsonify(produtos_formatados), 200


@app.route("/deletarProduto/<int:id>", methods=["DELETE"])
def deletarProduto(id):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.execute("SELECT * FROM PRODUTOS WHERE id = ?", (id,))
        produto = cursor.fetchone()

        if not produto:
            return jsonify({"erro": "Produto não encontrado"}), 401

        conn.execute("DELETE FROM PRODUTOS WHERE id = ?", (id,))
        conn.commit()
    return jsonify({"mensagem": f"Produto com ID {id} deletado com sucesso!"}), 200


if __name__ == "__main__":
    app.run(debug=True)
