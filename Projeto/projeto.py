import psycopg2
import os
import random
import tkinter as tk
from tkinter import messagebox
import datetime
from datetime import datetime, timedelta,time
import hashlib

# Inputs do cliente para criar a conta
def limpar_ecra():
    # Limpa a tela da console
    os.system('cls' if os.name == 'nt' else 'clear')





#FUNÇÕES DE LOGIN E CRIAR CONTA -------------------------------------------------------

def fazer_login(conn1, cur):
    print(" Por favor, faça login.")
    while True:
        email = input("Digite seu mail de usuário: ")
        senha = input("Digite sua senha: ")
        if autenticar_usuario(conn, cur, email, senha):
                return obter_id_por_email(conn, cur, email)
            
            
def obter_id_por_email(conn, cur, email):
    try:
        # Consulta o banco de dados para obter o ID associado ao e-mail fornecido
        cur.execute("SELECT ID_usuario FROM usuario WHERE email = %s", (email,))
        resultado = cur.fetchone()

        if resultado:
            # Extrai o ID do usuário do resultado da consulta
            id_usuario = resultado[0]
            return id_usuario
        else:
            print("E-mail não encontrado.")
            return None

    except (Exception, psycopg2.Error) as error:
        print("Erro ao obter ID por e-mail:", error)
        return None


def autenticar_usuario(conn, cur, email, senha):
    try:
        # Consulta o banco de dados para obter o nome do usuário e a senha encriptada associada ao email fornecido
        cur.execute("SELECT nome, pass FROM usuario WHERE email = %s", (email,))
        resultado = cur.fetchone()

        if resultado:
            # Extrai o nome do usuário e a senha encriptada do resultado da consulta
            nome_usuario = resultado[0]
            senha_armazenada = resultado[1]
            
            # Encripta a senha fornecida pelo usuário
            senha_encriptada = encriptar_senha(senha)

            # Compara a senha encriptada fornecida pelo usuário com a senha encriptada armazenada no banco de dados
            if senha_encriptada == senha_armazenada:
                limpar_ecra()
                print(f"Bem-vindo, {nome_usuario}! Autenticação bem-sucedida.")
                return True
            else:
                print("Senha incorreta. Tente novamente.")
                return False
        else:
            print("Usuário não encontrado.")
            return False

    except (Exception, psycopg2.Error) as error:
        print("Erro ao autenticar usuário:", error)
        return False


def encriptar_senha(senha):
    # Criptografa a senha utilizando SHA-256
    senha_encriptada = hashlib.sha256(senha.encode()).hexdigest()
    return senha_encriptada
            
    
def verificar_senha_complexa(conn, cur, senha):
    try:
        cur.execute("SELECT verificar_senha_complexa(%s)", (senha,))
        resultado = cur.fetchone()[0]  # Obtém o resultado da função SQL
        return resultado  # Retorna True ou False dependendo do resultado da função
    except (Exception, psycopg2.Error) as error:
        print("Erro ao verificar senha complexa:", error)
        return False    
    
            
def gerar_novo_id(cur):
    novo_id = random.randint(100000, 999999)  # Gera um novo ID aleatório de 6 dígitos
    cur.execute("SELECT ID_usuario FROM usuario WHERE ID_usuario = %s", (novo_id,))
    if cur.fetchone():
        # Se o ID já existe, chama recursivamente a função para gerar outro ID
        return gerar_novo_id(cur)
    else:
        return novo_id


def verificar_nif_formato(nif):
    return len(nif) == 9 and nif.isdigit()


def verificar_nif_existente(conn, cur, nif):
    cur.execute("SELECT NIF FROM usuario WHERE NIF = %s", (nif,))
    return cur.fetchone()


def criar_conta(conn, cur):
    limpar_ecra()
    print(" Por favor, preencha o formulário abaixo para criar sua conta.")
    nome = input("Digite seu nome: ")
    while True:
        limpar_ecra()
        senha = input("Digite sua senha (necessita de uma sequencia numerica que nao seja 123, uma letra maiuscula,um caracter especial, 8 caracteres minimo): ")
        resultado = verificar_senha_complexa(conn, cur, senha)
        if resultado:
            print("A senha é apta para guardar a sua conta!")
            break
        else:
            print("A senha nao esta de acordo com os critérios mencionados. Por favor, insira outra.")
       
    senha=encriptar_senha(senha)
    email = input("Digite seu email: ")
    while True:
        # Chama a função verificar_email_existente para garantir que o email seja único
        email = verificar_email_existente(conn, cur, email)
        if email:  # Verifica se o email retornado é válido
            break  # Sai do loop se o email for único e válido
        
    while True:
        NIF = input("Digite seu NIF (9 dígitos): ")
        limpar_ecra()
        if not verificar_nif_formato(NIF):
            print("Formato de NIF inválido. Deve conter 9 dígitos numéricos.")
            continue
        if verificar_nif_existente(conn, cur, NIF):
            print("Este NIF já está em uso. Por favor, digite um novo.")
        else:
            break

    while True:
        telefone = input("Digite seu número de telefone (9 dígitos): ")
        limpar_ecra()
        
        if not verificar_telefone_formato(telefone):
            print("Formato de telefone inválido. Deve conter 9 dígitos numéricos.")
            continue
        else:
            break

    # Gerar um novo ID de usuário único
    novo_id = gerar_novo_id(cur)

    # Inserir o novo usuário na tabela 'usuario' com o ID gerado
    cur.execute('''INSERT INTO usuario (ID_usuario, pass, nome, email, NIF) 
                    VALUES (%s, %s, %s, %s, %s)''', (novo_id, senha, nome, email, NIF))

    # Inserir o novo usuário na tabela 'clientes' com o ID de usuário e telefone
    cur.execute('''INSERT INTO cliente (usuario_id_usuario, telefone) 
                    VALUES (%s, %s)''', (novo_id, telefone))
    
    conn.commit()
    print("Conta criada com sucesso! Seu ID de usuário é:", novo_id)
    op3=("Presssione qualquer tecla: ")
    
    return novo_id



def verificar_telefone_formato(telefone):
    # Verifica se o telefone tem 9 dígitos
    if len(telefone) != 9:
        return False

    # Verifica se todos os caracteres são dígitos
    if not telefone.isdigit():
        return False

    return True



def verificar_email_existente(conn, cur, email):
    while True:
        try:
            # Executar a consulta SQL para verificar se o e-mail existe na tabela Usuario
            cur.execute("SELECT COUNT(*) FROM Usuario WHERE email = %s", (email,))
            email_count = cur.fetchone()[0]

            # Se o e-mail existir, pedir ao usuário para inserir outro e-mail
            if email_count > 0:
                print("Mail já existente! Por favor, insira outro.")
                email = input("Digite outro e-mail: ")

            else:
                return email  # Retornar o e-mail único

        except psycopg2.IntegrityError as error:
            # Se ocorrer um erro de violação de integridade, exibir mensagem de erro e continuar o loop
            print("Por favor insira outro mail pois esse já existe:", error)
            continue


#---------------------------------------------------------------------------------------


#FUNÇÕES DE MOSTRAR O PERFIL--------------------------------------------------------------

def exibir_perfil(ID_usuario):
    try:
        # Conexão com o banco de dados
        conn = psycopg2.connect("host=localhost dbname=Padel_Mondego user=postgres password=postgres")
        cur = conn.cursor()

        # Obtendo os dados do perfil com base no ID de usuário
        dados = obter_dados_perfil(conn, cur, ID_usuario)

        if dados:
            # Criar uma janela para exibir o perfil
            janela_perfil = tk.Tk()
            janela_perfil.title("Perfil de Usuário")

            # Exibir nome, ID de usuário, NIF e email
            tk.Label(janela_perfil, text="Nome:").grid(row=0, column=0, sticky="w")
            tk.Label(janela_perfil, text=dados[0]).grid(row=0, column=1, sticky="w")
            tk.Label(janela_perfil, text="ID de Usuário:").grid(row=1, column=0, sticky="w")
            tk.Label(janela_perfil, text=ID_usuario).grid(row=1, column=1, sticky="w")
            tk.Label(janela_perfil, text="NIF:").grid(row=2, column=0, sticky="w")
            tk.Label(janela_perfil, text=dados[1]).grid(row=2, column=1, sticky="w")
            tk.Label(janela_perfil, text="Email:").grid(row=3, column=0, sticky="w")
            tk.Label(janela_perfil, text=dados[2]).grid(row=3, column=1, sticky="w")

            janela_perfil.mainloop()
        else:
            messagebox.showerror("Erro", "Nenhum usuário encontrado com o ID fornecido.")
            opp=input("PRESSIONE QUALQUER TECLA: ")

    except psycopg2.Error as e:
        messagebox.showerror("Erro", "Erro ao conectar ao banco de dados: {}".format(e))
        opp=input("PRESSIONE QUALQUER TECLA: ")


    finally:
        # Fechar conexão com o banco de dados
        if conn:
            cur.close()
            conn.close()


