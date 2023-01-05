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
#Aula 5: Dataframes - Pandas
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
print()
#----------
#Aula 5: Coletando diversos dados das Candles
#----------

#Obs: o máximo que o programa pode coletar é 1.000 dados de velas então na minha variavel Candles_varias não consigo definir mais de mil,
#mas é possível acumular dados para coletar mais
candles_varias = API.get_candles(ativo,60,1500,time.time())
quant_candles = len(candles_varias)
print(quant_candles)
# Então nesse caso, como 1500 são muitas informações e a api não comporta, etão podemos criar mais uma variavel para que seja acrescentado a quantidade
#de candles pra trás vinculando a variavel anterior e colocando -1 para que o sistema pegue a partir da ultima candle filtrada na primeira variavel "candles_varias"

candles_varias_2 = API.get_candles(ativo,60,500,candles_varias[0]['from']-1)
print('Mostrando a data e hora convertida no from')
print(timestamp2dataHora(candles_varias_2[0]['from']))
#print('mostrando as informações da ultima vela do filtro da variavel candles_varias que foi definida na variavel candles_varias_2')
#print(candles_varias_2)

#criando uma lista para por todos os dados:
print('mostrando as somas dos valores para ver se estão corretas')
ct = []
ct = candles_varias + candles_varias_2
#no caso abaixo tem que dar 1.500 dados que é a soma das minhas junções acima
print(len(ct))
print()

#Coleta de candles acima de 1.000 usando a função criada coletaCandles:

novos_candles = coletaCandle()
print('Quantidade definida no coletaCandle')
print(len(novos_candles))

#----------
#Aula 7: Ticks, coletando dados em tempo real do preços
#----------

# Ticks são as variações de preço que aparecem na lista branca na esquerda que sobe e desce e mostra alguns números no iqoption

#O 1 abaixo serve para mostrar o número máximo de informação
#Stream é uma coleta em tempo real dos dados, vai ficar rodando por baixo
ativo = 'EURUSD'
API.start_candles_stream(ativo,60,1)
ticks = API.get_realtime_candles(ativo,60)
print('Tick informações do tick em tempo real')
for tick in ticks:
    print(ticks[tick])

while True:
    for tick in ticks:
        print(ticks[tick]['close'])
        time.sleep(1)
#Processo abaixo para o stream de coleta das informações.
API.stop_candles_stream(ativo,60)