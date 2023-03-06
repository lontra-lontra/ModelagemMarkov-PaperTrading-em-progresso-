import yfinance as yf 
import numpy as np
import matplotlib.pyplot as plt

def nome(dados):
    return "[" + str(dados[0]) + "," + str(dados[1]) + ")"
def dados_da_uniao(dadosA,dadosB):
    return min(dadosA[0],dadosB[0]),max(dadosA[1],dadosB[1])

class M_estado:
    def __init__(self, criterio_inicial,numero,nome,dados):
        self.criterios = []
        self.criterios.append(criterio_inicial)
        self.dados = dados
        self.numero = numero
        self.nome = lambda: nome(dados = self.dados)
    def agrega(self,agregado,novosdados):
        self.criterios.extend(agregado.criterios)
        self.dados = novosdados(self.dados,agregado.dados)

    def criterio(self,situacao):
        for criterio in self.criterios:
            if criterio(situacao) == True:
                return True
        return False 

def achaEstado(situacao,estados):
    for estado in estados:
        if estado.criterio(situacao):
            return estado
    print("nao há estado correspondente!")
    return 0


def matrizDeTransicao(estados):
    m = np.zeros((max(estados)+1,max(estados)+1))
    estados_seguintes = [estados[i+1] for i in range(len(estados)-1)]
    for estado,estado_seguinte in zip(estados,estados_seguintes):
        m[estado][estado_seguinte] += 1
    return m
    
acao = yf.Ticker("aapl")
historico_de_valores = acao.history(period = "7d",interval="1m")["Close"]
deltas = [historico_de_valores[i+1]-historico_de_valores[i] for i in range(len(historico_de_valores)-1)]
sequenciaDeSituacoes = deltas

raio = max(max(sequenciaDeSituacoes),-min(sequenciaDeSituacoes))
n_de_estados = int(round(2*raio/(0.05)))
estados = []


for i in range(n_de_estados):
    def criterio(situacao,i=i):
        return (( i*0.05 - raio <= situacao ) and (situacao < (i+1)*0.05 - raio ))
    estados.append(M_estado(criterio,i,nome,((i*0.05 - raio), (i+1)*0.05 - raio )) )


sequencia_de_estados = [achaEstado(situacao,estados) for situacao in sequenciaDeSituacoes]
print([estados.index(estado) for estado in sequencia_de_estados])

m = matrizDeTransicao([estados.index(estado) for estado in sequencia_de_estados])

while np.prod([linha.sum() for linha in m]) == 0:
    for linha,indiceLinha in zip(m,range(m.shape[0]-1)):
        if linha.sum() < 5:
            if (indiceLinha > 0):
                estados[indiceLinha].agrega(estados[indiceLinha-1],dados_da_uniao)  
                estados.remove(estados[indiceLinha-1])
            else: 
                estados[indiceLinha].agrega(estados[indiceLinha+1],dados_da_uniao)
                estados.remove(estados[indiceLinha+1])
            break
    sequencia_de_estados = [achaEstado(situacao,estados) for situacao in sequenciaDeSituacoes]
    m = matrizDeTransicao([estados.index(estado) for estado in sequencia_de_estados])
print(m)
for estado in estados:
    print(estado.nome())
casos_por_coluna = m.sum(axis=1)
markov = np.round(m / casos_por_coluna[:, np.newaxis],3)
print(markov)
print(np.round(np.linalg.matrix_power(markov, 5)
,3))
print(np.round(np.linalg.matrix_power(markov, 1000)
,3))

plt.matshow(markov)
plt.matshow(np.round(np.linalg.matrix_power(markov, 2)
,3))
plt.matshow(np.round(np.linalg.matrix_power(markov, 3)
,3))
plt.matshow(np.round(np.linalg.matrix_power(markov, 4)
,3))

plt.show()
        