def obter_dados_perfil(conn, cur, ID_usuario):
    cur.execute("SELECT nome, NIF, email FROM usuario WHERE ID_usuario = %s", (ID_usuario,))
    dados = cur.fetchone()
    return dados


def obter_nome_usuario_por_id(conn, cur, ID_usuario):
    cur.execute("SELECT nome FROM usuario WHERE ID_usuario = %s", (ID_usuario,))
    nome = cur.fetchone()
    if nome:
        return nome[0]  # Retorna o nome do usuário
    else:
        return None  # Retorna None se o ID de usuário não existir na base de dados


#--------------------------------------------------------------------------------



#FUNCÕES DE MENU---------------------------------------------------------------------

def menu_Cliente (op,cur ,id_usuario):
    limpar_ecra()
    atualizar_disponibilidade_reservas(op,cur)
    nome=obter_nome_usuario_por_id(op,cur,id_usuario)
    while True:
        limpar_ecra()
        # Chamar a função para criar a conta do cliente
        print("Bem-Vindo ",nome)
        print("O seu ID:",id_usuario)
        print("1- Fazer Reserva")
        print("2- Ver Reservas Futuras")
        print("3- Histórico de Reservas ")
        print("4- Mensagens")
        print("5- Perfil")
        print("6- Sair")
        op= input("->:")
   
        if op=="1":
            limpar_ecra()
            print("Opções de Reserva: ")
            print("1-Dia de Hoje")
            print("2-Noutro dia")
            print("3-Por Filtragem")
            print ("4- Voltar")
            op1=input("->:")
            
            if op1=="1":
             limpar_ecra()
             data_atual = datetime.now().date()
             fim_semana=verificar_fim_de_semana(data_atual)
             id_horario=imprimir_horarios_omissao(conn,cur,fim_semana)
             
             if id_horario !="1":
                 limpar_ecra()
                 completar_tabela_reservar(conn,cur,id_usuario,id_horario,data_atual)


            if op1=="2":
                
                limpar_ecra()
                dia=print_proximos_7_dias()
                fim_semana=verificar_fim_de_semana(dia)
                limpar_ecra()
                id_horario=imprimir_horarios(conn,cur,fim_semana)
                limpar_ecra()
                completar_tabela_reservar(conn,cur,id_usuario,id_horario,dia)
                input("Pressione qualquer tecla:")

            
            if op1=="4":  
             menu_Cliente(op,cur,id_usuario)

             
        if op=="2":
            limpar_ecra()
            listar_reservas_anteriores_por_cliente_futuras(op,cur,id_usuario)
            
                  
            
        if op=="3":
            limpar_ecra()
            listar_reservas_anteriores_por_cliente_passadas(conn,cur,id_usuario)
            #obter_reservas_anteriores_por_cliente(conn, cur, id_usuario)
        
        if op=="4":
            limpar_ecra()
            nao_lidas=contar_vistas_falsas(conn,cur,id_usuario)
            print("Mensagens não lidas:",nao_lidas)
            print("1- Mensagens não lidas")
            print ("2- Mensagens lidas")
            print ("3- Voltar")
            op1=input("->:")
            
            if op1=="1":
                limpar_ecra()
                imprimir_mensagens_usuario(conn,cur,id_usuario,True)
                marcar_mensagens_como_vistas(conn,cur,id_usuario)

            
            if op1=="2":
                limpar_ecra()
                imprimir_mensagens_usuario(conn,cur,id_usuario,False)
                
            if op1=="3":
                menu_Cliente(op,cur,id_usuario)
        
        if op=="5":
            limpar_ecra()
            exibir_perfil(id_usuario)
            break
        
        if op=="6":
            limpar_ecra()
            break 


def mostrar_ids_usuarios(conn, cur,id_usuario):
    try:
        # Consulta todos os IDs de usuário na tabela 'cliente'
        cur.execute("SELECT usuario_id_usuario FROM cliente")
        ids_usuarios = cur.fetchall()

        # Verifica se existem IDs de usuários disponíveis
        if not ids_usuarios:
            print("Nenhum ID de usuário disponível.")
            op1=input("Pressione qualquer tecla para voltar: ")
            menu_Admin(conn,cur,id_usuario)
            

        # Mostra os IDs de usuário na tela
        print("IDs de Usuários Disponíveis:")
        for usuario in ids_usuarios:
            print(usuario[0])

        while True:
            # Solicita ao usuário que selecione um ID de usuário
            id_selecionado = input("Selecione um ID de usuário: ")

            # Verifica se o ID selecionado é válido
            if not id_selecionado.isdigit() or int(id_selecionado) not in [id[0] for id in ids_usuarios]:
                print("ID inválido. Por favor, selecione um ID válido.")
                continue
            else:
                # Retorna o ID de usuário selecionado
                return int(id_selecionado)

    except psycopg2.Error as e:
        print("Erro ao mostrar os IDs de usuário:", e)
        return None


def mostrar_admins_nao_super_admin(conn, cur,id_usuario):
    try:
        # Consulta todos os administradores onde super_admin é False
        cur.execute("SELECT usuario_id_usuario FROM admin WHERE super_admin = false")
        admins_nao_super_admin = cur.fetchall()

        # Verifica se existem administradores com super_admin igual a False
        if not admins_nao_super_admin:
            print("Nenhum administrador disponível.")
            op1=input("Pressione qualquer tecla para voltar: ")
            menu_Admin(conn,cur,id_usuario)

        # Mostra os IDs dos administradores não super admin na tela
        print("Administradores  Disponíveis:")
        for admin in admins_nao_super_admin:
            print(admin[0])

        while True:
            # Solicita ao usuário que selecione um ID de administrador
            id_admin_selecionado = input("Selecione um ID de administrador: ")

            # Verifica se o ID selecionado é válido
            if not id_admin_selecionado.isdigit() or int(id_admin_selecionado) not in [admin[0] for admin in admins_nao_super_admin]:
                print("ID inválido. Por favor, selecione um ID válido.")
                continue
            else:
                # Retorna o ID de administrador selecionado
                return int(id_admin_selecionado)

    except psycopg2.Error as e:
        menu_Admin(conn,cur,id_usuario)
        print("Erro ao mostrar os administradores:", e)
        return None
    
    
