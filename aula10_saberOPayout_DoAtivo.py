from iqoptionapi.stable_api import IQ_Option
import configparser
from datetime import datetime
from pytz import timezone
import time
import pandas as pd

arq = configparser.RawConfigParser()
arq.read(r'C:\Users\bruno.marques\PycharmProjects\untitled\RoboTrader\config.txt')

email = arq.get('LOGIN', 'email')
senha = arq.get('LOGIN', 'senha')

#Função para fazer a conexão com a conta:
def fazerConexao(email, senha, tipoConta='PRACTICE'):
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


API, conectado = fazerConexao(email, senha)

info = API.get_profile_ansyc()


# Função para realizar a conversão do tmestamp (data e hora)
def timestamp2dataHora(x, timezone_='America/Sao_paulo'):
    d_rs = datetime.fromtimestamp(x, tz=timezone(timezone_))
    return str(d_rs)

#Função para coletar oPayout do Ativo:
def payout(par,tipo,timeframe=1):
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
def infosContaIQ(api):
    conta = api.get_profile_ansyc()
    nome = conta['name']
    moeda = conta['currency']
    data_criacao = timestamp2dataHora(conta['created'])
    return conta, nome, moeda, data_criacao

#Função para coletar dados da vela
def coletaCandle():
    tempo = time.time()
    candles = []
    # O Underline abaixo serve quando precisa fazer um for na estrutura mas não precisa mostrar as informações, assim não precisa ir nenhuma variavel
    for _ in range(2):
        c = API.get_candles(ativo, 60, 1000, tempo)
        candles = c + candles
        # Posição 0 são valores, posição 1 são campos
        tempo = c[0]['from'] - 1
    return candles


ativo = 'EURUSD'
API.start_mood_stream(ativo)
# ----------
# Aula 8: Barra de humor dos traders
# ----------

# A barra de humor dos traders é a barra a esquerda que mostra se a maioria dos traders acha que o ativo vai cair, ou subir.
# A BARRA DE HUMOR SERVE APENAS PARA O TIPO DE OPERAÇÃO BINÁRIA..... O TIPO DIGITAL NÃO FUNCIONA !!!!!!

# While abaixo comentado para não rodar infinitamente durante os testes
'''
print()
print('Barra de Mood (humor) dos traders:')

API.start_mood_stream(ativo)

while True:
    m =  API.get_traders_mood(ativo)
    #o valor 2 é a quantidade de casas decimais que vou mostrar o valor
    #Round serve para arredondar o valor, dessa forma, tem uma precisão, e a multiplicação por 1000 faz parte do calculo
    print(100*round(m,2))
    time.sleep(1)
#Processo abaixo stopa o stream de coleta das informações.
API.stop_mood_stream(ativo)
'''

# ----------
# Aula 9: Coletando dados de Ativos (moedas) disponíveis para operar
# ----------
print('Pegando ativos disponíveis')
a = API.get_all_ACTIVES_OPCODE().items()

# Abaixo nada mais é do que um FOR pegando chave e valor com o .items, montado em apenas uma linha
ID = dict({(codigo, ativo_c) for ativo_c, codigo in API.get_all_ACTIVES_OPCODE().items()})
# Se eu quiser saber qual o nome do ativo pelo código, basta filtrar da seguinte forma e o sistema retornará o nome do ativo:

# print(ID[10])


# For para pegar todos os ativos e seus IDs
'''
for v,k in ID.items():
    print(k,v)
'''

# Para verificar o humor de varios ativos, podemos fazer o seguinte:
ativo1 = 'EURUSD'
ativo2 = 'EURCAD'

API.start_mood_stream(ativo1)
API.start_mood_stream(ativo2)

# OBS Apenas reforçando, o retorno da barra de humor mostrará sempre o da barra de ALTA (VERDE)
'''
while True:
    m = API.get_all_traders_mood()
    # Mostrar o nome do arquivo, e vai pegar o código e mostrar o nome e o valor do humor dos ativos 1 e 2
    for i in m:
        print(ID[i] + ': ' + str(100 * round(m[i], 2)))
    print('-=-=-' * 10)
    print(time.sleep(1))
'''
# ----------
# Aula 10: Coletando dados de Payout do Ativo
# ----------

# função payout:
ativos = API.get_all_open_time()

print()
print('-='*30)
print()

# Aqui o programa vai rastrear só os ativos tipo binários
for ativo in ativos['turbo']:
    #Aqui abaixo, vai rastrear todos abertos:
    if ativos['turbo'][ativo]['open'] == True:
        print('[ TURBO ]: '+ativo+' | Payout: '+str(payout(ativo, 'turbo',1)))
print()
print('-='*30)
print()

# Aqui o programa vai rastrear só os ativos tipo digital
for ativo in ativos['digital']:
    #Aqui abaixo, vai rastrear todos abertos:
    if ativos['digital'][ativo]['open'] == True:
        print('[ DIGITAL ]: '+ativo+' | Payout: '+str(payout(ativo, 'digital',1)))

print()
print('-='*30)
print()
