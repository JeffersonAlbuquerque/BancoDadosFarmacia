from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)



def init_db(): 
    with sqlite3.connect("database.db") as conn:
        conn.execute("""
    CREATE TABLE IF NOT EXISTS CADASTROPRODUTO(
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome TEXT NOT NULL,
                     descricaoProduto TEXT NOT NULL,
                     precoProduto TEXT NOT NULL,
                     quantidadeDisponivel INTEGER NOT NULL)
""")





if __name__ == "__main__":
    app.run(debug=True)
