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
        usuarios = conn.execute("SELECT FROM * CADASTRO").fetchall()

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
            return jsonify(usuarios_formatados), 100


@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    email = dados["email"]
    senha = dados["senha"]

    with sqlite3.connect("database.db") as conn:
        conn.row_factory = sqlite3.Row  # permite acessar os dados como dicionário
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


if __name__ == "__main__":
    app.run(debug=True)
