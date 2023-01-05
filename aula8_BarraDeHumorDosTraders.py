from iqoptionapi.stable_api import IQ_Option
import configparser
from datetime import datetime
from pytz import timezone
import time
import pandas as pd



arq = configparser.RawConfigParser()
arq.read(r'C:\Users\bruno.marques\PycharmProjects\untitled\RoboTrader\config.txt')

email = arq.get('LOGIN','email')
senha = arq.get('LOGIN','senha')


def fazerConexao(email,senha, tipoConta ='PRACTICE'):
    API = IQ_Option(email, senha)
    API.connect()
    # Mudar conta para DEMO, em caso de escolha da conta oficial, usar a 'REAL':
    API.change_balance(tipoConta)

    conectado = False

    if API.check_connect() == True:
        print('Conectado')
        conectado = True
    else:
        print('Não conectado')
        conectado = False
    return API, conectado



API, conectado = fazerConexao(email,senha)

info = API.get_profile_ansyc()

#criar uma função para realizar a conversão do tmestamp (data e hora)

def timestamp2dataHora(x,timezone_ ='America/Sao_paulo'):
    d_rs = datetime.fromtimestamp(x, tz=timezone(timezone_))
    return str(d_rs)


#Função para pegar informações da conta
def infosContaIQ(api):
    conta = api.get_profile_ansyc()
    nome = conta['name']
    moeda = conta['currency']
    data_criacao = timestamp2dataHora(conta['created'])
    return conta,nome,moeda,data_criacao

def coletaCandle():
    tempo = time.time()
    candles = []
    #O Underline abaixo serve quando precisa fazer um for na estrutura mas não precisa mostrar as informações, assim não precisa ir nenhuma variavel
    for _ in range(2):
        c = API.get_candles(ativo,60,1000,tempo)
        candles = c + candles
        #Posição 0 são valores, posição 1 são campos
        tempo = c[0]['from']-1
    return candles

ativo = 'EURUSD'
API.start_mood_stream(ativo)
#----------
#Aula 8: Barra de humor dos traders
#----------

#A barra de humor dos traders é a barra a esquerda que mostra se a maioria dos traders acha que o ativo vai cair, ou subir.
# A BARRA DE HUMOR SERVE APENAS PARA O TIPO DE OPERAÇÃO BINÁRIA..... O TIPO DIGITAL NÃO FUNCIONA !!!!!!
print()
print('Barra de Mood (humor) dos traders:')

API.start_mood_stream(ativo)

#While abaixo comentado para não rodar infinitamente durante os testes
'''
while True:
    m =  API.get_traders_mood(ativo)
    #o valor 2 é a quantidade de casas decimais que vou mostrar o valor
    #Round serve para arredondar o valor, dessa forma, tem uma precisão, e a multiplicação por 1000 faz parte do calculo
    print(100*round(m,2))
    time.sleep(1)
#Processo abaixo stopa o stream de coleta das informações.
API.stop_mood_stream(ativo)
'''


