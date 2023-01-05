from iqoptionapi.stable_api import IQ_Option
import configparser
from datetime import datetime
from pytz import timezone

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

info = dict(API.get_profile_ansyc())

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





