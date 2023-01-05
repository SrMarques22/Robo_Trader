from iqoptionapi.stable_api import IQ_Option
import configparser

#email = 'ti....'
#senha = 'Ti...'

'''
API = IQ_Option(email, senha)
API.connect()
#Mudar conta para DEMO, em caso de escolha da conta oficial, usar a 'REAL':
API.change_balance('PRACTICE')

if API.check_connect() == True:
    print('Conectado')
else:
    print('Não conectado')
'''
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

print(conectado)

'''
# O tipo de conta foi definido padrão apenas para evitar que conecte em outra neste momento
def fazerConexao(email, senha, tipoconta='PRACTICE'):
    API = IQ_Option(email, senha)

    API.connect()

    conectado = False
    # Conecta no ambiente de TREINO:
    API.change_balance('PRACTICE')  # Ou REAL

    if API.check_connect() == True:
        print('Conectado')
        conectado = True
    else:
        print('Não conectado')
        conectado = False
    return API, conectado


API, conectado = fazerConexao(email, senha)
print(conectado)
'''
