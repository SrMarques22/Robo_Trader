from iqoptionapi.stable_api import IQ_Option
import configparser

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

#Aula 2 coletando dados da conta do usuario:


#print(info) para pegar os meus dados do site:

for a in info:
    for k, v in info.items():
        print(k,':',v)

dataCriacaoConta = info['created']
print('dados de criação da conta: ',dataCriacaoConta)
