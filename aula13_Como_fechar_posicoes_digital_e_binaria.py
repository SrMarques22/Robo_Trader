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
def payout(par,tipo,API,timeframe=1):
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
def coletaCandle(ativo,API):
    tempo = time.time()
    candles = []
    # O Underline abaixo serve quando precisa fazer um for na estrutura mas não precisa mostrar as informações, assim não precisa ir nenhuma variavel
    for _ in range(2):
        c = API.get_candles(ativo, 60, 1000, tempo)
        candles = c + candles
        # Posição 0 são valores, posição 1 são campos
        tempo = c[0]['from'] - 1
    return candles


#ativo = 'EURUSD'
#API.start_mood_stream(ativo)
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

'''
print('Pegando ativos disponíveis')
a = API.get_all_ACTIVES_OPCODE().items()

# Abaixo nada mais é do que um FOR pegando chave e valor com o .items, montado em apenas uma linha
ID = dict({(codigo, ativo_c) for ativo_c, codigo in API.get_all_ACTIVES_OPCODE().items()})
'''
# Se eu quiser saber qual o nome do ativo pelo código, basta filtrar da seguinte forma e o sistema retornará o nome do ativo:

# print(ID[10])


# For para pegar todos os ativos e seus IDs
'''
for v,k in ID.items():
    print(k,v)
'''

# Para verificar o humor de varios ativos, podemos fazer o seguinte:
'''
ativo1 = 'EURUSD'
ativo2 = 'EURCAD'

API.start_mood_stream(ativo1)
API.start_mood_stream(ativo2)
'''
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
'''
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
'''
# ----------
# Aula 11: Operando em compra e venda e operando em OTC
# ----------

#Caso esteja operando em OTC, deverá utilizar a definição com -OTC conforme abaixo
#ativo = 'USDCHF-OTC'
'''
ativo = 'EURJPY-OTC'
API.start_mood_stream(ativo)
#Lote é o valor que quer aplicar
lotes = 2
#A direção put indica uma operação de venda, call indica compra
direcao = 'put'
timeframe = 1 #Tempo grafico
'''
'''
#As referencias abaixo indicam a ordem: PREÇO(LOTES), o ATIVO, AÇÃO(call ou put) e tempo de expiração(timeframe que está definido em 1 min)
status, ID = API.buy(lotes,ativo,direcao,timeframe)

#Abaixo é para pegar as informações da operação direcionada acima se deu WIN ou LOOSE

if status:
    # Esssa função de check retorna dois valores por isso deve ser referenciado por 2 campos
    print(API.check_win_v3(ID))
    print('\n')
    print(API.check_win_v4(ID))

# Mostar a situação lucro positivo, ou negativo
if status:
    #Esssa função de check retorna dois valores por isso deve ser referenciado por 2 campos
    situacao, lucro = API.check_win_v3(ID)
    print()
    print ('Situação =',situacao,f' | Lucro = {lucro:.2f}')

'''

# ----------
# Aula 12: Operando em compra e venda no tipo DIGITAL
# ----------

#filtros na seguinte ordem: Ativo, valor aplicado, Ação(compra ou venda) e duração (minuto a ser operado ex: 1M, 5M...)
'''
print('Aplicando digital')
'''
# A ordem do digital é diferente, segue: active,amount,action,duration
'''
status, ID = API.buy_digital_spot(ativo, lotes, direcao, timeframe)

for a in range(1,94):
    sleep(1)

#função de verificar status da operação
isWin, lucro = API.check_win_digital_v2(ID)




if lucro > 0:
    print(f'Resultado: WIN | Lucro = {lucro:.2f}')

else:
    print(f'Resultado: LOSE | Prejuizo = {lucro:.2f}')

'''
#os dois IFs abaixo sao refetentes a condição para verificar MOSTRAR o status da operação, win ou lose:
'''
if status:
    # Esssa função de check retorna dois valores por isso deve ser referenciado por 2 campos
    print(API.check_win_digital_v2(ID))
    print('\n')
    print(API.check_win_digital_v2(ID))

# Mostar a situação lucro positivo, ou negativo
if status:
    #Esssa função de check retorna dois valores por isso deve ser referenciado por 2 campos
    situacao, lucro = API.check_win_digital_v2(ID)
    print()
    print (f'Situação = {situacao} | Lucro = {lucro:.2f}')

'''