def menu_Admin(op, cur, id_usuario):
    limpar_ecra()
    nome = obter_nome_usuario_por_id(conn, cur, id_usuario)
    atualizar_disponibilidade_reservas(op,cur)     
    
    while True:
         limpar_ecra()
         # Chamar a função para criar a conta do cliente
         print("Bem-Vindo ", nome)
         print("O seu ID:",id_usuario)
         print("1- Alterar/Cancelar Reserva")
         print("2- Ver Reservas existentes")
         print("3- Enviar Mensagens")
         print("4- Perfil")
         print("5- Remover admin ")
         print("6- Tornar Usuário Admin")
         print("7- Alterar Preços")
         print("8- Estatísticas")
         print("9- Sair")
         op = input("->:")

         if op == "1":
            limpar_ecra()
            listar_reservas_disponiveis(conn,cur)
            reserva_id = int(input("Digite o ID da reserva que deseja cancelar/alterar: "))
            print("Prima 1 se deseja Cancelar. 2 para alterar!")
            opc=input("->:")
            if opc=="1":               
                limpar_ecra()
                cancelar_reserva(conn, cur, reserva_id)
                
            if opc=="2":

                try:
                    # Perguntar ao usuário quais parâmetros ele deseja alterar
                    opcao_camp = input("Deseja alterar o ID do campo? (S/N): ").upper()
                    if opcao_camp == "S":
                        novo_id_camp = int(input("Digite o novo ID do campo: "))
                    else:
                        # Se o usuário não quiser alterar, manter o valor atual do ID do campo
                        cur.execute("SELECT id_camp FROM Reservar WHERE id_reserva = %s", (reserva_id,))
                        novo_id_camp = cur.fetchone()[0]

                    opcao_hora = input("Deseja alterar o ID da hora? (S/N): ").upper()
                    if opcao_hora == "S":
                        novo_id_hora = int(input("Digite o novo ID da hora: "))
                    else:
                        # Se o usuário não quiser alterar, manter o valor atual do ID da hora
                        cur.execute("SELECT id_horario FROM Reservar WHERE id_reserva = %s", (reserva_id,))
                        novo_id_hora = cur.fetchone()[0]

                    # Executar a alteração da reserva
                    if alterar_reserva(conn, cur, reserva_id, novo_id_camp, novo_id_hora):
                        print("Reserva alterada com sucesso!")
                    else:
                        print("Erro ao alterar reserva.")

                except (Exception, psycopg2.Error) as error:
                    print("Erro ao alterar reserva:", error)


         if op == "2":
            limpar_ecra()
            listar_reservas_disponiveis(conn,cur)
            input("Pressione qualquer tecla para continuar:")
            


         if op == "3":
            limpar_ecra()
            print("Mensagens:")
            print("1- Todos  ")
            print("2- Individual ")
            print("3- Voltar")
            op1 = input("->:")

            if op1 == "1":
                limpar_ecra()
                print("Escreva a mensagem que deseja enviar:")
                mensagem_texto=input("")
                enviar_mensagem_admin(conn,cur,mensagem_texto,True,id_usuario)

            
            if op1 == "2":
                limpar_ecra()
                print("Escreva a mensagem que deseja enviar:")
                mensagem_texto=input("")
                enviar_mensagem_admin(conn,cur,mensagem_texto,False,id_usuario)


            if op1 == "3":
                menu_Admin(op, cur, id_usuario)


         if op == "4":
            limpar_ecra()
            exibir_perfil(id_usuario)


         if op == "5":
             limpar_ecra()
             admin_verifica=verificar_super_admin(op,cur,id_usuario)
             remover_admin(conn,cur,admin_verifica)
 

         if op == "6":
              limpar_ecra()
              super=verificar_super_admin(op,cur,id_usuario)
            
              if super==True:
                 usuario_id = mostrar_ids_usuarios(conn,cur, id_usuario)
                 morada = input("Digite a morada do usuário: ")
                 super_admin = input("É super administrador? (S/N): ").upper()
             
                 if super_admin == "S":
                     super_admin = True
            
                 else:
                     super_admin = False   
                     tornar_admin(conn, cur, usuario_id, morada, super_admin)
    
              else:
                 limpar_ecra()
                 print("Não tem permissão para tornar um  usuário de admin.")
                 opp=input("PRESSIONE QUALQUER TECLA: ")
            
            
         if op == "7":
              while True: 
                  limpar_ecra()
                  print("1-Alterar Preços do Fim-de-semana")
                  print("2-Alterar Preços da  semana")
                  print("3- Voltar")
                  op1 = input("->:")
              
                  if op1 == "1":
                      limpar_ecra()
                      alterar_preco_horario(conn,cur,True)
                   
                
                  if op1 == "2":
                     limpar_ecra()
                     alterar_preco_horario(conn,cur,False)
                  
                  if op1 == "3":
                     break
       
       
         if op== "8":
             while True:
                 limpar_ecra()    
                 print("Escolha o período que quer utilizar para filtrar")
                 print("1-Mês")           
                 print("2-Semana Atual")
                 print("3-Dia de Hoje")
                 print("4-Voltar")
                 op=input("->:")
                 
                   
                 if op=="1":
                     while True:
                            limpar_ecra()
                            print("Escolha o parametro que quer ver:")
                            print("1-Campo e Horario mais reservado")
                            print("2- Campos/Horarios que não tiveram reservas")
                            print("3- Reservadas canceladas/alteradas")
                            print("4-Períodos que os clientes pediram para receber notificação")
                            print("5-Voltar")
                            op3=input("->:")

                            if op3=="1":
                              limpar_ecra()  
                              horario_mais_reservado(conn,cur,op)
                              campo_mais_reservado_mes(conn,cur)
                            if op3=="2":
                             limpar_ecra()
                             listar_campos_horarios_sem_reservas(conn,cur,op)
                 
                            if op3=="3":
                               limpar_ecra()
                               listar_reservas_canceladas_alteradas(conn,cur,op)
                           
                            if op3=="4":
                               limpar_ecra()
                               listar_periodos_notificacao_unicos(conn,cur)
                           
                            if op3=="5":
                               break
                            
                 
                 
                 if op=="2":
                    while True:
                            limpar_ecra()
                            print("Escolha o parametro que quer ver:")
                            print("1-Campo e Horario mais reservado")
                            print("2- Campos/Horarios que não tiveram reservas")
                            print("3- Reservadas canceladas/alteradas")
                            print("4-Períodos que os clientes pediram para receber notificação")
                            print("5-Voltar")
                            op3=input("->:")

                            if op3=="1":
                               limpar_ecra()
                               horario_mais_reservado(conn,cur,op)
                               campo_mais_reservado_semana(conn,cur)
                 
                            if op3=="2":
                             limpar_ecra()
                             listar_campos_horarios_sem_reservas(conn,cur,op)
                 
                            if op3=="3":
                               limpar_ecra()
                               listar_reservas_canceladas_alteradas(conn,cur,op)
                           
                            if op3=="4":
                               limpar_ecra()
                               listar_periodos_notificacao_unicos(conn,cur)
                           
                            if op3=="5":
                               break
                 
                 
                 
                 if op=="3":
                      while True:
                            limpar_ecra()
                            print("Escolha o parametro que quer ver:")
                            print("1-Campo e Horario mais reservado")
                            print("2- Campos/Horarios que não tiveram reservas")
                            print("3- Reservadas canceladas/alteradas")
                            print("4-Períodos que os clientes pediram para receber notificação")
                            print("5-Voltar")
                            op3=input("->:")

                            if op3=="1":
                              limpar_ecra()
                              horario_mais_reservado(conn,cur,op)
                              campo_mais_reservado_hoje(conn,cur)
                 
                            if op3=="2":
                                limpar_ecra()
                                listar_campos_horarios_sem_reservas(conn,cur,op)
                 
                            if op3=="3":
                                limpar_ecra()
                                listar_reservas_canceladas_alteradas(conn,cur,op)
                           

                            if op3=="4":
                               limpar_ecra()
                               listar_periodos_notificacao_unicos(conn,cur)
                           
                            if op3=="5":
                                limpar_ecra()
                                break
                 
                 
                 
                 if op=="4":
                     break
                 
            
         if op == "9":
              limpar_ecra()
              break

 
 
    
#--------------------------------------------------------------------------------


#ESTATISTICAS E RESERVAS PASSADAS E FUTURAS--------------------------------------

def listar_reservas_anteriores_por_cliente_passadas(conn, cur, id_cliente):
    try:
        # Obter a data atual
        data_atual = datetime.now().date()

        # Executar o comando SQL para selecionar todas as reservas anteriores feitas pelo cliente específico
        sql_select = """
            SELECT r.data, h.horas, h.preco, c.nome_campo
            FROM reservar r
            INNER JOIN horario h ON r.id_horario = h.id
            INNER JOIN campos c ON r.id_camp = c.id_campo
            WHERE r.cliente_usuario_id_usuario = %s AND r.data < %s 
            ORDER BY r.data DESC
        """
        cur.execute(sql_select, (id_cliente, data_atual))
        
        # Recuperar as reservas
        reservas = cur.fetchall()

        if not reservas:
            print(f"Não há reservas anteriores feitas pelo cliente com ID {id_cliente}.")
            return

        # Exibir as reservas anteriores feitas pelo cliente
        print(f"Reservas Anteriores:")
        print("======================================")
        for reserva in reservas:
            data_reserva = reserva[0]
            hora_reserva = reserva[1]
            preco_reserva = reserva[2]
            campo_reserva = reserva[3]

            # Exibir a data da reserva, o horário da reserva, o preço e o campo da reserva
            print(f"Data: {data_reserva} - Horário: {hora_reserva} - Preço: {preco_reserva} - Campo: {campo_reserva}")
        input("Pressione qualquer tecla para continuar:")

    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao listar reservas anteriores feitas pelo cliente com ID {id_cliente}:", error)


