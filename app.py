from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS
import bcrypt  # ADICIONADO PARA HASH DA SENHA
from datetime import datetime
from routes import init_routes
import os

app = Flask(__name__)
CORS(app)



def init_db():  # inicia o database.
    os.makedirs("db", exist_ok=True)  # Cria pasta se não existir
    with sqlite3.connect("database.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS CADASTRO(
                nome TEXT NOT NULL,
                cpf TEXT PRIMARY KEY,
                nascimento TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                celular TEXT NOT NULL,
                cep TEXT NOT NULL,  -- Novo campo
                endereco TEXT NOT NULL,  -- Novo campo
                telefone TEXT,
                senha TEXT NOT NULL
            )
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
                nome TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS CARRINHO (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                produto_id INTEGER,
                quantidade INTEGER,
                FOREIGN KEY (usuario_id) REFERENCES CADASTRO(rowid),
                FOREIGN KEY (produto_id) REFERENCES PRODUTOS(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ITENS_PEDIDO (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id TEXT,
                produto_id INTEGER,
                quantidade INTEGER,
                FOREIGN KEY (pedido_id) REFERENCES PEDIDOS(numero_pedido),
                FOREIGN KEY (produto_id) REFERENCES PRODUTOS(id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS PEDIDOS(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_pedido TEXT UNIQUE,
                usuario_id INTEGER,
                data_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total REAL,
                status_pagamento TEXT DEFAULT 'pendente'
            )
        """)


init_routes(app)  # <-- chamando as rotas.

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