#
#Como fechar posições SELL, Digital (Venda antes do prazo acabar):
#
#OBS: Na opção DIGITAL, podemos vender a operação até o ultimo segundo!!!

'''
ativo = 'EURUSD'
API.start_mood_stream(ativo)
#Lote é o valor que quer aplicar
lotes = 2
#A direção put indica uma operação de venda, call indica compra
direcao = 'put'
timeframe = 1 #Tempo grafico


print('Aplicando digital')
'''
# A ordem do digital é diferente, segue: active,amount,action,duration

'''
status, ID = API.buy_digital_spot(ativo, lotes, direcao, timeframe)

if status:
    print('Operação realizada com sucesso')
else:
    print('Não foi possível enviar a solicitação devido ao encerramento da Candle anterior')

#Definindo um valor para encerrar a operação
print('7 Segundos para o encerramento')
time.sleep(7)
status_close = API.close_digital_option(ID) #Comando para vender a operção !
print(status_close) #Mostra apenas se o comando acima foi realizado

'''
#Obs: Nos testes realizados, o delay de envio das operações é de 2 segundos

#
#Como fechar posições SELL, Binárias (Venda antes do prazo acabar):
#
#OBS: Na opção BINÁRIA, temos um limite de tempo para poder cancelar!!!

'''
ativo = 'EURUSD'
API.start_mood_stream(ativo)
#Lote é o valor que quer aplicar
lotes = 2
#A direção put indica uma operação de venda, call indica compra
direcao = 'put'
timeframe = 1 #Tempo grafico



print('Aplicando Binária')

# A ordem do BINÁRIA é diferente da Digital


status, ID = API.buy(lotes, ativo, direcao, timeframe)

if status:
    print('Operação realizada com sucesso')
else:
    print('Não foi possível enviar a solicitação devido ao encerramento da Candle anterior')

#Definindo um valor para encerrar a operação
print('7 Segundos para o encerramento')
time.sleep(7)
binaria_status_close = API.sell_option(ID) #Comando para vender a operção !
print(binaria_status_close) #Mostra apenas se o comando acima foi realizado
'''

#
# Manipulando Data e Hora em LOOPS Infinitos:
#

#Esse processo é muito importante, vai fazer com que o Robô siga o processo de análise de várias velas e não apenas uma operação

espera_em_segundos = 11
contador_s = 1 #Contador de segundos
contador_m = 1 #Contador de minutos
"""
while True:
    d = datetime.now(tz=timezone('America/Sao_Paulo')) #Pega a Data/Hora atual e tranforma no formato no qual o IQ entende
    # Abaixo extraindo informações do meu datetime acima, para aplicar em alguma regra de operção:
    hora = d.hour
    minutos = d.minute
    segundos = d.second
    milesimos = d.microsecond
    # Trazendo as informações formatadas
    # Obs: Posso usar tanto a opção acima quanto a abaixo, não preciso usar ambas
    '''
    dados_formatados = d.strftime('%H:%M:%S:%f')
    print(dados_formatados)
    '''
    if d.second == 00:
        print('Temos uma nova CANDLE, em M1')
    '''
    if contador_s == espera_em_segundos:
        print('Aguardando 10 segundos')
        contador_s = 0 #é colocado a variavel zerada para ele começar a contar novamente
    '''
    time.sleep(1)
    contador_s +=1
    print(d)
"""
#----------------------------------------------------------------
#Operando a cada 5 velas:

#OBS: vamos utilizar o "contador_m"  que criamos acima:
#OBS2: O Tipo de operação MHI consiste em analisar as 5 ultimas velas, e na sexta operar no sentido que tem menos cor.
while True:
    d = datetime.now(tz=timezone('America/Sao_Paulo'))
    hora = d.hour
    minutos = d.minute
    segundos = d.second
    milesimos = d.microsecond
    if d.second == 58: #Colocando 58 segundos por causa do Delay, se fose segundo exato, dai seria "00".
        contador_m +=1
        print('Temos uma nova CANDLE, em M1')
    if contador_m == 5:
        print('Aplicando estratégia MHI')
        operar = True
        contador_m = 0 #Zerando novamente o contador para começar denovo
    if operar:
        print('Aqui devo colocar minha estratégia')
        operar = False #Colocando False para ele esperar novamente os 5 min
    time.sleep(1)
    print(d)