def horario_mais_reservado(conn, cur, escolha):
    try:
        # Obter a data atual
        data_atual = datetime.now()

        if escolha == "1":
            # Mês atual
            primeiro_dia_mes = data_atual.replace(day=1).date()
            ultimo_dia_mes = (data_atual.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            periodo_inicio = primeiro_dia_mes
            periodo_fim = ultimo_dia_mes.date()
            periodo_texto = "Mês Atual"
        elif escolha == "2":
            # Semana atual (considerando que a semana começa no domingo)
            primeiro_dia_semana = (data_atual - timedelta(days=data_atual.weekday() + 1)).date()
            ultimo_dia_semana = primeiro_dia_semana + timedelta(days=6)
            periodo_inicio = primeiro_dia_semana
            periodo_fim = ultimo_dia_semana
            periodo_texto = "Semana Atual"
        elif escolha == "3":
            # Dia atual
            periodo_inicio = data_atual.date()
            periodo_fim = data_atual.date()
            periodo_texto = "Dia Atual"
        else:
            print("Escolha inválida. Por favor, escolha 1, 2 ou 3.")
            return

        # Executar o comando SQL para encontrar o campo e o horário mais reservado no período escolhido
        sql_select = """
            SELECT c.nome_campo, h.horas, COUNT(*) as total_reservas
            FROM reservar r
            INNER JOIN horario h ON r.id_horario = h.id
            INNER JOIN campos c ON r.id_camp = c.id_campo
            WHERE r.data >= %s AND r.data <= %s
            GROUP BY c.nome_campo, h.horas
            ORDER BY total_reservas DESC
            LIMIT 1
        """
        cur.execute(sql_select, (periodo_inicio, periodo_fim))
        
        # Recuperar o campo e o horário mais reservado
        resultado = cur.fetchone()

        if not resultado:
            print(f"Não há reservas no {periodo_texto.lower()}.")
            return

        # Exibir o campo e o horário mais reservado no período escolhido
        campo_mais_reservado = resultado[0]
        horario_mais_reservado = resultado[1]
        total_reservas = resultado[2]

        print(f"Horário Mais Reservado no {periodo_texto}:")
        print("============================================")
        print(f"Horário: {horario_mais_reservado}")
        input("Pressione qualquer tecla para aparecer o campo:")
        

    except (Exception, psycopg2.Error) as error:
        print("Erro ao obter o campo e horário mais reservado:", error)



def listar_reservas_anteriores_por_cliente_futuras(conn, cur, id_cliente):
    try:
        # Obter a data atual
        data_atual = datetime.now().date()

        # Executar o comando SQL para selecionar todas as reservas anteriores feitas pelo cliente específico
        sql_select = """
            SELECT r.data, h.horas, h.preco, c.nome_campo
            FROM reservar r
            INNER JOIN horario h ON r.id_horario = h.id
            INNER JOIN campos c ON r.id_camp = c.id_campo
            WHERE r.cliente_usuario_id_usuario = %s AND r.data > %s 
            ORDER BY r.data DESC
        """
        cur.execute(sql_select, (id_cliente, data_atual))
        
        # Recuperar as reservas
        reservas = cur.fetchall()

        if not reservas:
            print(f"Não há reservas anteriores feitas pelo cliente com ID {id_cliente}.")
            return

        # Exibir as reservas anteriores feitas pelo cliente
        print(f"Reservas Futuras:")
        print("======================================")
        for reserva in reservas:
            data_reserva = reserva[0]
            hora_reserva = reserva[1]
            preco_reserva = reserva[2]
            campo_reserva = reserva[3]

            # Exibir a data da reserva, o horário da reserva, o preço e o campo da reserva
            print(f"Data: {data_reserva} - Horário: {hora_reserva} - Preço: {preco_reserva} - Campo: {campo_reserva}")
        input("Pressione qualquer tecla para continuar:")

    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao listar reservas anteriores feitas pelo cliente com ID {id_cliente}:", error)




def listar_reservas_disponiveis(conn, cur):
    try:
        # Executar o comando SQL para selecionar as reservas disponíveis
        sql_select = """
            SELECT r.id_reserva, r.data, h.horas, c.nome_campo, r.cliente_usuario_id_usuario 
            FROM reservar r
            INNER JOIN horario h ON r.id_horario = h.id
            INNER JOIN campos c ON r.id_camp = c.id_campo
            WHERE r.disponivel = TRUE
            ORDER BY r.data, h.horas
        """
        cur.execute(sql_select)
        
        # Recuperar as reservas disponíveis
        reservas_disponiveis = cur.fetchall()

        if not reservas_disponiveis:
            print("Não há reservas disponíveis.")
            return

        # Exibir as reservas disponíveis
        print("Reservas Disponíveis:")
        print("======================================")
        for reserva in reservas_disponiveis:
            id_reserva = reserva[0]
            data_reserva = reserva[1]
            hora_reserva = reserva[2]
            nome_campo = reserva[3]
            id_cliente = reserva[4]

            print(f"ID Reserva: {id_reserva} - Data: {data_reserva} - Horário: {hora_reserva} - Campo: {nome_campo} - ID Cliente: {id_cliente}")
        input("Pressione qualquer tecla para continuar:")    

    except (Exception, psycopg2.Error) as error:
        print("Erro ao listar reservas disponíveis:", error)



def atualizar_disponibilidade_reservas(conn, cur):
    try:
        # Obter a data e hora atual
        data_hora_atual = datetime.now()

        # Executar o comando SQL para atualizar a disponibilidade das reservas
        sql_update = """
            UPDATE reservar r
            SET disponivel = FALSE 
            FROM horario h
            WHERE r.id_horario = h.id
            AND r.data + h.horas < %s;
        """
        cur.execute(sql_update, (data_hora_atual,))
        
        # Confirmar a transação
        conn.commit()

        print("Disponibilidade das reservas atualizada com sucesso.")

    except (Exception, psycopg2.Error) as error:
        conn.rollback()
        print("Erro ao atualizar disponibilidade das reservas:", error)



def campo_mais_reservado_hoje(conn, cur):
    try:
        # Obter a data atual

        data_atual = datetime.now().date()

        # Executar o comando SQL para encontrar o campo mais reservado no dia atual
        sql_select = """
            SELECT r.id_camp, COUNT(*) as total_reservas
            FROM reservar r
            WHERE r.data = %s
            GROUP BY r.id_camp
            ORDER BY total_reservas DESC
            LIMIT 1
        """
        cur.execute(sql_select, (data_atual,))
        
        # Recuperar o campo mais reservado
        resultado = cur.fetchone()

        if not resultado:
            print(f"Não há reservas no dia {data_atual}.")
            return None

        # Obter o ID do campo mais reservado
        campo_mais_reservado_id = resultado[0]
        total_reservas = resultado[1]

        print(f"Campo Mais Reservado no Dia {data_atual}:")
        print("============================================")
        print(f"ID do Campo: {campo_mais_reservado_id} - Total de Reservas: {total_reservas}")
        imprimir_nome_campo(conn,cur,campo_mais_reservado_id)
        input("Pressione qualquer tecla para continuar ")
        return campo_mais_reservado_id
        

    except (Exception, psycopg2.Error) as error:
        print("Erro ao obter o campo mais reservado:", error)
        return None



def campo_mais_reservado_mes(conn, cur):
    try:
        # Obter a data atual
        data_atual = datetime.now().date()
        # Calcular o primeiro e o último dia do mês atual
        primeiro_dia_mes = data_atual.replace(day=1)
        ultimo_dia_mes = (primeiro_dia_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        # Executar o comando SQL para encontrar o campo mais reservado no mês atual
        sql_select = """
            SELECT r.id_camp, COUNT(*) as total_reservas
            FROM reservar r
            WHERE r.data BETWEEN %s AND %s
            GROUP BY r.id_camp
            ORDER BY total_reservas DESC
            LIMIT 1
        """
        cur.execute(sql_select, (primeiro_dia_mes, ultimo_dia_mes))
        
        # Recuperar o campo mais reservado
        resultado = cur.fetchone()

        if not resultado:
            print(f"Não há reservas no mês de {data_atual.strftime('%B %Y')}.")
            return None

        # Obter o ID do campo mais reservado
        campo_mais_reservado_id = resultado[0]
        total_reservas = resultado[1]

        print(f"Campo Mais Reservado no Mês de {data_atual.strftime('%B %Y')}:")
        print("============================================")
        print(f"ID do Campo: {campo_mais_reservado_id} - Total de Reservas: {total_reservas}")
        imprimir_nome_campo(conn,cur,campo_mais_reservado_id)
        input("Pressione qualquer tecla para continuar:")
        return campo_mais_reservado_id

    except (Exception, psycopg2.Error) as error:
        print("Erro ao obter o campo mais reservado:", error)
        return None



def campo_mais_reservado_semana(conn, cur):
    try:
        # Obter a data atual
        data_atual = datetime.now().date()
        # Calcular o primeiro e o último dia da semana atual (assumindo que a semana começa no domingo)
        primeiro_dia_semana = data_atual - timedelta(days=data_atual.weekday() + 1)
        ultimo_dia_semana = primeiro_dia_semana + timedelta(days=6)

        # Executar o comando SQL para encontrar o campo mais reservado na semana atual
        sql_select = """
            SELECT r.id_camp, COUNT(*) as total_reservas
            FROM reservar r
            WHERE r.data BETWEEN %s AND %s
            GROUP BY r.id_camp
            ORDER BY total_reservas DESC
            LIMIT 1
        """
        cur.execute(sql_select, (primeiro_dia_semana, ultimo_dia_semana))
        
        # Recuperar o campo mais reservado
        resultado = cur.fetchone()

        if not resultado:
            print(f"Não há reservas na semana de {primeiro_dia_semana.strftime('%d/%m/%Y')} a {ultimo_dia_semana.strftime('%d/%m/%Y')}.")
            return None

        # Obter o ID do campo mais reservado
        campo_mais_reservado_id = resultado[0]
        total_reservas = resultado[1]

        print(f"Campo Mais Reservado na Semana de {primeiro_dia_semana.strftime('%d/%m/%Y')} a {ultimo_dia_semana.strftime('%d/%m/%Y')}:")
        print("============================================")
        print(f"ID do Campo: {campo_mais_reservado_id} - Total de Reservas: {total_reservas}")
        imprimir_nome_campo(conn,cur,campo_mais_reservado_id)
        input("Pressione qualquer tecla:")
        return campo_mais_reservado_id

    except (Exception, psycopg2.Error) as error:
        print("Erro ao obter o campo mais reservado:", error)
        return None



def imprimir_nome_campo(conn, cur, id_campo):
    try:
        # Executar o comando SQL para selecionar o nome do campo com o ID fornecido
        sql_select = "SELECT nome_campo FROM campos WHERE id_campo = %s"
        cur.execute(sql_select, (id_campo,))
        
        # Recuperar o resultado da consulta
        resultado = cur.fetchone()

        if not resultado:
            print(f"Não há campo com o ID {id_campo}.")
            return

        # Obter o nome do campo
        nome_campo = resultado[0]

        # Exibir o nome do campo
        print(f"Nome do Campo: {nome_campo}")

    except (Exception, psycopg2.Error) as error:
        print("Erro ao obter o nome do campo:", error)




def listar_periodos_notificacao_unicos(conn, cur):
    try:
        # Executar o comando SQL para selecionar os períodos de notificação únicos, ordenados por ordem decrescente de pedidos
        sql_select = """
            SELECT data, hora, COUNT(*) as total_pedidos
            FROM listadeespera
            GROUP BY data, hora
            ORDER BY total_pedidos DESC
        """
        cur.execute(sql_select)
        
        # Recuperar os resultados
        periodos = cur.fetchall()

        if not periodos:
            print("Não há pedidos de notificação registrados.")
            return

        # Exibir os períodos de notificação ordenados por ordem decrescente de pedidos
        print("Períodos de Notificação de Disponibilidade do Campo (Únicos):")
        print("============================================================")
        for periodo in periodos:
            data_notificacao = periodo[0]
            hora_notificacao = periodo[1]
            total_pedidos = periodo[2]

            # Exibir a data, hora e o número total de pedidos
            print(f"Data: {data_notificacao} - Hora: {hora_notificacao} - Total de Pedidos: {total_pedidos}")
        input("Pressione qualquer tecla para continuar:")

    except (Exception, psycopg2.Error) as error:
        print("Erro ao listar os períodos de notificação:", error)




def listar_reservas_canceladas_alteradas(conn, cur, escolha):
    try:
        # Obter a data atual
        data_atual = datetime.now()

        # Determinar o período com base na escolha do usuário
        if escolha == "1":
            # Mês atual
            primeiro_dia_mes = data_atual.replace(day=1)
            ultimo_dia_mes = (primeiro_dia_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            periodo_inicio = primeiro_dia_mes
            periodo_fim = ultimo_dia_mes
            periodo_texto = "Mês Atual"
        elif escolha == "2":
            # Semana atual (considerando que a semana começa no domingo)
            primeiro_dia_semana = data_atual - timedelta(days=data_atual.weekday() + 1)
            ultimo_dia_semana = primeiro_dia_semana + timedelta(days=6)
            periodo_inicio = primeiro_dia_semana
            periodo_fim = ultimo_dia_semana
            periodo_texto = "Semana Atual"
        elif escolha == "3":
            # Dia atual
            periodo_inicio = data_atual.date()
            periodo_fim = data_atual.date()
            periodo_texto = "Dia Atual"
        else:
            print("Escolha inválida. Por favor, escolha 1, 2 ou 3.")
            return

        # Executar o comando SQL para selecionar reservas canceladas ou alteradas no período especificado
        sql_select = """
            SELECT 'cancelada' AS tipo_reserva, cliente_usuario_id_usuario, id_reserva, data, id_horario, id_camp
            FROM historico_reservas
            WHERE data BETWEEN %s AND %s
            UNION ALL
            SELECT 'alterada' AS tipo_reserva, cliente_usuario_id_usuario, id_reserva, data, id_horario, id_camp
            FROM reservar
            WHERE reserva_alterada = TRUE AND data BETWEEN %s AND %s
            ORDER BY data, id_horario
        """
        cur.execute(sql_select, (periodo_inicio, periodo_fim, periodo_inicio, periodo_fim))
        
        # Recuperar os resultados da consulta
        reservas = cur.fetchall()

        if not reservas:
            print(f"Não há reservas canceladas ou alteradas no {periodo_texto.lower()}.")
            input("Pressione qualquer tecla para continuar:")

            return

        # Exibir as reservas canceladas ou alteradas no período especificado
        print(f"Reservas Canceladas ou Alteradas no {periodo_texto}:")
        print("======================================")
        for reserva in reservas:
            tipo_reserva = reserva[0]
            cliente_id = reserva[1]
            reserva_id = reserva[2]
            data_reserva = reserva[3]
            id_horario = reserva[4]
            id_camp = reserva[5]

            # Obter a hora associada ao id_horario
            cur.execute("SELECT horas FROM horario WHERE id = %s", (id_horario,))
            hora_reserva = cur.fetchone()[0]

            # Obter o nome do campo associado ao id_camp
            cur.execute("SELECT nome_campo FROM campos WHERE id_campo = %s", (id_camp,))
            nome_campo = cur.fetchone()[0]

            # Exibir os detalhes da reserva
            print(f"Tipo: {tipo_reserva.capitalize()} - Cliente ID: {cliente_id} - Reserva ID: {reserva_id} - Data: {data_reserva} - Hora: {hora_reserva} - Campo: {nome_campo}")

        input("Pressione qualquer tecla para continuar:")

    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao listar reservas canceladas ou alteradas no {periodo_texto.lower()}:", error)






def listar_campos_horarios_sem_reservas(conn, cur, escolha):
    try:
        # Obter a data atual
        data_atual = datetime.now()

        if escolha == "1":
            # Mês atual
            primeiro_dia_mes = data_atual.replace(day=1)
            ultimo_dia_mes = (primeiro_dia_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            periodo_inicio = primeiro_dia_mes
            periodo_fim = ultimo_dia_mes
            periodo_texto = "Mês Atual"
        elif escolha == "2":
            # Semana atual (considerando que a semana começa na segunda-feira)
            primeiro_dia_semana = data_atual - timedelta(days=data_atual.weekday())
            ultimo_dia_semana = primeiro_dia_semana + timedelta(days=6)
            periodo_inicio = primeiro_dia_semana
            periodo_fim = ultimo_dia_semana
            periodo_texto = "Semana Atual"
        elif escolha == "3":
            # Dia atual
            periodo_inicio = data_atual.date()
            periodo_fim = data_atual.date()
            periodo_texto = "Dia Atual"
        else:
            print("Escolha inválida. Por favor, escolha 1, 2 ou 3.")
            return

        # Executar o comando SQL para encontrar todos os campos e horários disponíveis
        sql_campos_horarios = """
            SELECT c.id_campo, c.nome_campo, h.id AS id_horario, h.horas
            FROM campos c, horario h
            ORDER BY c.nome_campo, h.horas
        """
        cur.execute(sql_campos_horarios)
        todos_campos_horarios = cur.fetchall()

        # Executar o comando SQL para encontrar todas as reservas no período escolhido
        sql_reservas = """
            SELECT r.id_camp, r.id_horario
            FROM reservar r
            WHERE r.data >= %s AND r.data <= %s
        """
        cur.execute(sql_reservas, (periodo_inicio, periodo_fim))
        reservas_periodo = cur.fetchall()

        # Criar um conjunto de (id_camp, id_horario) para reservas feitas no período
        reservas_set = set(reservas_periodo)

        # Filtrar campos/horários que não tiveram reservas no período
        campos_horarios_sem_reservas = [
            (campo[0], campo[1], campo[2], campo[3])
            for campo in todos_campos_horarios
            if (campo[0], campo[2]) not in reservas_set
        ]

        if not campos_horarios_sem_reservas:
            print(f"Todos os campos e horários tiveram reservas no {periodo_texto.lower()}.")
            return

        # Exibir os campos e horários que não tiveram reservas no período escolhido
        print(f"Campos e Horários Sem Reservas no {periodo_texto}:")
        print("============================================")
        for campo in campos_horarios_sem_reservas:
            print(f"Campo: {campo[1]} - Horário: {campo[3]}")

        input("Pressione qualquer tecla para continuar:")

    except (Exception, psycopg2.Error) as error:
        print("Erro ao listar campos e horários sem reservas:", error)








#-------------------------------------------------------------------------------

#FUNÇÕES DE RESERVA---------------------------------------------------------------

def verificar_fim_de_semana(data):
    # Obtém o dia da semana (0 = segunda-feira, 6 = domingo)
    dia_da_semana = data.weekday()

    # Se o dia da semana for sábado (5) ou domingo (6), retorna True (fim de semana)
    if dia_da_semana in [5, 6]:
        return True
    else:
        return False




def print_proximos_7_dias():
    # Obter a data de hoje
    hoje = datetime.now().date()+ timedelta(days=1)

    # Imprimir os próximos 7 dias
    print("Próximos 7 dias:")
    for i in range(7):
        dia = hoje + timedelta(days=i)
        print(f"{i+1} - {dia.strftime('%Y-%m-%d')}")

    # Solicitar ao usuário que selecione um dia
    while True:
        
        try:
            escolha = int(input("Escolha um dos dias acima: "))
            if 1 <= escolha <= 7:
                return hoje + timedelta(days=escolha - 1)
            else:
                print("Por favor, escolha um número de 1 a 7.")
                input("Pressione qualquer tecla:")
                limpar_ecra()
                
        except ValueError:
            print("Por favor, insira um número válido.")
    
    

    
def imprimir_horarios_omissao(conn, cur, fimds):
    try:
        # Obter a hora atual
        hora_atual = datetime.now().time().strftime('%H:%M')

        # Seleciona os horários disponíveis na tabela 'horario' com base na hora atual e no valor fornecido para fimds
        cur.execute("SELECT id, horas FROM horario WHERE fimds = %s AND horas >= %s ORDER BY horas ASC", (fimds, hora_atual,))
        horarios = cur.fetchall()

        if not horarios:
            print("Não há horários disponíveis para reservar neste momento.")
            input("Pressione qualquer tecla para voltar: ")
            return "1"

        print("Horários Disponíveis:")
        for horario in horarios:
            id_horario, hora = horario
            print(f"ID: {id_horario}, Hora: {hora}")

        # Solicita ao usuário que selecione um ID de horário
        id_selecionado = input("Selecione o ID do horário desejado: ")

        # Verifica se o ID selecionado é válido
        id_valido = False
        for horario in horarios:
            if id_selecionado == str(horario[0]):
                id_valido = True
                break

        if not id_valido:
            print("ID inválido. Por favor, selecione um ID válido.")
            input("Pressione qualquer tecla para voltar: ")
            return None

        return id_selecionado

    except psycopg2.Error as e:
        print("Erro ao imprimir os horários:", e)
        return None    
    
    

def verificar_disponibilidade_campos(conn, cur, dia_escolhido, id_horario):
    try:
        limpar_ecra()
        # Verificar a disponibilidade dos campos para o dia e horário escolhidos
        cur.execute("SELECT id_campo, nome_campo FROM campos WHERE id_campo NOT IN \
                     (SELECT id_camp FROM reservar WHERE id_horario = %s AND data = %s)", 
                     (id_horario, dia_escolhido,))
        campos_disponiveis = cur.fetchall()

        if not campos_disponiveis:
            limpar_ecra()
            print("Não há campos disponíveis para o horário escolhido ou todos estão reservados.")
            input("Pressione qualquer tecla:")
            return "51"

        print("Campos Disponíveis:")
        for campo in campos_disponiveis:
            id_campo, nome_campo = campo
            print(f"ID: {id_campo}, Nome: {nome_campo}")

        # Solicitar ao usuário que selecione um ID de campo
        id_campo_escolhido = input("Selecione o ID do campo desejado para reserva: ")

        # Verificar se o ID selecionado é válido
        id_valido = False
        for campo in campos_disponiveis:
            if id_campo_escolhido == str(campo[0]):
                id_valido = True
                break

        if not id_valido:
            limpar_ecra()
            print("ID inválido. Por favor, selecione um ID válido.")
            input("Pressione qualquer tecla:")
            verificar_disponibilidade_campos(conn,cur,dia_escolhido,id_horario)
                    
        return id_campo_escolhido

    except psycopg2.Error as e:
        print("Erro ao verificar a disponibilidade dos campos:", e)
        return None




def imprimir_horarios(conn, cur, fimds):
    try:
        # Seleciona os horários da tabela 'horario' com base no valor fornecido para fimds
        cur.execute("SELECT id, horas FROM horario WHERE fimds = %s ORDER BY horas ASC", (fimds,))
        horarios = cur.fetchall()

        if not horarios:
            print("Não há horários disponíveis.")
            op1=input("Pressione qualquer tecla para voltar: ")

            return None

        print("Horários Disponíveis:")
        for horario in horarios:
            id_horario, hora = horario
            print(f"ID: {id_horario}, Hora: {hora}")

        # Solicita ao usuário que selecione um ID de horário
        id_selecionado = input("Selecione o ID do horário desejado: ")

        # Verifica se o ID selecionado é válido
        id_valido = False
        for horario in horarios:
            if id_selecionado == str(horario[0]):
                id_valido = True
                break

        if not id_valido:
            print("ID inválido. Por favor, selecione um ID válido.")
            op1=input("Pressione qualquer tecla para voltar: ")

            return None

        return id_selecionado

    except psycopg2.Error as e:
        print("Erro ao imprimir os horários:", e)
        return None





def imprimir_horarios_todos(conn, cur):
    try:
        # Seleciona os horários da tabela 'horario' com base no valor fornecido para fimds
        cur.execute("SELECT id, horas FROM horarioORDER BY horas ASC")
        horarios = cur.fetchall()

        if not horarios:
            print("Não há horários disponíveis.")
            op1=input("Pressione qualquer tecla para voltar: ")

            return None

        print("Horários Disponíveis:")
        for horario in horarios:
            id_horario, hora = horario
            print(f"ID: {id_horario}, Hora: {hora}")

        # Solicita ao usuário que selecione um ID de horário
        id_selecionado = input("Selecione o ID do horário desejado: ")

        # Verifica se o ID selecionado é válido
        id_valido = False
        for horario in horarios:
            if id_selecionado == str(horario[0]):
                id_valido = True
                break

        if not id_valido:
            print("ID inválido. Por favor, selecione um ID válido.")
            op1=input("Pressione qualquer tecla para voltar: ")

            return None

        return id_selecionado

    except psycopg2.Error as e:
        print("Erro ao imprimir os horários:", e)
        return None




def completar_tabela_reservar(conn, cur, id_cliente, id_horario, data_reserva):
    try:
        # Listar os campos disponíveis
        cur.execute("SELECT id_campo, nome_campo FROM campos")
        campos = cur.fetchall()
        id_campo_escolhido=verificar_disponibilidade_campos(conn,cur,data_reserva,id_horario)

        if id_campo_escolhido!="51":
            cur.execute("SELECT preco FROM horario WHERE id = %s", (id_horario,))
            preco = cur.fetchone()[0]

            while True:
                limpar_ecra()
                print("O preço da sua reserva será:", preco, "€")
                print("1 - Confirmar reserva")
                print("2 - Cancelar reserva")
                op = input("->:")

                if op == "1":
                    cur.execute("INSERT INTO reservar (id_camp, cliente_usuario_id_usuario, id_horario, disponivel, receber_notific, reserva_alterada, data) VALUES (%s, %s, %s, true, false, false, %s)",
                                (id_campo_escolhido, id_cliente, id_horario, data_reserva))
                    conn.commit()
                    limpar_ecra()
                    print("Reserva concluída com sucesso!")
                    input("Pressione qualquer tecla:")
                    break

                if op == "2":
                    break
                
        else:
            while True:
                limpar_ecra()
                print("Deseja Receber uma notificação quando algum campo estiver disponivel?")
                print("1-Sim")
                print("2-Não")
                op=input("->:")
                
                if op=="1":
                    preencher_lista_de_espera(conn,cur,id_cliente,data_reserva, id_horario)
                    break
                    
                    
                if op=="2":
                    break
                        

    except psycopg2.Error as e:
        conn.rollback()
        print("Erro ao completar a tabela reservar:", e)
        input("Pressione qualquer tecla:")





def preencher_lista_de_espera(conn, cur, id_cliente, data_atual, id_horario):
    try:
        # Obter a hora associada ao id_horario da tabela horario
        cur.execute("SELECT horas FROM horario WHERE id = %s", (id_horario,))
        hora_horario = cur.fetchone()[0]

        # Inserir na tabela listadeespera
        cur.execute("INSERT INTO listadeespera (cliente_usuario_id_usuario, data, hora, hora_notificada) VALUES (%s, %s, %s, %s)",
                    (id_cliente, data_atual, hora_horario, False))
        conn.commit()
        limpar_ecra()
        print("Registro adicionado à lista de espera com sucesso.")
        input("Pressione qualquer tecla: ")

    except psycopg2.Error as e:
        conn.rollback()
        print("Erro ao preencher a lista de espera:", e)




def atualizar_hora_notificada(conn, cur, cliente_id):
    try:
        # Atualizar a coluna hora_notificada para true
        cur.execute("UPDATE listadeespera SET hora_notificada = true WHERE cliente_usuario_id_usuario = %s", (cliente_id,))
        conn.commit()
        print("Hora notificada atualizada com sucesso.")
    except psycopg2.Error as e:
        conn.rollback()
        print("Erro ao atualizar hora notificada:", e)





def listar_reservas_disponiveis(conn, cur):
    try:
        # Executando o comando SQL para selecionar as reservas disponíveis
        sql_select = """SELECT id_reserva, data, id_horario 
                        FROM reservar 
                        WHERE disponivel = TRUE"""
        cur.execute(sql_select)
        
        # Recuperando as reservas disponíveis
        reservas_disponiveis = cur.fetchall()

        # Exibindo as reservas disponíveis
        print("Reservas Disponíveis:")
        print("=======================")
        for reserva in reservas_disponiveis:
            # Associar o ID do horário à hora correspondente
            id_reserva = reserva[0]
            data_reserva = reserva[1]
            id_horario = reserva[2]
            horario_associado = associar_id_a_horario(conn, cur, id_horario)
            
            # Exibir o ID, a data e o horário associado
            print(f"ID da Reserva: {id_reserva} - Data: {data_reserva} - Horário: {horario_associado}")

    except (Exception, psycopg2.Error) as error:
        print("Erro ao listar reservas disponíveis:", error)




def associar_id_a_horario(conn, cur, id_horario):
    try:
        # Executa o comando SQL para selecionar o horário correspondente ao ID da reserva
        sql_select = """SELECT horas FROM Horario WHERE id = %s"""
        cur.execute(sql_select, (id_horario,))
        
        # Recupera o horário correspondente ao ID da reserva
        horario = cur.fetchone()

        # Verifica se o horário foi encontrado
        if horario:
            return horario[0]
        else:
            return "Horário não encontrado"

    except (Exception, psycopg2.Error) as error:
        print("Erro ao associar ID a horário:", error)


#------------------------------------------------------------------------------------------



#FUNÇÕES DE ADMINS--------------------------------------------------------------------------


def verificar_super_admin(conn, cur, usuario_id):
    try:
        # Verifica se o usuário é um super administrador
        cur.execute("SELECT super_admin FROM admin WHERE usuario_id_usuario = %s", (usuario_id,))
        super_admin = cur.fetchone()

        if super_admin and super_admin[0]:
            return True
        else:
            return False

    except psycopg2.Error as e:
        print("Erro ao verificar se o usuário é um super administrador:", e)
        return False


def enviar_mensagem_admin(conn, cur, mensagem_texto, mensagem_para_todos,id_usuario):
    try:
        # Obter a data e hora atual sem segundos
        data_hora = datetime.now().strftime('%Y-%m-%d %H:%M')

        # Inserir a mensagem na tabela mensagem_
        cur.execute("INSERT INTO mensagem_ (texto, mensagem_all) VALUES (%s, %s) RETURNING id_mensagem", 
                    (mensagem_texto, mensagem_para_todos))
        mensagem_id = cur.fetchone()[0]  # Obter o ID de mensagem atribuído

        conn.commit()
        
        # Se mensagem_para_todos for verdadeira, associar a mensagem a todos os clientes na tabela visualizacao
        if mensagem_para_todos:
            # Obter todos os IDs de usuário dos clientes
            cur.execute("SELECT usuario_id_usuario FROM cliente")
            clientes_ids = cur.fetchall()

            # Verificar se a associação já existe antes de inseri-la
            for cliente_id in clientes_ids:
                cur.execute("SELECT COUNT(*) FROM visualizacao WHERE mensagem__id_mensagem = %s AND cliente_usuario_id_usuario = %s", 
                            (mensagem_id, cliente_id))
                existe_associacao = cur.fetchone()[0]

                if existe_associacao == 0:  # Se a associação não existe, insira-a
                    cur.execute("INSERT INTO visualizacao (mensagem__id_mensagem, cliente_usuario_id_usuario, vista, horas_mensagem) VALUES (%s, %s, %s, %s)", 
                                (mensagem_id, cliente_id, False, data_hora))
            
            conn.commit()
            limpar_ecra()
            print("Mensagem enviada com sucesso para todos os clientes.")
            op=input("Pressione qualquer tecla para continuar")
            
        else:
            # Envio da mensagem para um membro específico
            destinatario_id=mostrar_ids_usuarios(conn,cur,id_usuario)
            if destinatario_id is None:
                raise ValueError("O ID do destinatário não foi especificado.")
                op=input("Pressione qualquer tecla para continuar")

            # Verificar se o destinatário é um cliente
            cur.execute("SELECT COUNT(*) FROM cliente WHERE usuario_id_usuario = %s", (destinatario_id,))
            destinatario_existe = cur.fetchone()[0]

            if destinatario_existe == 0:
                print("O destinatário especificado não é um cliente válido.")
                op=input("Pressione qualquer tecla para continuar")
            else:
                # Inserir a mensagem na tabela visualizacao para o destinatário específico
                cur.execute("INSERT INTO visualizacao (mensagem__id_mensagem, cliente_usuario_id_usuario, vista, horas_mensagem) VALUES (%s, %s, %s, %s)", 
                            (mensagem_id, destinatario_id, False, data_hora))
                conn.commit()
                limpar_ecra()
                print("Mensagem enviada com sucesso para o usuário {}.".format(destinatario_id))
                op=input("Pressione qualquer tecla para continuar")

    
    
    except psycopg2.IntegrityError as e:
        conn.rollback()
        print("Erro ao enviar a mensagem:", e)
        op=input("Pressione qualquer tecla para continuar")



def enviar_mensagem_admin_a_especifico(conn, cur, mensagem_texto, ids_usuarios):
    try:
        # Obter a data e hora atual sem segundos
        data_hora = datetime.now().strftime('%Y-%m-%d %H:%M')

        # Inserir a mensagem na tabela mensagem_
        cur.execute("INSERT INTO mensagem_ (texto, mensagem_all) VALUES (%s, %s) RETURNING id_mensagem", 
                    (mensagem_texto, False))
        mensagem_id = cur.fetchone()[0]  # Obter o ID de mensagem atribuído

        conn.commit()

        for id_usuario in ids_usuarios:
            # Verificar se o destinatário é um cliente
            cur.execute("SELECT COUNT(*) FROM cliente WHERE usuario_id_usuario = %s", (id_usuario,))
            destinatario_existe = cur.fetchone()[0]

            if destinatario_existe == 0:
                print(f"O destinatário especificado (ID: {id_usuario}) não é um cliente válido.")
            else:
                # Verificar se a associação já existe antes de inseri-la
                cur.execute("SELECT COUNT(*) FROM visualizacao WHERE mensagem__id_mensagem = %s AND cliente_usuario_id_usuario = %s", 
                            (mensagem_id, id_usuario))
                existe_associacao = cur.fetchone()[0]

                if existe_associacao == 0:  # Se a associação não existe, insira-a
                    cur.execute("INSERT INTO visualizacao (mensagem__id_mensagem, cliente_usuario_id_usuario, vista, horas_mensagem) VALUES (%s, %s, %s, %s)", 
                                (mensagem_id, id_usuario, False, data_hora))
        
        conn.commit()
        limpar_ecra()
        print("Mensagens enviadas com sucesso.")
        input("Pressione qualquer tecla para continuar")

    except psycopg2.IntegrityError as e:
        conn.rollback()
        print("Erro ao enviar a mensagem:", e)
        input("Pressione qualquer tecla para continuar")



def remover_admin(conn, cur, super_admin):
    try:
        # Verifica se o usuário tem permissão de super administrador
        if not super_admin:
            print("Você não tem permissão para remover usuários de admin.")
            opp=input("PRESSIONE QUALQUER TECLA: ")
            return False

        # Solicita o ID do administrador a ser removido
        id_admin_remover=mostrar_admins_nao_super_admin(conn,cur,super_admin)
    
        # Verifica se o administrador a ser removido existe
        cur.execute("SELECT * FROM admin WHERE usuario_id_usuario = %s", (id_admin_remover,))
        admin_existente = cur.fetchone()

        if admin_existente:
            # Remove o administrador da lista de administradores
            cur.execute("DELETE FROM admin WHERE usuario_id_usuario = %s", (id_admin_remover,))
            conn.commit()
            print("Usuário com ID {} foi removido da lista de administradores.".format(id_admin_remover))
            opp=input("PRESSIONE QUALQUER TECLA: ")
            return True
        
        else:
            print("O ID do administrador {} não foi encontrado.".format(id_admin_remover))
            opp=input("PRESSIONE QUALQUER TECLA: ")

            return False

    except psycopg2.Error as e:
        conn.rollback()
        print("Erro ao remover o administrador da lista de administradores:", e)
        opp=input("PRESSIONE QUALQUER TECLA: ")
        return False


def tornar_admin(conn, cur, usuario_id, morada, super_admin):
    try:
        # Verifica se o usuário já é um administrador
        cur.execute("SELECT * FROM admin WHERE usuario_id_usuario = %s", (usuario_id,))
        admin_existente = cur.fetchone()        

        if not admin_existente:
            # Insere um novo registro se o usuário ainda não for um administrador
            cur.execute("INSERT INTO admin (morada, super_admin, usuario_id_usuario) VALUES (%s, %s, %s)",
                        (morada, super_admin, usuario_id))
            conn.commit()
            print("Usuário com ID {} tornou-se um administrador com sucesso!".format(usuario_id))
            
            # Remove o usuário da tabela de clientes
            cur.execute("DELETE FROM cliente WHERE usuario_id_usuario = %s", (usuario_id,))
            conn.commit()
            print("Usuário com ID {} removido da tabela de clientes.".format(usuario_id))
            
        else:
            print("Usuário com ID {} já é um administrador.".format(usuario_id))

    except psycopg2.Error as e:
        conn.rollback()
        print("Erro ao tornar o usuário um administrador:", e)


def verificar_admin(conn, cur, usuario_id):
    try:
        # Verifica se o usuário é um administrador
        cur.execute("SELECT * FROM admin WHERE usuario_id_usuario = %s", (usuario_id,))
        admin_existente = cur.fetchone()

        if admin_existente:
          
         return True
          
        else:
            return False

    except psycopg2.Error as e:
        print("Erro ao verificar se o usuário é um administrador:", e)
        return False


def alterar_preco_horario(conn, cur, fimds=True):
    try:
        # Seleciona os registros com FimDS igual ao parâmetro fornecido e ordena por preço crescente
        cur.execute("SELECT id, horas, preco FROM horario WHERE fimds = %s ORDER BY preco ASC", (fimds,))
        horarios = cur.fetchall()

        if not horarios:
            print("Não há horários disponíveis para alteração de preço com fimds igual a", fimds)
            op=input("Pressione qualquer tecla:")
            return

        print("Horários disponíveis para alteração de preço:")
        for horario in horarios:
            id_horario, hora, preco = horario
            print(f"ID: {id_horario}, Hora: {hora}, Preço: {preco}")

        id_horario_alterar = input("Digite o ID do horário para alterar o preço: ")

        # Verifica se o ID fornecido é válido
        if not id_horario_alterar.isdigit() or int(id_horario_alterar) not in [horario[0] for horario in horarios]:
            print("ID inválido. Por favor, insira um ID válido.")
            op=input("Pressione qualquer tecla:")
            limpar_ecra()
            alterar_preco_horario(conn,cur,fimds)
            

        novo_preco = input("Digite o novo preço: ")

        # Atualiza o preço na tabela horario
        cur.execute("UPDATE horario SET preco = %s WHERE id = %s", (novo_preco, id_horario_alterar))
        conn.commit()

        print("Preço atualizado com sucesso!")
        op=input("Pressione qualquer tecla:")

    except psycopg2.Error as e:
        conn.rollback()
        print("Erro ao alterar o preço:", e)
        op=input("Pressione qualquer tecla:")


def alterar_reserva(conn, cur, reserva_id, novo_id_camp, novo_id_hora):

    try:
        # Verificar se a reserva existe antes de tentar alterá-la
        cur.execute("SELECT * FROM Reservar WHERE id_reserva = %s", (reserva_id,))
        reserva = cur.fetchone()

        if not reserva:
            print("Reserva não encontrada.")
            return False

        # Executar o comando SQL para alterar a reserva
        cur.execute("UPDATE Reservar SET id_camp = %s, id_horario = %s WHERE id_reserva = %s",
                    (novo_id_camp, novo_id_hora, reserva_id))
        
        # Commit para confirmar a transação
        conn.commit()
        
        print("Reserva alterada com sucesso!")
        return True

    except (Exception, psycopg2.Error) as error:
        print("Erro ao alterar reserva:", error)
        return False


def listar_reservas(conn, cur):
    try:
        # Executando o comando SQL para selecionar todas as reservas
        sql_select = """SELECT id_reserva, data FROM Reservar"""
        cur.execute(sql_select)
        
        # Recuperando todas as reservas
        reservas = cur.fetchall()

        # Exibindo as reservas
        print("Reservas:")
        for reserva in reservas:
            print("ID:", reserva[0], "- Data da Reserva:", reserva[1])

    except (Exception, psycopg2.Error) as error:
        print("Erro ao listar reservas:", error)




def cancelar_reserva(conn, cur, reserva_id):
    try:
        get_reserva_info(conn,cur,reserva_id)
        # Executando o comando SQL para eliminar a reserva
        sql_delete = """DELETE FROM reservar WHERE id_reserva = %s;"""
        cur.execute(sql_delete, (reserva_id,))
        
        # Commit para confirmar a transação
        conn.commit()
        
        print("Reserva cancelada e eliminada com sucesso!")

    except (Exception, psycopg2.Error) as error:
        print("Erro ao cancelar reserva:", error)




def get_reserva_info(conn, cur, id_reserva):
    try:
        # Obter a hora e o dia da reserva da tabela 'reservar'
        cur.execute("SELECT data FROM reservar WHERE id_reserva = %s", (id_reserva,))
        dia_reserva1 = cur.fetchone()
       
        cur.execute("SELECT id_horario FROM reservar WHERE id_reserva = %s", (id_reserva,))
        id_horario = cur.fetchone()

        cur.execute("SELECT horas FROM horario WHERE id = %s", (id_horario,))
        hora_reserva = cur.fetchone()
        
        if dia_reserva1:
            
            # Buscar os usuários na lista de espera com a mesma hora e dia
           cur.execute("SELECT cliente_usuario_id_usuario FROM listadeespera WHERE hora = %s AND data = %s AND hora_notificada=False", (hora_reserva, dia_reserva1))
           usuarios_listadeespera = cur.fetchall()
           mensagem="Campos disponiveis para o horario selecionado"
           if usuarios_listadeespera:
                print("Usuários na lista de espera para a mesma hora e dia da reserva:")
                for usuario in usuarios_listadeespera:
                    print(usuario[0])
                    enviar_mensagem_admin_a_especifico(conn,cur,mensagem,usuario)
                    atualizar_hora_notificada(conn,cur,usuario)
                
                limpar_ecra()
                print("NOTIFICAÇÃO ENVIADA")    
                input("Pressione qualquer tecla")
           else:
                print("Nenhum usuário encontrado na lista de espera para a mesma hora e dia da reserva.")
        else:
            print("Reserva não encontrada.")

    except psycopg2.Error as e:
        print("Erro ao obter informações da reserva:", e)





#-------------------------------------------------------------------------------------------
 
 
 
#FUNÇÕES DAS MENSAGENS----------------------------------------------------------------------

def contar_vistas_falsas(conn, cur, cliente_id):
    try:
        # Executa a consulta SQL para contar o número de vezes que 'vista' é false para o cliente especificado
        cur.execute("SELECT COUNT(*) FROM visualizacao WHERE cliente_usuario_id_usuario = %s AND vista = false", (cliente_id,))
        contador = cur.fetchone()[0]  # Obtém o resultado da consulta
        
        return contador
    
    except psycopg2.Error as e:
        print("Erro ao contar vistas falsas:", e)
        return None
    
    
def marcar_mensagens_como_vistas(conn, cur, usuario_id):
    try:
        # Atualiza a variável 'vista' para True na tabela 'visualizacao' para o usuário especificado
        cur.execute("UPDATE visualizacao SET vista = true WHERE cliente_usuario_id_usuario = %s", (usuario_id,))
        conn.commit()
        print("Mensagens marcadas como visualizadas para o usuário {}.".format(usuario_id))
    except psycopg2.Error as e:
        print("Erro ao marcar mensagens como visualizadas:", e)


def imprimir_mensagens_usuario(conn, cur, usuario_id, mostrar_lidas=False):
    try:
        if not mostrar_lidas:
            # Marca todas as mensagens como visualizadas se estiverem sendo exibidas como não lidas
            cur.execute("UPDATE visualizacao SET vista = true WHERE cliente_usuario_id_usuario = %s AND vista = false", (usuario_id,))
            conn.commit()

        # Executa a consulta SQL para obter as mensagens enviadas para o usuário especificado
        if mostrar_lidas:
            cur.execute("SELECT mensagem__id_mensagem FROM visualizacao WHERE cliente_usuario_id_usuario = %s AND vista = false", (usuario_id,))
            
        else:
            cur.execute("SELECT mensagem__id_mensagem FROM visualizacao WHERE cliente_usuario_id_usuario = %s AND vista = true", (usuario_id,))
        mensagens_ids = cur.fetchall()  # Obtém os IDs das mensagens

        # Imprime as mensagens
        if mensagens_ids:
            print("Mensagens para o usuário {}: ".format(usuario_id))
            for mensagem_id in mensagens_ids:
                cur.execute("SELECT texto FROM mensagem_ WHERE id_mensagem = %s", (mensagem_id,))
                mensagem_texto = cur.fetchone()[0]  # Obtém o texto da mensagem

                print("- ", mensagem_texto)
                
            op=input("Pressione qualquer tecla:")

        else:
            print("Nenhuma mensagem encontrada para o usuário {}.".format(usuario_id))
            op=input("Pressione qualquer tecla:")
    
    except psycopg2.Error as e:
        print("Erro ao obter ou marcar mensagens do usuário:", e)
        op=input("Pressione qualquer tecla:")


#---------------------------------------------------------------------------------------------

try:
    # Conexão com o banco de dados
    conn = psycopg2.connect("host=localhost dbname=Padel_Mondego user=postgres password=postgres")
    cur = conn.cursor()
    

   #ID CAMPO 1- Campo Mondego 
   #ID CAMPO 2- Campo Grande 
   #ID CAMPO 3- Campo Rural 
   
      
    while True:
        limpar_ecra()
        # Chamar a função para criar a conta do cliente
        print("Bem-Vindo Ao Padel-Mondego")
        print("1-Criar conta")
        print("2-Login")
        print("3-Sair")
        op= input("->:")
        
        if op=="1":
            limpar_ecra()      
            id=criar_conta(conn, cur)
            menu_Cliente(conn,cur,id)

        if op=="2":
            limpar_ecra()
            id=fazer_login(conn,cur)
            
            admin_verifica=verificar_admin(conn,cur,id)
            if admin_verifica==False: 
                 menu_Cliente(conn,cur,id)
            else:
                menu_Admin(conn,cur,id)     
            
            
        if op=="3":
            limpar_ecra()
            print("Volte rápido :( ")
            break



except psycopg2.Error as e:
    print("Erro ao conectar ao banco de dados:", e)
    op= input("->:")
    
finally:
    # Fechar conexão com o banco de dados
    if conn:
        cur.close()
        conn.close()


