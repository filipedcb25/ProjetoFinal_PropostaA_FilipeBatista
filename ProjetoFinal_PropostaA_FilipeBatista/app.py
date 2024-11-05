import flask
from flask import Flask, url_for, render_template, request, redirect, session, flash
from datetime import datetime, timedelta
import sqlite3
import random as r

# ----------------- CLASSES E SUAS CARACTERÍSTICAS E FUNCIONALIDADES ----------------- #
class Veiculo: # Criação da classe veículo com os parâmetros que vão ser usados na DB
    @staticmethod
    def filtrar_veiculos(lista_veiculos, tipo_veiculo):
        veiculos_filtrados = [veiculo for veiculo in lista_veiculos if veiculo.tipo == tipo_veiculo]
        return veiculos_filtrados

    @staticmethod
    def catalogar_veiculos(lista_veiculos, tipo = None): # segundo argumento é opcional
        if tipo is not None:
            veiculos_filtrados = [veiculo for veiculo in lista_veiculos if veiculo.tipo == tipo]
            for veiculo in  veiculos_filtrados:
                atributos = ','.join(f"{atributo} = {valor}" for atributo, valor in veiculo.__dict__.items())
                print(f"Veiculo: {atributos}")
            print(f"Encontrados{len(veiculos_filtrados)} veículos do tipo '{tipo}'")
        else:
            for veiculo in lista_veiculos:
                atributos = ','.join(f"{atributo} = {valor}" for atributo, valor in veiculo.__dict__.items())
                print(f"Veiculo: {atributos}")
            print(f"Encontrados {len(lista_veiculos)} veiculos no total.")
    def __init__(self,veiculo_id=None, marca=None, modelo=None, categoria=None, transmissao=None, tipo=None, quantidade=None, valor_diaria=None, data_proxima_revisao=None, data_ultima_revisao=None, data_ultima_inspecao=None, is_alugado=0):
        self.veiculo_id = veiculo_id
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

        # Gerar datas aleatórias para as revisões e inspeções dos veículos
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

    @staticmethod
    def get_veiculo(): # função para ir buscar os veículos e juntar a uma lista
        with sqlite3.connect('Database/veiculos.db') as con_veiculo:
            con_veiculo.row_factory = sqlite3.Row
            cursor_veiculo = con_veiculo.cursor()
            cursor_veiculo.execute("SELECT * FROM veiculo")
            rows = cursor_veiculo.fetchall()

        lista_veiculos = []
        for veiculo in rows:
            novo_veiculo = Veiculo(
                veiculo_id=veiculo['veiculo_id'],
                marca=veiculo['Marca'],
                modelo=veiculo['Modelo'],
                categoria=veiculo['Categoria'],
                transmissao=veiculo['Transmissao'],
                tipo=veiculo['Tipo'],
                quantidade=veiculo['Quantidade'],
                valor_diaria=veiculo['valor_diaria'],
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
                cursor_veiculo.execute("SELECT * FROM veiculo WHERE veiculo_id = ?", (self.veiculo_id,))
                resultado_consulta = cursor_veiculo.fetchone()

            # caso o veículo seja encontrado pelo id, atualiza a informação a db
            if resultado_consulta:
                resultado_query = """UPDATE veiculo SET Marca = ?, Modelo = ?, Categoria = ?, Transmissao = ?, 
                                    Tipo = ?, Quantidade = ?, valor_diaria = ?, Ultima_Revisao = ?, Proxima_Revisao = ?, 
                                    Ultima_Inspecao = ?, is_alugado = ? WHERE veiculo_id = ?"""
                #print("Veículo encontrado. A atualizar") -> DEBUG

                cursor_veiculo.execute(resultado_query, (self.marca, self.modelo, self.categoria,
                                                          self.transmissao, self.tipo, self.quantidade,
                                                          self.valor_diaria, self.data_ultima_revisao,
                                                          self.data_proxima_revisao, self.data_ultima_inspecao,
                                                          self.is_alugado, self.veiculo_id))
                con_veiculo.commit()
                #print("Veículo atualizado com sucesso.") -> DEBUG
            # caso o veículo não seja encontrado pelo id, insere a informação na db
            else:
                cursor_veiculo.execute("""INSERT INTO veiculo(Marca, Modelo, Categoria, Transmissao, Tipo, Quantidade, valor_diaria, Ultima_Revisao, Proxima_Revisao, Ultima_Inspecao, is_alugado)
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
                    WHERE veiculo_id NOT IN (
                        SELECT MIN(veiculo_id)
                        FROM veiculo
                        GROUP BY Marca, Modelo, Categoria, Transmissao, Tipo, Quantidade, valor_diaria, Ultima_Revisao, Proxima_Revisao, Ultima_Inspecao, is_alugado
                    )
                """)
                con_veiculo.commit()
                #print("Registos duplicados foram removidos com sucesso.") -> DEBUG
        except sqlite3.Error as error:
            print("Erro: ", error)


class User: # criação da classe User com os parâmetros que vão ser usados na DB
    def __init__(self, primeiro_nome, apelido, password, email):
        self.primeiro_nome = primeiro_nome
        self.apelido = apelido
        self.password = password
        self.email = email


    def verificar_credenciais(self): # Função para verificar se o email já se encontra presente na DB
        with sqlite3.connect('Database/users.db') as con_user:
            con_user.row_factory = sqlite3.Row
            cursor_user = con_user.cursor()
            cursor_user.execute("SELECT * FROM User WHERE email = ?", (self.email,))
            return cursor_user.fetchone() is not None

    def criar_user(self): # Se o email não estiver na DB, criar um novo User
        if self.verificar_credenciais():
            return False,"Este email já existe"

        with sqlite3.connect('Database/users.db') as con_user:
            con_user.row_factory = sqlite3.Row
            cursor_user = con_user.cursor()
            cursor_user.execute(""" INSERT INTO User (primeiro_nome, apelido, password, 
                                                            email)
                    VALUES (?, ?, ?, ?) """,
                                (self.primeiro_nome, self.apelido, self.password,
                                 self.email))
            con_user.commit()
            return True, "Utilizador criado com sucesso."

    def atualizar_user(self): # Função para atualizar caso não exista esse User
        try:
            with sqlite3.connect('Database/users.db') as con_user:
                con_user.row_factory = sqlite3.Row
                cursor_user = con_user.cursor()
                query = "UPDATE user SET primeiro_nome = ?, apelido = ?, password = ?, email = ? WHERE email = ?"
                cursor_user.execute("SELECT * FROM user WHERE email = ?", (self.email,))
                resultado_consulta = cursor_user.fetchone()

                if resultado_consulta:
                    cursor_user.execute(query, (self.primeiro_nome, self.apelido, self.password,
                                                self.email))
                    con_user.commit()
                   # print("Os seus dados foram atualizados com sucesso")  -> DEBUG
        except sqlite3.Error as error:
            print("Erro ao atualizar os seus dados", error)

class Reservas: # Criação da classe reservas, onde serão tratados
    def __init__(self, reserva_id,email, pagamento, data_inicio, data_final, veiculo_id, valor_pagar):
        self.reserva_id = reserva_id
        self.email = email
        self.pagamento = pagamento
        self.data_inicio = data_inicio
        self.data_final = data_final
        self.veiculo_id = veiculo_id
        self.valor_pagar = valor_pagar

    def criar_reserva(self, email, veiculo_id, data_inicio, data_final, pagamento, valor_pagar):
        try:
            with sqlite3.connect('Database/reservas.db') as con_reservas:
                cursor_reservas = con_reservas.cursor()
                cursor_reservas.execute("""INSERT INTO reserva (email,
                                        veiculo_id, data_inicio, data_final,
                                        pagamento, valor_pagar) VALUES 
                                        (?,?,?,?,?,?)""", (email, veiculo_id,
                                                           data_inicio, data_final, pagamento,
                                                           valor_pagar))
                con_reservas.commit()
                return True, "Reserva criada com sucesso"
        except sqlite3.Error as error:
            print(f"Erro ao criar a reserva: {error}")
            return False,"\nTente novamente"

    def atualizar_reserva(self):
        try:
            with sqlite3.connect('Database/reservas.db') as con_reservas:
                cursor_reserva = con_reservas.cursor()
                query = """UPDATE reserva SET data_inicio = ?, data_final = ?, valor_pagar = ? WHERE reserva_id = ?"""
                cursor_reserva.execute("""SELECT * FROM reserva WHERE reserva_id = ?""", (self.reserva_id,))
                resultado_consulta = cursor_reserva.fetchone()

                if resultado_consulta:
                    cursor_reserva.execute(query,(self.data_inicio,self.data_final, self.valor_pagar))
                    con_reservas.commit()

        except sqlite3.Error as error:
            print("Erro ao atualizar os seus dados", error)

    def cancelar_reserva(self):
        try:
            with sqlite3.connect('Database/reservas.db') as con_reservas:
                cursor_reserva = con_reservas.cursor()
                cursor_reserva.execute("DELETE FROM reserva WHERE reserva_id = ?", (self.reserva_id,))
                con_reservas.commit()

        except sqlite3.Error as error:
            print("Erro ao atualizar os seus dados", error)

class CartaoCredito:
    def __init__(self, numero_id, nome_cartao, mes, ano, cvv):
        self.numero_id = numero_id
        self.nome_cartao = nome_cartao
        self.mes = mes
        self.ano = ano
        self.cvv = cvv

    def info_cartao(self): # função para inserir os dados do cartão na base de dados
        try:
            with sqlite3.connect('Database/cartoes.db') as con_cartao:
                con_cartao.row_factory = sqlite3.Row
                cursor_cartao = con_cartao.cursor()
                cursor_cartao.execute("""INSERT INTO cartao (numero_id, nome_cartao, mes, ano, cvv) 
                                            VALUES (?,?,?,?,?)""",(self.numero_id, self.nome_cartao,
                                                                   self.mes, self.ano, self.cvv))
                con_cartao.commit()
                return True,"Cartão inserido com sucesso"

        except sqlite3.Error as e:
            print(f"Erro ao inserir as informações do cartão: {e}")
            return False,"\nTente novamente."

    def atualizar_info(self):
        try:
            with sqlite3.connect('Database/cartoes.db') as con_cartao:
                con_cartao.row_factory = sqlite3.Row
                cursor_cartao = con_cartao.cursor()
                query = ("""UPDATE cartao SET numero_id = ?, mes = ?, ano = ?, cvv = ? WHERE nome_cartao = ?""")
                cursor_cartao.execute("""SELECT * FROM cartao WHERE nome_cartao = ?""",(self.nome_cartao,))
                resultado_consulta = cursor_cartao.fetchone()

                if resultado_consulta:
                    cursor_cartao.execute(query,(self.numero_id, self.mes, self.ano, self.cvv))
                    con_cartao.commit()
        except sqlite3.Error as e:
            return f"Erro ao atualizar a reserva: {e}. \nTente novamente."

    def apagar_info(self):
        try:
            with sqlite3.connect('Database/cartoes.db') as con_cartao:
                con_cartao.row_factory = sqlite3.Row
                cursor_cartao = con_cartao.cursor()
                cursor_cartao.execute("""DELETE FROM cartao WHERE numero_id = ?""",(self.numero_id,))
                con_cartao.commit()

        except sqlite3.Error as e:
            return f"Erro ao apagar a reserva: {e}. \nTente novamente."


 # ----------------- CLASSES E SUAS CARACTERÍSTICAS E FUNCIONALIDADES ----------------- #

# ---------------------------------------------------------- CRIAÇÃO DOS VEÍCULOS ---------------------------------------------------------- #
lista_veiculos = [
    Veiculo(1116,'Toyota', 'Yaris','Médio','Manual','Carro',5,12,None,None,None,0),
    Veiculo(1117,'Ford','Focus','Médio','Manual','Carro',9,15,None,None,None, 0),
    Veiculo(1118,'Citroen','C4','Grande','Automática','SUV',9,20,None,None,None, 0),
    Veiculo(1119,'Mini','Cooper','Pequeno','Manual','Carro',4,7,None,None,None, 0),
    Veiculo(1120,'Nissan','Qashqai','Grande','Automática','SUV',9,15,None,None,None, 0),
    Veiculo(1121,'BMW','F800 GS','Única','Manual','Mota',1,16,None,None,None, 0),
    Veiculo(1122,'Honda','CRF 230F','Única','Automática','Mota',1,16,None,None,None, 0)
    ]

for veiculo in lista_veiculos:
    veiculo.info_veiculo()
    veiculo.remover_duplicados()
    veiculo.get_veiculo()

Veiculo.catalogar_veiculos(lista_veiculos)
Veiculo.catalogar_veiculos(lista_veiculos, tipo='Carro') #Ficaram para DEBUG

veiculos_filtrados = Veiculo.filtrar_veiculos(lista_veiculos, 'SUV') # Ficou SUV para DEBUG
for veiculo in veiculos_filtrados:
    print(f"Filtrado: {veiculo.marca} {veiculo.modelo}")
# ---------------------------------------------------------- CRIAÇÃO DOS VEÍCULOS ---------------------------------------------------------- #

# Inicializar a aplicação Flask
app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "flask_cookie_secret_key"

# ---------------- FUNCIONALIDADES NECESSÁRIAS PARA A WEBAPP ---------------- #
# fazer o get de todos os veículos da db
def get_all_veiculos():
    with sqlite3.connect('Database/veiculos.db') as con_veiculo:
        con_veiculo.row_factory = sqlite3.Row
        cursor_veiculo = con_veiculo.cursor()
        cursor_veiculo.execute("SELECT veiculo_id, Marca, Modelo, Tipo FROM veiculo WHERE is_alugado = 0")
        veiculos = cursor_veiculo.fetchall()
        return [{"veiculo_id": veiculo["veiculo_id"], "Marca": veiculo["Marca"], "Modelo": veiculo["Modelo"], "Tipo": veiculo["Tipo"]} for veiculo in veiculos]

#fazer o get dos veículos por id
def get_veiculos_by_id(veiculo_id):
    with sqlite3.connect('Database/veiculos.db') as con_veiculo:
        con_veiculo.row_factory = sqlite3.Row
        cursor_veiculo = con_veiculo.cursor()
        cursor_veiculo.execute("SELECT Marca, Modelo, Tipo FROM veiculo WHERE veiculo_id = ? AND is_alugado = 0", (veiculo_id,))
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
        cursor_veiculo.execute("SELECT valor_diaria FROM veiculo WHERE veiculo_id = ?", (veiculo_id,))
        resultado = cursor_veiculo.fetchone()
        return resultado['valor_diaria'] if resultado else None

# Função para fazer o get de todos os veículos alugados
def get_veiculos_alugados():
    with sqlite3.connect('Database/veiculos.db') as con_veiculo:
        con_veiculo.row_factory = sqlite3.Row
        cursor_veiculo = con_veiculo.cursor()
        cursor_veiculo.execute("SELECT Marca, Modelo, Tipo FROM veiculo WHERE is_alugado = 1")
        veiculos = cursor_veiculo.fetchall()
        return [{"Marca": veiculo["Marca"], "Modelo": veiculo["Modelo"], "Tipo": veiculo["Tipo"]} for veiculo in veiculos]
#print(get_veiculos_alugados()) -> DEBUG
# função para marcar o veículo como alugado
def veiculo_alugado(veiculo_id):
    try:
        with sqlite3.connect('Database/veiculos.db') as con_veiculo:
            con_veiculo.row_factory = sqlite3.Row
            cursor_veiculo = con_veiculo.cursor()
            cursor_veiculo.execute("UPDATE veiculo SET is_alugado = 1 WHERE veiculo_id = ?", (veiculo_id,))
            con_veiculo.commit()
    except sqlite3.Error as e:
        print(f"Erro ao alugar o veículo: {e}")

# função para marcar o veículo como disponível na base de dados
def veiculo_disponivel(veiculo_id):
    try:
        with sqlite3.connect('Database/veiculos.db') as con_veiculo:
            con_veiculo.row_factory = sqlite3.Row
            cursor_veiculo = con_veiculo.cursor()
            cursor_veiculo.execute("UPDATE veiculo SET is_alugado = 0 WHERE veiculo_id = ?", (veiculo_id,))
            con_veiculo.commit()
    except sqlite3.Error as e:
        print(f"Erro ao marcar o veículo com disponível: {e}")

# função para calcular o valor da diária
def calcular_diaria(veiculo_id, data_inicio_str, data_final_str):
    try:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        data_final = datetime.strptime(data_final_str, '%Y-%m-%d').date()

        if data_final < data_inicio: # tratamento de exceções
            raise ValueError (f" A data final {data_final} não pode ser anterior à data inicial {data_inicio}")

        # calcular o número de dias
        num_dias = (data_final - data_inicio).days
        # calcular o valor a pagar
        valor_diaria = get_valor_diaria(veiculo_id)
        valor_pagar = valor_diaria * num_dias if valor_diaria is not None else 0.0

        return valor_pagar

    except ValueError as ve:
        print(f"Erro ao validar as datas: {ve}")
        return None
    except Exception as e:
        print(f"Erro ao calcular o valor a pagar: {e}")
        return None


def get_users_by_email(email):
    with sqlite3.connect('Database/users.db') as con_user:
        con_user.row_factory = sqlite3.Row
        cursor_user = con_user.cursor()
        cursor_user.execute("""SELECT * FROM user WHERE email = ?""", (email,))
        user = cursor_user.fetchone()

        if user:
            return {"Primeiro Nome": user["primeiro_nome"],
                     "Apelido": user["apelido"],
                     "Email": user["email"]}
        return None


def get_reservas_by_email(email):
    try:
        with sqlite3.connect('Database/reservas.db') as con_reserva:
            con_reserva.row_factory = sqlite3.Row
            cursor_reserva = con_reserva.cursor()
            cursor_reserva.execute("""SELECT * FROM reserva WHERE email = ?""",(email,))
            reservas = cursor_reserva.fetchall()

            if reservas:
                return [{"Número da Reserva": reserva['reserva_id'],
                        "Email Associado": reserva['email'],
                        "Veículo Selecionado": reserva['veiculo_id'],
                        "Data de Início": reserva['data_inicio'],
                        "Data do Final": reserva['data_final'],
                        "Método de Pagamento": reserva['pagamento'],
                        "Valor a Pagar": reserva['valor_pagar']} for reserva in reservas]
            return []
    except sqlite3.Error as error:
        print(f"Erro ao verificar reservas: {error}")
        return []


# ---------------- FUNCIONALIDADES NECESSÁRIAS PARA A WEBAPP ---------------- #

# ------------------------ ROTAS FLASK ------------------------ #
# Página inicial da webapp
@app.route('/', methods=['GET'])
def homepage():
    return render_template("index.html")

@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']

            with sqlite3.connect('Database/users.db') as con_user:
                cursor_user = con_user.cursor()
                cursor_user.execute(
                "SELECT * FROM user WHERE email = ? AND password = ?",
                        (email, password,))
                dados_user = cursor_user.fetchone()

                if dados_user:
                    #Armazenar as informações
                    session['email'] = email
                    session['password'] = password
                    # Se o user existir, também vai ser redirecionado para a página seguinte
                    return redirect(url_for('selecionar_veiculo'))
                else:
                    flash('Email ou password incorretos,\n Tente novamente.', 'error')
                    return redirect(url_for('login'))

        except Exception as e:
            print(f"Erro ao processar a solicitação {e}.")
            flash('Ocorreu um erro.\n Tente mais tarde', 'error')
            return redirect(url_for('login.html'))
    else:
        return render_template('login.html')

@app.route('/registar_user', methods=['GET', 'POST'])
def registar_user():
    if request.method == 'GET':
        return render_template('registo_user.html')
    elif request.method == 'POST': # Requisitar os dados do User
        primeiro_nome = request.form['primeiro_nome']
        apelido = request.form['apelido']
        password = request.form['password']
        email = request.form['email']

        # Armazenar na sessão através de cookies
        session['primeiro_nome'] = primeiro_nome
        session['apelido'] = apelido
        session['password'] = password
        session['email'] = email

        user = User(primeiro_nome=primeiro_nome, apelido=apelido, password=password, email=email)
        if user:
            user.criar_user()
        else:
            flash('Algo incorreto aconteceu.\n Tente novamente.', 'error')
            return redirect(url_for('registar_user'))

        return redirect(url_for('login', primeiro_nome=primeiro_nome,
                                    apelido=apelido,
                                    email=email,
                                    password=password))


@app.route('/selecionar_veiculo', methods=['GET','POST'])
def selecionar_veiculo():
    try:
        if request.method == 'POST':
            veiculo_id = request.form.get('veiculo_id') # Requisitar qual o veículo pretendido
            session['veiculo_id'] = veiculo_id # Armazenar a escolha através de cookies
            return redirect(url_for('alugar_veiculo', veiculo_id=veiculo_id))

        # Set up dos filtros
        tipo = request.args.get('tipo')
        categoria = request.args.get('categoria')
        valor_diaria = request.args.get('valor_diaria')
        quantidade = request.args.get('quantidade')

        lista_veiculos = Veiculo.get_veiculo()

        # Aplicar os filtros
        if tipo:
            lista_veiculos = [veiculo for veiculo in lista_veiculos if veiculo.tipo == tipo]

        if categoria:
            lista_veiculos = [veiculo for veiculo in lista_veiculos if veiculo.categoria == categoria]

        if valor_diaria:
            lista_veiculos = [veiculo for veiculo in lista_veiculos if str(veiculo.valor_diaria) == valor_diaria]

        if quantidade:
            lista_veiculos = [veiculo for veiculo in lista_veiculos if veiculo.quantidade == quantidade]

        return render_template('selecionar_veiculo.html', veiculos_filtrados=lista_veiculos,
                               tipo=tipo,
                               categoria=categoria,
                               valor_diaria=valor_diaria,
                               quantidade=quantidade)

    except Exception as e:
        return str(e), 500
@app.route('/alugar_veiculo', methods=['GET', 'POST'])
def alugar_veiculo():
    try:
        veiculo_id = session.get('veiculo_id')

        if request.method == 'POST':
            data_inicio_str = request.form.get('data_inicio') #Requisição da data inicial
            data_final_str = request.form.get('data_final') #Requisição da data final
            session['data_inicio'] = data_inicio_str #Armazenamento na sessão através de cookies
            session['data_final'] = data_final_str #Armazenamento na sessão através de cookies

            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
            data_final = datetime.strptime(data_final_str,'%Y-%m-%d')

            # Lidar com exceções
            if data_inicio > data_final:
                flash('A data de início não pode ser inferior à data final.','error')
                return render_template('alugar_veiculo.html')

            elif data_inicio < datetime.now():
                flash('Não é permitido alugar veículos para uma data inferior à presente.', 'error')
                return render_template('alugar_veiculo.html')

            elif data_inicio == data_final:
                flash('Erro: Veículo não disponível','error')
                return render_template('alugar_veiculo.html')

            return redirect(url_for('pagamento', veiculo_id=veiculo_id, data_inicio=data_inicio, data_final=data_final))
        return render_template('alugar_veiculo.html', veiculo_id=veiculo_id)

    except Exception as e:
        print(f"Erro ao processar a solicitação {e}")
        return str(e), 500

@app.route('/pagamento', methods = ['GET','POST'])
def pagamento():
    if request.method == 'GET':
        return render_template('pagamento.html')

    if request.method == 'POST':
        # Requisição dos dados necessários em baixo
        pagamento = request.form.get('pagamento')
        veiculo_id = session.get('veiculo_id')
        data_inicio_str = session.get('data_inicio')
        data_final_str = session.get('data_final')

        if veiculo_id and data_inicio_str and data_final_str: # chamada da função para calcular a diária automaticamente
            valor_pagar = calcular_diaria(veiculo_id, data_inicio_str, data_final_str)

        if valor_pagar is not None:
            session['valor_pagar'] = valor_pagar # Armazenamento do valor_pagar através de cookies
            session['pagamento'] = pagamento # Armazenamento através de cookies

        else:
            flash('Erro ao calcular o valor a pagar', 'error')
            return redirect(url_for('pagamento'))

        if pagamento == 'Cartão de Crédito/Débito':
           return redirect(url_for('cartao_credito', pagamento=pagamento))

        #print(f"Selecionou {pagamento} como método de pagamento.")  -> DEBUG
        #print("O valor a pagar vai ser apresentado à frente.")  -> DEBUG
        else:
            return redirect(url_for('resumo_aluguer', pagamento=pagamento, valor_pagar=valor_pagar))

    else:
        flash('Dados incompletos.', 'error')
        return redirect(url_for('pagamento'))

@app.route('/resumo_aluguer', methods = ['GET'])
def resumo_aluguer():
    try: # Passagem de todos os parâmetros que foram recolhidos para a página final
        # Fazer o display de tudo para o cliente rever as suas opções
        password = session.get('password')
        email = session.get('email')
        veiculo_id = session.get('veiculo_id')
        data_inicio_str = session.get('data_inicio') #converter para dt(datetime)
        data_final_str = session.get('data_final') #converter para dt(datetime)
        pagamento = session.get('pagamento')
        valor_pagar = session.get('valor_pagar')

        # Tratamento de exceções
        if email is None or password is None:
            print("Por favor, introduza credenciais válidas.")
            return redirect(url_for('login'))

        elif veiculo_id is None:
            print("Por favor selecione um veículo válido.")
            return redirect(url_for('selecionar_veiculo'))

        elif data_inicio_str is None or data_final_str is None:
            print("Por favor, selecione as datas pretendidas.")
            return redirect(url_for('alugar_veiculo'))

        elif pagamento is None or valor_pagar is None:
            print("Por favor, selecione o método de pagamento.")
            return redirect(url_for('pagamento'))

        # Fazer o display das informações requeridas em baixo
        veiculo = get_veiculos_by_id(veiculo_id)
        if veiculo:
            marca = veiculo["Marca"]
            modelo = veiculo["Modelo"]
        else:
            marca = "Desconhecido"
            modelo = "Desconhecido"

        # Marcação do veículo selecionado como alugado
        veiculo_alugado(veiculo_id)

        return render_template('resumo_aluguer.html',email=email,
                               veiculo_id=veiculo_id, marca=marca, modelo=modelo,
                               data_inicio=data_inicio_str, data_final=data_final_str,
                               pagamento=pagamento, valor_pagar=valor_pagar)
    except ValueError as v:
        print(f"Erro ao converter as datas {v}")
        return str(v), 500
    except Exception as e:
        print(f"Erro ao finalizar o processo {e}")
        return str(e), 500

# Página que termina o processo
@app.route('/aluguer_sucesso', methods =['GET', 'POST'])
def aluguer_sucesso():
    if request.method == 'GET':
        return render_template('aluguer_sucesso.html')

    if request.method == 'POST':
        return redirect(url_for('portal_user'))

# ----------------- ACIMA ESTÃO AS FUNCIONALIDADES DE "PRIMEIRA RESERVA" PELA ORDEM DAS PÁGINAS ----------------- #
@app.route('/portal_user', methods = ['GET','POST'])
def portal_user():
    email = session.get('email')
    if not email:
        flash('Email não encontrado.\nTente novamente.', 'error')
        return redirect(url_for('login'))

    user = get_users_by_email(email)
    if not user:
        flash('Utilizador não encontrado.', 'warning')
        return redirect(url_for('login'))

    primeiro_nome = user['Primeiro Nome']
    apelido = user['Apelido']

    if request.method == 'GET':
        with sqlite3.connect('Database/reservas.db') as con_reservas:
            con_reservas.row_factory = sqlite3.Row
            cursor_reservas = con_reservas.cursor()
            cursor_reservas.execute("""SELECT * FROM reserva WHERE email = ?""",(email,))
            reservas = cursor_reservas.fetchall()

        if not reservas:
            flash('Nenhuma reserva encontrada.','warning')
            reservas = []

        reservas_detalhadas = []
        for reserva in reservas:
            veiculo_id = reserva['veiculo_id']
            with sqlite3.connect('Database/veiculos.db') as con_veiculos:
                con_veiculos.row_factory = sqlite3.Row
                cursor_veiculos = con_veiculos.cursor()
                cursor_veiculos.execute("""SELECT Marca, Modelo FROM veiculo WHERE veiculo_id = ?""",
                                        (veiculo_id,))
                veiculo = cursor_veiculos.fetchone()

            if veiculo:
                marca = veiculo["Marca"]
                modelo = veiculo["Modelo"]
            else:
                marca = "Desconhecido"
                modelo = "Desconhecido"

            reserva_detalhada = {
                'reserva_id': reserva['reserva_id'],
                'data_inicio': reserva['data_inicio'],
                'data_final' : reserva['data_final'],
                'pagamento' : reserva['pagamento'],
                'valor_pagar' : reserva['valor_pagar'],
                'marca' : marca,
                'modelo' : modelo,
                'veiculo_id' : veiculo_id
            }

            reservas_detalhadas.append(reserva_detalhada)

        return render_template('portal_user.html',
                primeiro_nome=primeiro_nome,
                apelido=apelido,
                user=user,
                reservas=reservas_detalhadas)

    if request.method == 'POST':
        reserva_id = request.form.get('reserva_id')
        choice = request.form.get('choice')

        session['reserva_id'] = reserva_id

        if not reserva_id:
            flash('Reserva não encontrada', 'warning')
            return redirect(url_for('portal_user'))

        if choice == 'editar':
            return redirect(url_for('editar_reserva', reserva_id=reserva_id))

        elif choice == 'cancelar':
            return redirect(url_for('cancelar_reserva', reserva_id=reserva_id))

        elif choice == 'nova_reserva':
            return redirect(url_for('nova_reserva'))

        return redirect(url_for('portal_user', reserva_id=reserva_id))

@app.route('/confirmar_reserva', methods = ['POST'])
def confirmar_reserva(): # rota para atualizar base de dados
    email = session.get('email')
    veiculo_id = session.get('veiculo_id')
    data_inicio = session.get('data_inicio')
    data_final = session.get('data_final')
    pagamento = session.get('pagamento')
    valor_pagar = session.get('valor_pagar')


    if not all([email, veiculo_id, data_inicio, data_final, pagamento,valor_pagar]):
        flash('Dados incompletos, para terminar o processo', 'error')
        return redirect(url_for('resumo_aluguer'))

    try:
        with sqlite3.connect('Database/reservas.db') as con_reserva:
            cursor_reserva = con_reserva.cursor()
            cursor_reserva.execute("""INSERT INTO reserva (email, veiculo_id, data_inicio, 
            data_final, pagamento, valor_pagar) VALUES (?,?,?,?,?,?)""",
                (email, veiculo_id, data_inicio, data_final, pagamento, valor_pagar))
            con_reserva.commit()

        flash('Reserva confirmada com sucesso', 'success')
        return redirect(url_for('aluguer_sucesso'))

    except sqlite3.Error as e:
        print(f"Erro ao atualizar a reserva {e}")
        flash('Erro ao confimar a reserva', 'error')
        return redirect(url_for('resumo_aluguer'))

@app.route('/editar_reserva', methods = ['GET', 'POST'])
def editar_reserva():
    if request.method == 'GET':
        return render_template('editar_reserva.html')

    if request.method == 'POST': #recolher os dados necessários para identificar a reserva
        reserva_id = request.form.get('reserva_id')
        session['reserva_id'] = reserva_id #recolher a reserva_id e armazenar através das cookies

        if reserva_id:
            # Vamos agora aceder à base de dados para o programa identificar o user através do ID da reserva
            try:
                with sqlite3.connect('Database/reservas.db') as con_reserva:
                    cursor_reserva = con_reserva.cursor()
                    cursor_reserva.execute("""SELECT veiculo_id, data_inicio, data_final, pagamento, valor_pagar
                                        FROM reserva WHERE reserva_id = ?""",
                                           (reserva_id,))
                    dados_reserva = cursor_reserva.fetchone()

                    if dados_reserva:
                        session['veiculo_id'] = dados_reserva[0]
                        session['data_inicio'] = dados_reserva[1]
                        session['data_final'] = dados_reserva[2]
                        session['pagamento'] = dados_reserva[3]
                        session['valor_pagar'] = dados_reserva[4]

                        return redirect(url_for('atualizar_reserva'))
                    else:
                        flash(f'Reserva {reserva_id} não encontrado', 'error')
                        return redirect(url_for('editar_reserva'))
            except sqlite3.Error as e:
                return f"Erro ao encontrar reserva requisitada: {e}"
        else:
            flash('Reserva não encontrada.\nTente novamente.', 'error')
            return render_template('editar_reserva.html')


@app.route('/atualizar_reserva', methods = ['GET', 'POST'])
def atualizar_reserva():
    if request.method == 'GET':
        return render_template('alterar_datas.html')

    if request.method == 'POST':
        new_data_inicio = request.form.get('data_inicio')
        new_data_final = request.form.get('data_final')
        veiculo_id = session.get('veiculo_id')

        if not (new_data_inicio and new_data_final):
            flash('Por favor, preencha os campos todos', 'error')
            return render_template('alterar_datas.html')

        if new_data_inicio > new_data_final:
            flash('A data de início não pode ser superior à data final','error')
            return render_template('alterar_datas.html')

        try:
            reserva_id = session.get('reserva_id')

            #print(reserva_id)  -> DEBUG

            if reserva_id:
                # Recalcular o novo valor a pagar
                new_valor_pagar = calcular_diaria(veiculo_id, new_data_inicio, new_data_final)

                with sqlite3.connect('Database/reservas.db') as con_reserva:
                    cursor_reserva = con_reserva.cursor()
                    cursor_reserva.execute("""UPDATE reserva
                                            SET data_inicio = ?, data_final = ?, valor_pagar = ? 
                                            WHERE reserva_id = ?""",
                                        (new_data_inicio, new_data_final, new_valor_pagar, reserva_id))
                    con_reserva.commit()


            #Agora vamos atualizar a sessão
            session['data_inicio'] = new_data_inicio
            session['data_final'] = new_data_final
            session['valor_pagar'] = new_valor_pagar

            flash('Reserva atualizada com sucesso', 'success')

            return redirect(url_for('resumo_aluguer_editar'))

        except sqlite3.Error as e:
            flash(f"Erro ao atualizar a reserva: {e}")
            return render_template('alterar_datas.html')
@app.route('/resumo_aluguer_editar', methods = ['GET'])
def resumo_aluguer_editar():
    try: # Passagem de todos os parâmetros que foram recolhidos
        # Fazer o display de tudo para o cliente rever as suas opções
        data_inicio = session.get('data_inicio')
        data_final = session.get('data_final')
        valor_pagar = session.get('valor_pagar')

        if not (data_inicio and data_final and valor_pagar):
            flash('Erro ao carregar os detalhes.\nTente novamente.','error')
            return redirect(url_for('editar_reserva'))

        return render_template('resumo_aluguer_editar.html',
                               data_inicio=data_inicio, data_final=data_final, valor_pagar=valor_pagar)
    except Exception as e:
        print(f"Erro ao finalizar o processo {e}")
        return str(e), 500

@app.route("/cancelar_reserva", methods = ['GET','POST'])
def cancelar_reserva():
    if request.method == 'GET':
        return render_template('cancelar_reserva.html')

    if request.method == 'POST':
        #reserva_id = session.get('reserva_id')
        reserva_id = request.form.get('reserva_id')
        #print(reserva_id) -> DEBUG

        if not reserva_id:
            flash('Reserva não encontrada.','error')
            return redirect(url_for('portal_user'))

        if reserva_id:
        # Vamos agora aceder à base de dados para o programa identificar
        # a reserva através do ID da reserva
            try:
                with sqlite3.connect('Database/reservas.db') as con_reserva:
                    cursor_reserva = con_reserva.cursor()
                    cursor_reserva.execute("""SELECT veiculo_id, data_inicio, data_final, pagamento, valor_pagar
                                            FROM reserva WHERE reserva_id = ?""",
                                                   (reserva_id,))
                    dados_reserva = cursor_reserva.fetchone()

                if dados_reserva:
                    session['veiculo_id'] = dados_reserva[0]
                    session['data_inicio'] = dados_reserva[1]
                    session['data_final'] = dados_reserva[2]
                    session['pagamento'] = dados_reserva[3]
                    session['valor_pagar'] = dados_reserva[4]

                    # Marcar veiculo como disponivel
                    veiculo_disponivel(dados_reserva[0])

                    # Apagar veiculo da db
                    cursor_reserva.execute("""DELETE FROM reserva WHERE reserva_id = ?""", (reserva_id,))
                    con_reserva.commit()

                    flash('Reserva cancelada com sucesso.', 'success')
                    return redirect(url_for('cancelar_sucesso'))

                else:
                    flash(f'Reserva {reserva_id} não encontrado', 'error')
                    return redirect(url_for('portal_user'))

            except sqlite3.Error as error:
                flash(f"Erro a cancelar a reserva: {error}.", 'error')
                return redirect(url_for('portal_user'))


@app.route('/cancelar_sucesso', methods=['GET','POST'])
def cancelar_sucesso():
    if request.method == 'GET':
        return render_template('cancelar_sucesso.html')
    if request.method == 'POST':
        return redirect(url_for('portal_user'))

@app.route('/editar_sucesso', methods=['GET', 'POST'])
def editar_sucesso():
    return render_template('editar_sucesso.html')

@app.route('/cartao_credito', methods=['GET', 'POST'])
def cartao_credito():
    if request.method == 'GET':
        pagamento = session.get('pagamento')
        return render_template('cartao_credito.html', pagamento=pagamento)

    if request.method == 'POST':
        numero_id = request.form['numero_id']
        nome_cartao = request.form['nome_cartao']
        mes = request.form['mes']
        ano = request.form['ano']
        cvv = request.form['cvv']

        # Validação de todos os campos
        if not all([numero_id, nome_cartao, mes, ano, cvv]):
            flash('Por favor, preencha todos os campos','warning')
            return render_template('cartao_credito.html')

        # Validação do número do cartão
        if len(numero_id) != 16 or not numero_id.isdigit():
            flash('O número do cartão tem de conter 16 dígitos', 'error')
            return render_template('cartao_credito.html')

        # Validação da data de validade
        try:
            data_validade_str =f"{mes}/{ano}"
            data_validade = datetime.strptime(data_validade_str, '%m/%Y').date()

            data_hoje = datetime.now().date()

            if data_validade < data_hoje:
                flash('O cartão apresentado já expirou.', 'warning')
                return render_template('cartao_credito.html')
        except ValueError:
            flash('Data de validade inválida.','error')
            return render_template('cartao_credito.html')

        # Validação do nome do cartão
        if not all(cartao.isalpha() or cartao.isspace() for cartao in nome_cartao):
            flash('O nome apenas pode conter letras','warning')
            return render_template('cartao_credito.html')

        # Validação do cvv
        if len(cvv) != 3 or not cvv.isdigit():
            flash('O cvv deve conter 3 dígitos','error')
            return render_template('cartao_credito.html')

        # Inserção dos dados na base de dados
        cartao = CartaoCredito(numero_id=numero_id, nome_cartao=nome_cartao,
                               mes=mes, ano=ano,cvv=cvv)
        sucesso, mensagem = cartao.info_cartao()

        if sucesso:
            flash(mensagem,'success')
            return redirect(url_for('cartao_sucesso'))
        else:
            flash(mensagem,'error')
            return redirect(url_for('cartao_fail'))

@app.route('/cartao_sucesso', methods=['GET'])
def cartao_sucesso():
    return render_template('cartao_sucesso.html')
@app.route('/cartao_fail', methods=['GET'])
def cartao_fail():
    return render_template('cartao_fail.html')
@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return render_template('logout.html')
@app.route('/nova_reserva', methods=['POST'])
def nova_reserva():
    email = session.get('email')
    if email:
        return redirect(url_for('selecionar_veiculo'))

    else:
        flash('Algo correu mal.\nTente novamente','error')
        return redirect(url_for('portal_user'))

@app.route("/veiculos_alugados", methods = ['GET'])
def check_veiculos_alugados():
    if request.method == 'GET':
        veiculos = get_veiculos_alugados()
        if veiculos:
           return render_template('veiculos_alugados.html', veiculos=veiculos)
        else:
            flash('Todos os veículos estão disponíveis', 'warning')
            return render_template('veiculos_alugados.html', veiculos=[])

# ------------------------ ACIMA ESTÃO AS FUNCIONALIDADES PARA EDITAR, CANCELAR, FILTRAR E VER VEÍCULOS ALUGADOS ------------------------ #
# ------------------------ FIM DAS ROTAS FLASK ------------------------ #


# Função criada para DEBUG que foi deixada como memento daquilo que se deve fazer no futuro
# Deixada aqui para servir de exemplo em prática profissional futura
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