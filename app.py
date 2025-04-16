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

        return jsonify({"Mensagem": "Usuário Cadastrado com sucesso"}), 201


if __name__ == "__main__":
    app.run(debug=True)
