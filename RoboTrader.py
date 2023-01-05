import sys

from iqoptionapi.stable_api import IQ_Option
import configparser
from datetime import datetime
from pytz import timezone
import time
from time import sleep
import pandas as pd

arq = configparser.RawConfigParser()
arq.read(r'C:\Users\bruno.marques\PycharmProjects\unlited\RoboTrader\config.txt')

email = arq.get('LOGIN', 'email')
senha = arq.get('LOGIN', 'senha')

#Função para fazer a conexão com a conta:
#Para conta treino usar: PRACTICE, para oficial usar: REAL

def FazerConexao(email, senha, tipoConta='PRACTICE'):
    API = IQ_Option(email, senha)
    API.connect()
    # Mudar conta para DEMO, em caso de escolha da conta oficial, usar a 'REAL':
    API.change_balance(tipoConta)

    conectado = False

    if API.check_connect() == True:
        print('Conectado a base IQOPTION')
        conectado = True
    else:
        print('Não conectado')
        conectado = False
    return API, conectado


# Função para realizar a conversão do tmestamp (data e hora)
def Timestamp2dataHora(x, timezone_='America/Sao_paulo'):
    d_rs = datetime.fromtimestamp(x, tz=timezone(timezone_))
    return str(d_rs)

#Função para coletar oPayout do Ativo:
def Payout(par,tipo,API,timeframe=1):
    #Coletar dados do tipo Binário (turbo)
    #Turbo é o tipo binário, caso queira usar em digital, colocar abaixo, "digital"
    if tipo == 'turbo':
        #pegar todos os lucros
        a = API.get_all_profit()
        #abaixo se multiplica por 100 para obter o valor em forma de percentual
        return int(100 * a[par]['turbo'])

    # Coletar dados do tipo digital:
    elif tipo == 'digital':
        API.subscribe_strike_list(par,timeframe)
        while True:
            d = API.get_digital_current_profit(par,timeframe)
            if d != False:
                d = int(d)
                break
            time.sleep(1)
        API.unsubscribe_strike_list(par,timeframe)
        return d



# Função para pegar informações da conta
def InfosContaIQ(api):
    conta = api.get_profile_ansyc()
    nome = conta['name']
    moeda = conta['currency']
    data_criacao = Timestamp2dataHora(conta['created'])
    return conta, nome, moeda, data_criacao

#Função para coletar dados da vela
def ColetaCandle(ativo,API):
    tempo = time.time()
    candles = []
    # O Underline abaixo serve quando precisa fazer um for na estrutura mas não precisa mostrar as informações, assim não precisa ir nenhuma variavel
    for _ in range(2):
        c = API.get_candles(ativo, 60, 1000, tempo)
        candles = c + candles
        # Posição 0 são valores, posição 1 são campos
        tempo = c[0]['from'] - 1
    return candles

def ColetaCorVelas(ativo,API):
    """
    # Abaixo criamos a lógica colocada na observação acima, vamos analisar as ulimas 3 velas para aplicar a operação:
    # OBS: a vela de posição 0 é a mais antiga, sendo a antepenultima vela gerada no grafico e a vela de posição 2 é a mais recente mostrada na tela

    # A = É referente a velas Altas
    # B = É referente a velas Baixas
    # D = É referente a Dojin (velas que ficam no meio)
    # A explicação da lógica acima é: A vela na opsição 0 vai ser A se o OPEN for menor que o CLOSE, senão,
    # vai ser B se o CLOSE for MENOR que o OPEN, senão, vai ser DOJIN!

    """
    #O valo 60 abaixo é referente aos minutos e o 3 é a quantidade de velas para analise
    #velas = API.get_candles(ativo, 60, 3, time.time())
    velas = API.get_candles(ativo, 60, 5, time.time())
    #Abaixo é a regra básica que vamos usar para qualquer estratégia, só precisamos incluir a quantidade de velas
    velas[0] = 'A' if velas[0]['open'] < velas[0]['close'] else 'B' if velas[0]['open'] > velas[0]['close'] else 'D'
    velas[1] = 'A' if velas[1]['open'] < velas[1]['close'] else 'B' if velas[1]['open'] > velas[1]['close'] else 'D'
    velas[2] = 'A' if velas[2]['open'] < velas[2]['close'] else 'B' if velas[2]['open'] > velas[2]['close'] else 'D'
    velas[3] = 'A' if velas[3]['open'] < velas[3]['close'] else 'B' if velas[3]['open'] > velas[3]['close'] else 'D'
    velas[4] = 'A' if velas[4]['open'] < velas[4]['close'] else 'B' if velas[4]['open'] > velas[4]['close'] else 'D'
    cores = velas[0] + ' ' + velas[1] + ' ' + velas[2] + ' ' + velas[3] + ' ' + velas[4]
    return cores

def Direcional_MHI(cores):
    direcao = ''
    if cores.count('A')> cores.count('B') and cores.count('D')==0:
        direcao = 'put'
        #direcao = 'call'
    if cores.count('B')> cores.count('A') and cores.count('D')==0:
        direcao = 'call'
        #direcao = 'put'
    return direcao

#Função para criar um stop win ou stop loss
def Stop(lucro,gain,loss):
    """

    :param lucro: Valor Total das Operações
    :param gain: Valor Total ganho
    :param loss: Valor Total perdido
    o argumento abaixo sys.exit() serve para finalizar o Robo no computador assim que finalizar a configuração
    :return:
    """
    if lucro <= -loss:
        print('Atividade finalizada pelo STOP LOSS')
        print('A Resiliência É A Chave Para O Sucesso!!!')
        sys.exit()
    if lucro >= gain:
        print('Atividade finalizada pelo STOP WIN')
        print('O Sucesso Está A Caminho $$$')
        sys.exit()

