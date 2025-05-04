from flask import Flask, request, jsonify, session
import sqlite3
import bcrypt  # ADICIONADO PARA HASH DA SENHA
from datetime import datetime


def init_routes(app):  # <- Criando a função init_routes(app)

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
        cep = dados.get("cep")  # Novo campo
        endereco = dados.get("endereco")  # Novo campo
        senha = dados.get("senha")

        # Gerar hash da senha
        senha_bytes = senha.encode('utf-8')
        senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())

        with sqlite3.connect("database.db") as conn:
            conn.execute("""
                INSERT INTO CADASTRO (nome, cpf, nascimento, email, celular, telefone, cep, endereco, senha)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nome, cpf, nascimento, email, celular, telefone, cep, endereco, senha_hash.decode('utf-8')))
            conn.commit()

            return jsonify({"sucesso": "Cadastrado com sucesso"}), 201

    @app.route("/editarUsuario/<cpf>", methods=["PUT"])
    def editarUsuario(cpf):
        dados = request.get_json()

        # Receber os dados a serem atualizados
        nome = dados.get("nome")
        nascimento = dados.get("nascimento")
        email = dados.get("email")
        celular = dados.get("celular")
        telefone = dados.get("telefone")
        cep = dados.get("cep")  # Novo campo
        endereco = dados.get("endereco")  # Novo campo

        with sqlite3.connect("database.db") as conn:
            # Verifica se o usuário existe pelo CPF
            cursor = conn.execute(
                "SELECT * FROM CADASTRO WHERE cpf = ?", (cpf,))
            usuario = cursor.fetchone()

            if not usuario:
                return jsonify({"erro": "Usuário não encontrado"}), 404

            # Atualizar dados do usuário
            conn.execute("""
                UPDATE CADASTRO
                SET nome = ?, nascimento = ?, email = ?, celular = ?, telefone = ?, cep = ?, endereco = ?
                WHERE cpf = ?
            """, (nome, nascimento, email, celular, telefone, cep, endereco, cpf))
            conn.commit()

            return jsonify({"mensagem": "Dados do usuário atualizados com sucesso!"}), 200

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
                    "telefone": item[5],
                    "cep": item[6],  # Novo campo
                    "endereco": item[7]  # Novo campo
                }
                usuarios_formatados.append(usuarios_dicionario)

            return jsonify(usuarios_formatados), 200

    @app.route("/login", methods=["POST"])
    def login():
        dados = request.get_json()
        email = dados.get("email")
        senha = dados.get("senha")

        with sqlite3.connect("database.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT rowid, * FROM CADASTRO WHERE email = ?", (email,))
            usuario = cursor.fetchone()

            if usuario:
                senha_hash = usuario["senha"]
                if bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8")):
                    session["usuario_id"] = usuario["rowid"]
                    session["email"] = usuario["email"]
                    session["nome"] = usuario["nome"]

                    return jsonify({
                        "sucesso": True,
                        "mensagem": "Login realizado com sucesso",
                        "usuario": {
                            "id": usuario["rowid"],
                            "nome": usuario["nome"],
                            "email": usuario["email"]
                        }
                    }), 200
                else:
                    return jsonify({"sucesso": False, "mensagem": "Senha incorreta"}), 401
            else:
                return jsonify({"sucesso": False, "mensagem": "Usuário não encontrado"}), 404

    @app.route("/verificarLogin")
    def verificar_login():
        if "usuario_id" in session:
            return jsonify({"logado": True, "usuario": session["nome"]})
        else:
            return jsonify({"logado": False}), 401
    
    @app.route("/logout")
    def logout():
        session.clear()
        return jsonify({"mensagem": "Logout realizado com sucesso!"})
    
    @app.route("/trocarSenha/<cpf>", methods=["PUT"])
    def trocarSenha(cpf):
        dados = request.get_json()

        # Receber a nova senha
        nova_senha = dados.get("nova_senha")
        senha_bytes = nova_senha.encode('utf-8')
        senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())

        with sqlite3.connect("database.db") as conn:
            # Verifica se o usuário existe
            cursor = conn.execute(
                "SELECT * FROM CADASTRO WHERE cpf = ?", (cpf,))
            usuario = cursor.fetchone()

            if not usuario:
                return jsonify({"erro": "Usuário não encontrado"}), 404

            # Atualiza a senha do usuário
            conn.execute("""
                UPDATE CADASTRO
                SET senha = ?
                WHERE cpf = ?
            """, (senha_hash.decode('utf-8'), cpf))
            conn.commit()

            return jsonify({"mensagem": "Senha alterada com sucesso!"}), 200

    @app.route("/usuario_logado", methods=["GET"])
    def usuario_logado():
        if "usuario_id" in session:
            usuario_id = session["usuario_id"]

            with sqlite3.connect("database.db") as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM CADASTRO WHERE rowid = ?", (usuario_id,))
                usuario = cursor.fetchone()

                if usuario:
                    usuario_dados = {
                        "nome": usuario["nome"],
                        "cpf": usuario["cpf"],
                        "nascimento": usuario["nascimento"],
                        "email": usuario["email"],
                        "celular": usuario["celular"],
                        "telefone": usuario["telefone"],
                        "cep": usuario["cep"],
                        "endereco": usuario["endereco"]
                    }

                    return jsonify({"usuario": usuario_dados}), 200
                else:
                    return jsonify({"erro": "Usuário não encontrado"}), 404
        else:
            return jsonify({"erro": "Usuário não logado"}), 401

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

        if not dados.get("img_url") or not dados.get("nome") or not dados.get("categoria_id"):
            return jsonify({"erro": "Campos obrigatórios faltando: img_url, nome ou categoria"}), 400

        if not dados.get("quantidade") or not dados.get("preco") or not dados.get("validade"):
            return jsonify({"erro": "Campos obrigatórios faltando: quantidade, preco ou validade"}), 400

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

    @app.route("/editarProduto/<int:id>", methods=["PUT"])
    def editarProduto(id):
        dados = request.get_json()

        # Recebe os novos dados para o produto
        nome = dados.get("nome")
        categoria_id = dados.get("categoria")
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
            # Verificar se o produto existe
            cursor = conn.execute("SELECT * FROM PRODUTOS WHERE id = ?", (id,))
            produto = cursor.fetchone()

            if not produto:
                return jsonify({"erro": "Produto não encontrado"}), 404

            # Atualizar os dados do produto
            conn.execute("""
                UPDATE PRODUTOS
                SET nome = ?, categoria_id = ?, fabricante = ?, descricao = ?, dosagem = ?, forma = ?,
                    quantidade = ?, preco = ?, validade = ?, lote = ?, controlado = ?
                WHERE id = ?
            """, (nome, categoria_id, fabricante, descricao, dosagem, forma, quantidade, preco, validade, lote, controlado, id))
            conn.commit()

            return jsonify({"mensagem": "Produto atualizado com sucesso!"}), 200

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

    @app.route("/adicionarCarrinho", methods=["POST"])
    def adicionarCarrinho():
        dados = request.get_json()
        usuario_id = dados.get("usuario_id")
        produto_id = dados.get("produto_id")
        quantidade = dados.get("quantidade")

        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()

            # Verificar se o produto existe
            cursor.execute(
                "SELECT id FROM PRODUTOS WHERE id = ?", (produto_id,))
            if not cursor.fetchone():
                return jsonify({"erro": "Produto não encontrado"}), 404

            # Verificar se o produto já está no carrinho
            cursor.execute("""
                SELECT * FROM CARRINHO WHERE usuario_id = ? AND produto_id = ?
            """, (usuario_id, produto_id))
            carrinho_item = cursor.fetchone()

            if carrinho_item:
                # Se já existir, atualize a quantidade
                cursor.execute("""
                    UPDATE CARRINHO SET quantidade = quantidade + ? WHERE usuario_id = ? AND produto_id = ?
                """, (quantidade, usuario_id, produto_id))
                mensagem = "Quantidade atualizada no carrinho!"
            else:
                # Caso contrário, insira um novo item no carrinho
                cursor.execute("""
                    INSERT INTO CARRINHO (usuario_id, produto_id, quantidade)
                    VALUES (?, ?, ?)
                """, (usuario_id, produto_id, quantidade))
                mensagem = "Produto adicionado ao carrinho!"

            conn.commit()
            return jsonify({"mensagem": mensagem}), 201

    @app.route("/pedidos/<cpf>", methods=["GET"])
    def listar_pedidos_usuario(cpf):
        with sqlite3.connect("database.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Descobrir o ID do usuário pelo CPF
            cursor.execute("SELECT rowid FROM CADASTRO WHERE cpf = ?", (cpf,))
            usuario = cursor.fetchone()

            if not usuario:
                return jsonify({"erro": "Usuário não encontrado"}), 404

            usuario_id = usuario["rowid"]

            # Buscar pedidos desse usuário
            cursor.execute("""
            SELECT numero_pedido, data_compra, total, status_pagamento
                        FROM PEDIDOS
                        WHERE usuario_id = ?
                        ORDER BY data_compra DESC
    """, (usuario_id,))

            pedidos = cursor.fetchall()

            pedidos_formatados = [{
                "numero_pedido": pedido["numero_pedido"],
                "data_compra": pedido["data_compra"],
                "total": pedido["total"],
                "status_pagamento": pedido["status_pagamento"]
            }
                for pedido in pedidos
            ]

            return jsonify(pedidos_formatados), 200

    def criar_pedido(usuario_id, produtos):
        numero_pedido = gerar_numero_pedido()
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO pedidos (numero_pedido, usuario_id, status_pagamento)
                VALUES (?, ?, ?)""", (numero_pedido, usuario_id, 'pendente'))
            for produto in produtos:
                cursor.execute("""
                    INSERT INTO itens_pedido (pedido_id, produto_id)
                    VALUES (?, ?)""", (numero_pedido, produto['id']))
            conn.commit()
        except sqlite3.IntegrityError:
            print("Erro: Pedido repetido!")

    @app.route("/finalizarPedido/<cpf>", methods=["POST"])
    def finalizar_pedido(cpf):
        with sqlite3.connect("database.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Pegar usuário
            cursor.execute("SELECT rowid FROM CADASTRO WHERE cpf = ?", (cpf,))
            usuario = cursor.fetchone()
            if not usuario:
                return jsonify({"erro": "Usuário não encontrado"}), 404

            usuario_id = usuario["rowid"]

            # Buscar produtos no carrinho
            cursor.execute("""
                SELECT c.produto_id, c.quantidade, p.preco
                FROM CARRINHO c
                JOIN PRODUTOS p ON c.produto_id = p.id
                WHERE c.usuario_id = ?
            """, (usuario_id,))
            produtos = cursor.fetchall()

            if not produtos:
                return jsonify({"erro": "Carrinho vazio!"}), 400

            total = sum([p["preco"] * p["quantidade"] for p in produtos])
            numero_pedido = gerar_numero_pedido()

            # Inserir pedido
            cursor.execute("""
                INSERT INTO PEDIDOS (numero_pedido, usuario_id, total)
                VALUES (?, ?, ?)
            """, (numero_pedido, usuario_id, total))

            # Inserir itens
            for item in produtos:
                cursor.execute("""
                    INSERT INTO ITENS_PEDIDO (pedido_id, produto_id, quantidade)
                    VALUES (?, ?, ?)
                """, (numero_pedido, item["produto_id"], item["quantidade"]))

            # Limpar carrinho
            cursor.execute(
                "DELETE FROM CARRINHO WHERE usuario_id = ?", (usuario_id,))
            conn.commit()

            return jsonify({"mensagem": "Pedido finalizado!", "numero_pedido": numero_pedido}), 201

    @app.route("/pedidosStatus/<status>", methods=["GET"])
    def pedidos_por_status(status):
        with sqlite3.connect("database.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT numero_pedido, usuario_id, data_compra, total
                FROM PEDIDOS
                WHERE status_pagamento = ?
                ORDER BY data_compra DESC
            """, (status,))
            pedidos = cursor.fetchall()

            pedidos_formatados = [{
                "numero_pedido": p["numero_pedido"],
                "usuario_id": p["usuario_id"],
                "data_compra": p["data_compra"],
                "total": p["total"]
            } for p in pedidos]

            return jsonify(pedidos_formatados), 200

    @app.route("/cancelarPedido/<numero_pedido>", methods=["PUT"])
    def cancelar_pedido(numero_pedido):
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT status_pagamento FROM PEDIDOS WHERE numero_pedido = ?", (numero_pedido,))
        pedido = cursor.fetchone()

        if not pedido:
            return jsonify({"erro": "Pedido não encontrado"}), 404

        if pedido[0] == "cancelado":
            return jsonify({"mensagem": "Pedido já está cancelado"}), 400

        cursor.execute("""
            UPDATE PEDIDOS SET status_pagamento = 'cancelado'
            WHERE numero_pedido = ?
        """, (numero_pedido,))
        conn.commit()
        return jsonify({"mensagem": "Pedido cancelado com sucesso!"}), 200


def listar_produtos_usuario(usuario_id):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.id, p.nome, p.preco, ip.quantidade
        FROM ITENS_PEDIDO ip
        JOIN PRODUTOS p ON ip.produto_id = p.id
        JOIN PEDIDOS pe ON ip.pedido_id = pe.numero_pedido
        WHERE pe.usuario_id = ?
        ORDER BY pe.data_compra DESC
    """, (usuario_id,))

    produtos = cursor.fetchall()
    conn.close()

    produtos_formatados = []
    for produto in produtos:
        produtos_formatados.append({
            "id": produto["id"],
            "nome": produto["nome"],
            "preco": produto["preco"],
            "quantidade": produto["quantidade"]
        })

    return produtos_formatados


def verificar_status_pagamento(numero_pedido):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT status_pagamento FROM pedidos WHERE numero_pedido = ?", (numero_pedido,))
    status = cursor.fetchone()[0]
    return status


def gerar_numero_pedido():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(numero_pedido) FROM pedidos")
    ultimo_numero = cursor.fetchone()[0]
    if ultimo_numero is None:
        return 1  # Caso não haja nenhum pedido registrado ainda
    return ultimo_numero + 1
