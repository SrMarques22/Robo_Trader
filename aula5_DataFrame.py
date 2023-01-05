from iqoptionapi.stable_api import IQ_Option
import configparser
from datetime import datetime
from pytz import timezone
import time
import pandas as pd

#email = 'ti....'
#senha = 'Ti...'


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

print(conectado)

#criar uma função para realizar a conversão do tmestamp (data e hora)

def timestamp2dataHora(x,timezone_ ='America/Sao_paulo'):
    d_rs = datetime.fromtimestamp(x, tz=timezone(timezone_))
    return str(d_rs)

#define a variavel que terá os dados de criação da conta:
dataCriacaoConta = info['created']
# Usa a função de converter
dn = timestamp2dataHora(dataCriacaoConta)
#Mostra natela o valor convertido
print('data e hora funcao de converter timestamp:',dn)

#Função para pegar informações da conta
def infosContaIQ(api):
    conta = api.get_profile_ansyc()
    nome = conta['name']
    moeda = conta['currency']
    data_criacao = timestamp2dataHora(conta['created'])
    return conta,nome,moeda,data_criacao

conta,nome,moeda,data_criacao = infosContaIQ(API)

print('Nome: ',nome,'\nMoeda: ',moeda,'\nData de Criação da conta: ',data_criacao)


#----------
#Aula 2 coletando dados da conta do usuario:
#----------

#print(info) para pegar os meus dados do site:
#Obs: com o FOR, eu pego todas as informações, caso contrário, não é necessário usar o FOR
'''
for k, v in info.items():
    print(k,':',v)
'''



#----------
#Aula 3: Transformação do Timestamp
#----------
'''
Transformar os valores de data e hora do site

 A função tz serve para referenciar a zona que data/hora que vamos pegar
 A informação GMT quer dizer que pegamos a zona do Meridiano de Greenwich
 Caso queira, posso colocar o timezone da horario de Brasilia, colocando como no segundo exemplo

#d = datetime.fromtimestamp(dataCriacaoConta,tz=timezone('GMT'))
#d_rs = datetime.fromtimestamp(dataCriacaoConta,tz=timezone('America/Sao_Paulo'))
'''
#----------
# Aula 4 - Candles:
#----------

# Se for no find usar EURUSD-OST
ativo = 'EURUSD'

#------
#IMPORTANTE!!!
#------

# O Ativo é a moeda que escolher, mesmo nome do site, o 60 é a operação (60 sec) e o 2 são as quantidades de velas para mostrar
#obs:o time.time() pega com exatidão o horário,segundos e milisegundos do momento atual
candles = API.get_candles(ativo,60,2,time.time())

#Lembrando que devido ao tipo de visualação tem que estar em 1M no IQOPTION
'''
for a in candles:
    print(a)
'''

#----------
#Aula 5: Dataframes
#----------
#Pegando os dados e transformando o dicionario,lista,etc.. em um Dataframe para facilitar visualização de dados

df = pd.DataFrame(candles)
print(df)


#resultado:
'''
        id        from                   at  ...       min       max  volume
0  1582655  1643202240  1643202300000000000  ...  1.127875  1.128025     287
1  1582656  1643202300  1643202360000000000  ...  1.127855  1.127995     281

[2 rows x 9 columns]
'''

#Para localizar as informações de maneira mais precisa no meu dataframe, posso fazer o seguinte:
#No caso do fitro abaixo, estou pegando a liha 0 e a coluna min
minimo = df.loc[0,'from']
print('Valor mínimo: ',minimo)
print()
# Se eu quiser pegar todos os dados de uma linha ou oluna, basta apenas referenciar, um ou outro sem o "LOC" ex:
volume =df['volume']
print('dados de volume:')
print(volume)
print()

#Saber uma média dos valores:
print('Média dos valores do campo escolhido valores')
print(df['volume'].describe())

#Pegar todas as colunas:
print()
print('Todas as colunas:')
print(df.columns)

# Converter data e hora dentro do meu filtro das candles:
# Unit = s é a unidade de segundos
print()
#convertendo o timestamp em datetime da coluna from do meu filtro
print('Filtro de candle com datetime correto na coluna FROM')
candles_ok = df['from'] = pd.to_datetime(df['from'], unit='s')
#mostrar apenas os dados da coluna FROM
print(candles_ok)
print()
#Convertendo a coluna T0
print('convertendo os dados de TO')
candles_ok_to = df['to'] = pd.to_datetime(df['to'], unit='s')
print(candles_ok_to)