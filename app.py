import flask
from flask import Flask, url_for, render_template, request, redirect
from datetime import datetime, timedelta

import sqlite3
import random as r


class Veiculo:
    def __init__(self,id=None, marca=None, modelo=None, categoria=None, transmissao=None, tipo=None, quantidade=None, valor_diaria=None, data_proxima_revisao=None, data_ultima_revisao=None, data_ultima_inspecao=None, is_alugado=0):
        self.id = id
        self.marca = marca
        self.modelo = modelo
        self.categoria = categoria
        self.transmissao = transmissao
        self.tipo = tipo
        self.quantidade = quantidade
        self.valor_diaria = valor_diaria
        self.data_proxima_revisao = data_proxima_revisao
        self.data_ultima_revisao = data_ultima_revisao
        self.data_ultima_inspecao = data_ultima_inspecao
        self.is_alugado = is_alugado

        # Gerar datas aleatórias
        def data_aleatoria(start_date, end_date):
            delta = end_date - start_date
            random_days = r.randint(0, delta.days)
            return start_date + timedelta(days=random_days)

        # Intervalo para as datas
        data_inicial = datetime(2020, 1, 1)
        data_final = datetime(2025, 12, 31)

        self.data_ultima_revisao = data_aleatoria(data_inicial, data_final)
        self.data_proxima_revisao = self.data_ultima_revisao + timedelta(days=r.randint(365, 365 * 2))
        self.data_ultima_inspecao = data_aleatoria(data_inicial, data_final)

    def get_veiculo(self):
        with sqlite3.connect('Database/veiculos.db') as con_veiculo:
            con_veiculo.row_factory = sqlite3.Row
            cursor_veiculo = con_veiculo.cursor()
            cursor_veiculo.execute("SELECT * FROM veiculo")
            rows = cursor_veiculo.fetchall()

        lista_veiculos = []
        for veiculo in rows:
            novo_veiculo = Veiculo(
                id=veiculo['id'],
                marca=veiculo['Marca'],
                modelo=veiculo['Modelo'],
                categoria=veiculo['Categoria'],
                transmissao=veiculo['Transmissao'],
                tipo=veiculo['Tipo'],
                quantidade=veiculo['Quantidade'],
                valor_diaria=veiculo['Diaria'],
                data_ultima_revisao=veiculo['Ultima_Revisao'],
                data_proxima_revisao=veiculo['Proxima_Revisao'],
                data_ultima_inspecao=veiculo['Ultima_Inspecao'],
                is_alugado=veiculo['is_alugado']
            )
            lista_veiculos.append(novo_veiculo)

        return lista_veiculos
    def info_veiculo(self):
        try:
            with sqlite3.connect('Database/veiculos.db') as con_veiculo:
                con_veiculo.row_factory = sqlite3.Row
                cursor_veiculo = con_veiculo.cursor()
                cursor_veiculo.execute("SELECT * FROM veiculo WHERE id = ?", (self.id,))
                resultado_consulta = cursor_veiculo.fetchone()

            # caso o veículo seja encontrado pelo id, atualiza a informação a db
            if resultado_consulta:
                resultado_query = """UPDATE veiculo SET Marca = ?, Modelo = ?, Categoria = ?, Transmissao = ?, Tipo = ?, Quantidade = ?, Diaria = ?, Ultima_Revisao = ?, Proxima_Revisao = ?, Ultima_Inspecao = ?, is_alugado = ? WHERE id = ?"""
                print("Veículo encontrado. A atualizar")

                cursor_veiculo.execute(resultado_query, (self.marca, self.modelo, self.categoria,
                                                          self.transmissao, self.tipo, self.quantidade,
                                                          self.valor_diaria, self.data_ultima_revisao,
                                                          self.data_proxima_revisao, self.data_ultima_inspecao,
                                                          self.is_alugado, self.id))
                con_veiculo.commit()
                print("Veículo atualizado com sucesso.")
            # caso o veículo não seja encontrado pelo id, insere a informação na db
            else:
                cursor_veiculo.execute("""INSERT INTO veiculo(Marca, Modelo, Categoria, Transmissao, Tipo, Quantidade, Diaria, Ultima_Revisao, Proxima_Revisao, Ultima_Inspecao, is_alugado)
                                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                       (self.marca, self.modelo, self.categoria, self.transmissao,
                                        self.tipo, self.quantidade, self.valor_diaria,
                                        self.data_ultima_revisao, self.data_proxima_revisao,
                                        self.data_ultima_inspecao, self.is_alugado))
                con_veiculo.commit()
                self.lista_veiculos = self.get_veiculo()
                return self.lista_veiculos
        except sqlite3.Error as error:
            print("Erro: ",error)

# caso haja duplicados, criou-se uma função para os remover
    def remover_duplicados(self):
        try:
            with sqlite3.connect('Database/veiculos.db') as con_veiculo:
                cursor_veiculo = con_veiculo.cursor()
                cursor_veiculo.execute("""
                    DELETE FROM veiculo
                    WHERE id NOT IN (
                        SELECT MIN(id)
                        FROM veiculo
                        GROUP BY Marca, Modelo, Categoria, Transmissao, Tipo, Quantidade, Diaria, Ultima_Revisao, Proxima_Revisao, Ultima_Inspecao, is_alugado
                    )
                """)
                con_veiculo.commit()
                print("Registos duplicados foram removidos com sucesso.")
        except sqlite3.Error as error:
            print("Erro: ", error)


class User:
    def __init__(self, primeiro_nome, apelido, email):
        self.primeiro_nome = primeiro_nome
        self.apelido = apelido
        self.email = email

    def verificar_credenciais(self):
        with sqlite3.connect('Database/users.db') as con_user:
            con_user.row_factory = sqlite3.Row
            cursor_user = con_user.cursor()
            cursor_user.execute("SELECT * FROM User WHERE email = ?", (self.email,))
            return cursor_user.fetchone() is not None

    def criar_user(self):
        if self.verificar_credenciais():
            return False, "Este email já existe."

        with sqlite3.connect('Database/users.db') as con_user:
            con_user.row_factory = sqlite3.Row
            cursor_user = con_user.cursor()
            cursor_user.execute("""
                INSERT INTO User (primeiro_nome, apelido, email)
                VALUES (?, ?, ?)
            """, (self.primeiro_nome, self.apelido, self.email,))
            con_user.commit()
            return True, "Usuário criado com sucesso."

    def atualizar_user(self):
        try:
            with sqlite3.connect('Database/users.db') as con_user:
                con_user.row_factory = sqlite3.Row
                cursor_user = con_user.cursor()
                query = "UPDATE user SET primeiro_nome = ?, apelido = ?, email = ? WHERE id = ?"
                cursor_user.execute("SELECT * FROM user WHERE id = ?", (self.id,))
                resultado_consulta = cursor_user.fetchone()

                if resultado_consulta is None:
                    self.inserir_user()
                else:
                    cursor_user.execute(query, (self.primeiro_nome, self.apelido, self.email,))
                    con_user.commit()
                    print("Os seus dados foram atualizados com sucesso")
        except sqlite3.Error as error:
            print("Erro ao atualizar os seus dados", error)

# ---------------------------------------------------------- CRIAÇÃO DOS VEÍCULOS ----------------------------------------------------------
lista_veiculos = [
    Veiculo(1116,'Toyota', 'Yaris','Médio','Manual','Carro',5,12,None,None,None,0),
    Veiculo(1117,'Ford','Focus','Médio','Manual','Carro',9,15,None,None,None, 0),
    Veiculo(1118,'Citroen','C4','Grande','Automática','SUV',9,20,None,None,None, 0),
    Veiculo(1119,'Mini','Cooper','Pequeno','Manual','Carro',4,7,None,None,None, 0),
    Veiculo(1120,'Nissan','Qashqai','Grande','Automática','SUV',9,15,None,None,None, 0),
    Veiculo(1121,'BMW','F800 GS','Única','Manual','Mota',1,16,None,None,None, 0),
    Veiculo(1122,'Honda','CRF 230F','única','Automática','Mota',1,16,None,None,None, 0)
    ]

for veiculo in lista_veiculos:
    veiculo.info_veiculo()
    veiculo.remover_duplicados()
    veiculo.get_veiculo()
# ---------------------------------------------------------- CRIAÇÃO DOS VEÍCULOS ----------------------------------------------------------

# Inicializar a aplicação Flask
app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Página inicial da webapp
@app.route('/', methods=['GET'])
def homepage():
    return render_template("index.html")

# Obter os veículos que estão na base de dados com base no tipo: Carro, Mota ou SUV
@app.route('/registar_user', methods=['GET', 'POST'])
def registar_user():
    if request.method == 'GET':
        return render_template('registo_user.html')
    elif request.method == 'POST':
        primeiro_nome = request.form['primeiro_nome']
        apelido = request.form['apelido']
        email = request.form['email']

        # Instanciar um user enquanto objeto
        user = User(primeiro_nome=primeiro_nome, apelido=apelido, email=email)
        success, message = user.criar_user()

        if success:
            return redirect(url_for('resumo_aluguer', primeiro_nome=primeiro_nome, apelido=apelido, email=email))


# fazer o get de todos os veículos da db
def get_all_veiculos():
    with sqlite3.connect('Database/veiculos.db') as con_veiculo:
        con_veiculo.row_factory = sqlite3.Row
        cursor_veiculo = con_veiculo.cursor()
        cursor_veiculo.execute("SELECT Marca, Modelo, Tipo FROM veiculo WHERE is_alugado = 0")
        veiculos = cursor_veiculo.fetchall()
        return [{"Marca": veiculo["Marca"], "Modelo": veiculo["Modelo"], "Tipo": veiculo["Tipo"]} for veiculo in veiculos]

#fazer o get dos veículos por id
def get_veiculos_by_id(veiculo_id):
    with sqlite3.connect('Database/veiculos.db') as con_veiculo:
        con_veiculo.row_factory = sqlite3.Row
        cursor_veiculo = con_veiculo.cursor()
        cursor_veiculo.execute("SELECT Marca, Modelo, Tipo WHERE ID = ?", (veiculo_id,))
        veiculo = cursor_veiculo.fetchone()

        if veiculo:
            return{"Marca": veiculo["Marca"], "Modelo": veiculo["Modelo"], "Tipo": veiculo["Tipo"]}
        return None

#fazer o get dos veículos por tipo
def get_veiculos_by_tipo(tipo):
    with sqlite3.connect('Database/veiculos.db') as con_veiculo:
        con_veiculo.row_factory = sqlite3.Row
        cursor_veiculo = con_veiculo.cursor()
        cursor_veiculo.execute("SELECT Marca, Modelo, Tipo FROM veiculo WHERE tipo = ? AND is_alugado = 0", (tipo,))
        veiculos = cursor_veiculo.fetchall()
        return [{"Marca": veiculo["Marca"], "Modelo": veiculo["Modelo"], "Tipo": veiculo["Tipo"]} for veiculo in veiculos]

#fazer o get do valor da diaria correspondente ao veículo na db
def get_valor_diaria(veiculo_id):
    with sqlite3.connect('Database/veiculos.db') as con_veiculo:
        con_veiculo.row_factory = sqlite3.Row
        cursor_veiculo = con_veiculo.cursor()
        cursor_veiculo.execute("SELECT Diaria FROM veiculo WHERE ID = ?", (veiculo_id,))
        resultado = cursor_veiculo.fetchone()
        return resultado['Diaria'] if resultado else None



@app.route('/selecionar_veiculo', methods=['GET','POST'])
def selecionar_veiculo():
    try:
        if request.method == 'GET':
            tipo = request.args.get('tipo')
            veiculos = get_veiculos_by_tipo(tipo) if tipo else get_all_veiculos()
            return render_template('selecionar_veiculo.html', veiculos=veiculos, tipo=tipo)

        elif request.method == 'POST':
            veiculo_id = request.form['veiculo_id']
            return redirect(url_for('resumo_aluguer', veiculo_id=veiculo_id))

    except Exception as e:
        return str(e), 500
@app.route('/alugar_veiculo', methods=['GET', 'POST'])
def alugar_veiculo():
    try:
        veiculo_id = request.args.get('veiculo_id')

        if request.method == 'POST':
            data_inicio_dt = request.form.get('data_inicio')
            data_fim_dt = request.form.get('data_fim')

            return redirect(url_for('pagamento', veiculo_id=veiculo_id, data_inicio_dt=data_inicio_dt, data_fim_dt=data_fim_dt))
        return render_template('alugar_veiculo.html', veiculo_id=veiculo_id)

    except Exception as e:
        print(f"Erro ao processar a solicitação {e}")
        return str(e), 500

@app.route('/pagamento', methods = ['GET','POST'])
def pagamento():
    if request.method == 'GET':
        return render_template('pagamento.html')
    if request.method == 'POST':
        metodo_pagamento = request.form.get('metodo_pagamento')
        print(f"Selecionou {metodo_pagamento} como método de pagamento.")
        return redirect(url_for('resumo_aluguer', metodo_pagamento = metodo_pagamento))
@app.route('/resumo_aluguer', methods = ['GET'])
def resumo_aluguer():
    try:
        primeiro_nome = request.args.get('primeiro_nome')
        apelido = request.args.get('apelido')
        email = request.args.get('email')
        veiculo_selecionado = request.args.get('veiculo_id')
        data_inicio_dt = request.args.get('data_inicio') #converter para dt(datetime)
        data_final_dt = request.args.get('data_final') #converter para dt(datetime)
        metodo_pagamento = request.args.get('metodo_pagamento')
        #valor_pagar = request.args.get('valor_pagar')

        # converter as datas para o formato datetime
        data_inicio = datetime.strptime(data_inicio_dt,'%Y-%m-%d')
        data_final = datetime.strptime(data_final_dt, '%Y-%m-%d')

        # calcular o número de dias
        num_dias = (data_final - data_inicio).days
        #
        valor_pagar = get_valor_diaria(veiculo_selecionado) * num_dias

        return render_template('resumo_aluguer.html', primeiro_nome=primeiro_nome,
                               apelido=apelido, email=email,veiculo_selecionado=veiculo_selecionado,
                               data_inicio=data_inicio, data_final=data_final,
                               metodo_pagamento=metodo_pagamento, valor_pagar=valor_pagar)
    except Exception as e:
        print(f"Erro ao finalizar o processo {e}")
        return str(e), 500

@app.route('/aluguer_sucesso', methods =['GET'])
def aluguer_sucesso():
    return render_template('aluguer_sucesso')



'''debug para verificar as colunas da tabela sql:
def verificar_tabela():
    with sqlite3.connect('Database/veiculos.db') as con_veiculo:
        cursor_veiculo = con_veiculo.cursor()
        cursor_veiculo.execute("PRAGMA table_info(veiculo)")
        colunas = cursor_veiculo.fetchall()
        for coluna in colunas:
            print(coluna)

verificar_tabela()
'''

if __name__ == '__main__':
    app.run()