#Função para realizar Martingale
def Martingale(entrada,payout):
    """

    :param entrada: Operação de Put ou Call
    :param payout: Payout é a porcentagem que o ativo está pagando
    calculo do Martingale: aposta = valor * (1+payout)/payout
    """
    aposta = entrada * (1 + payout) / payout
    return aposta

#Conectando ao IQOPTION e sincronizando o perfil:
#OBS: Caso queira, pode colocar todas as chamadas dentro do arquivo de "config.txt" na função de conexão que coloquei os dados de login

API, conectado = FazerConexao(email, senha)
info = API.get_profile_ansyc()

#-=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=-

#Dados de Operação:


ativo = 'EURUSD'
#ativo = 'EURUSD-OTC'
payout = Payout(ativo,'digital',API)

stop_win = 20 #Ganho total diário
stop_loss = 15 #Perda total diário
valor_entrada_b = 5 #Valor de cada entrada
martingale = 1 #Quantidade de Martingales em caso de perdas
delay = 2 #Aqui posso definir o Delay que eu quiser

lucro = 0
cont = 0 #Variavel para contar o numero de Candles
total_trades = 0 #se eu colocar o valor 1 ele vai operar 2 vezes, se eu deixar 2 serão 3 operações....
n_espera = 3 #Dicionário que coleta a quantidade de Candles de espera para os ciclos
novoCandle = False

#-=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=-



d = datetime.now(tz=timezone('America/Sao_Paulo'))
print('Inicio da Operação:',d.hour,':',d.minute)
print('')
while True:

    d = datetime.now(tz=timezone('America/Sao_Paulo'))
    hora = d.hour
    minutos = d.minute
    segundos = d.second
    milesimos = d.microsecond
    entrar = False

    #Define em que momento entrar com a operação
    novoCandle = (segundos == (30-delay))
    #Looping de avaliação de Candles

    if (novoCandle):
        cont += 1

    print('Ativo: ',ativo,' - Nova Vela: ', novoCandle, " - Posição Da Vela: ", cont, "° - Segundos: ", segundos, " - Total De Operações: ", total_trades)

    if(cont == n_espera):
        entrar = True
        cont = 0 #Definindo 0 na contagem para zerar a contagem assim que operar

    #Looping Operacional "ENTRAR",aqui fica a lógica
    if entrar:
        print('\n\n ATENÇÃO: Robô efetuando o Trade!')
        print('')
        print(':::: Verificando as cores das Candles: ', end='')
        #A informação das velas abaixo não esta sendo utilizada
        velas = API.get_candles(ativo,60,5,time.time())
        cores = ColetaCorVelas(ativo,API)
        direcao = Direcional_MHI(cores)


        if direcao =='': #Aqui se tiver Dojin dentro da minha operação não opera
            print('Operação não efetuada, cores das Candles ficaram imparciais')
            print('')
            entrar = False
        else: #Aqui opera conforme estrategia
            print('As ultimas cores foram: ',cores)

        if(direcao == 'call' or direcao =='put'):
            print('A direção sugere uma operação de: ',direcao)
            valor_entrada = valor_entrada_b

            for i in range(martingale+1):

                #Abaixo processo Digital, status é o responsável pela operação:
                status,id_ = API.buy_digital_spot(ativo,valor_entrada,direcao,1)
                cont += 1
                print('Operando em: ',direcao)
                print('Aguarde...')
                total_trades +=1 #soma quantidade de trades

                #Se Operar:
                if status:
                    while True:
                        #Acompanha o resultado da operação:
                        status,valor = API.check_win_digital_v2(id_)


                        if status:
                            valor = valor if valor > 0 else float('-' + str(abs(valor_entrada)))
                            #Acumulo de lucro:
                            lucro += round(valor,2)

                            print('-------'*10)
                            print('Resultado: ', end='')
                            if valor > 0:
                                print('')
                                print('$ WIN $ / ',' Valor Recebido: ', round(valor,2), '/',' Valor Total: ',round(lucro,2))
                                print('')
                                cont = 0
                            else:
                                print('')
                                print('! LOSS ! / ',' Valor Recebido: ', round(valor,2), '/',' Valor Total: ',round(lucro,2))
                                print('')
                                #adicionei pra teste o cont=0 abaixo
                                cont = 0
                                if i > 0:
                                    print('')
                                    print('Realizado o',str(i),'° Martingale ! ')
                                    print('')
                                else:
                                    print('')
                            #print(' WIN /' if valor > 0 else 'LOSS / ',' Valor Recebido: ', round(valor,2), '/',' Valor Total: ',round(lucro,2),('/'+str(i)+ 'Aplicando Martingale' if i > 0 else ''))
                            # Avalia se precisa por Matingale:
                            valor_entrada = Martingale(valor_entrada, payout / 100)

                            #Avalia se precisa dar stopWin ou Loss
                            Stop(lucro,stop_win,stop_loss)

                            if(valor > 0 and i > 0):
                                cont += 1
                                #print('::: Saimos no WIN e precisamos contar UM: ',cont)
                            entrar = False
                            break
                    if valor > 0:
                        break

                else:
                    print('\n ERRO AO REALIZAR OPERAÇÃO \n\n')
                    cont = 0
                if(i>0):
                    cont += 1

                print('Vamos operar mais uma '+ direcao +", Com entrada de ",round(valor_entrada,2), ", e Payout = ",payout)
                print('')
    time.sleep(1)