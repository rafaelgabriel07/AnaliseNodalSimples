# Aluno: Rafael Gabriel
# DRE: 121087555

import numpy as np

# A funcao abaixo foi criado com para eu dispor os dados da netlist de uma maneira que acho mais simples de trabalhar
def listConfig(nomeArq):
    arqNetlist = open(nomeArq, 'r')
    linhaNetlist = arqNetlist.readline()
    listaConfig = []

    while (linhaNetlist != ''):
        auxList = []
        auxList2 = []
        
        # Fazendo a organizacao da lista
        # De maneira resumida, o que estou fazendo é separar cada linha da netlist em uma linha da minha matriz de dados
        # E em cada linha, os dados estao despostos de uma maneira mais intuitica
        for caracter in linhaNetlist:
            if (caracter != ' ' and caracter != '\n'):
                auxList.append(caracter)

            else:
                auxList2.append(''.join(auxList))
                auxList = []

        listaConfig.append(auxList2)
        linhaNetlist = arqNetlist.readline()
    arqNetlist.close()
    #print(listaConfig)

    return listaConfig

# Funcao para fazer a conta de quantos nos tem no circuito
def calculoNos(listaConfig):
    maiorNo = 0
    # Nesse for, a funcao ira olhar no por no de cada componente para encontrar o maior no
    # E valido lembrar que a quantidade de nos do circuito sera o maior no + 1 ja que temos o no 0
    for componente in listaConfig:
        if int(componente[1]) > maiorNo:
            maiorNo = int(componente[1])

        if int(componente[2]) > maiorNo:
            maiorNo = int(componente[2])

    numeroDeNos = maiorNo + 1
    return numeroDeNos

# Funcao para ver quais componentes são necessarios criar uma variaves de corrente
def calculoComponentesAnaliseModificada(listaConfig):
    # Essa lista vai nos auxiliar para falar da corrente do componente na matriz
    componentesAnaliseModificada = []

    # Essa variavel vai indicar quantas linhas e colunas terei que adicionar na matriz
    numComponentesAnaliseModificada = 0

    for componente in listaConfig:
        if (componente[0][0] == 'L' or componente[0][0] == 'F' or componente[0][0] == 'E' or componente[0][0] == 'H' or componente[0][0] == 'V'):
            componentesAnaliseModificada.append([componente[0], numComponentesAnaliseModificada])
            numComponentesAnaliseModificada += 1
        
        elif (componente[0][0] == 'K'):
            componentesAnaliseModificada.append([componente[0], numComponentesAnaliseModificada, numComponentesAnaliseModificada + 1])
            numComponentesAnaliseModificada += 2

    return componentesAnaliseModificada, numComponentesAnaliseModificada

# Funcao para montar a matriz de condutancia e a matriz resultado
def calculoMatrizes(listaConfig, numeroDeNos, tipoAnalise, numComponentesAnaliseModificada, componentesAnaliseModificada):

    # Criando as matrizes com base no numero de nos do circuito
    gm = np.zeros([numeroDeNos + numComponentesAnaliseModificada, numeroDeNos + numComponentesAnaliseModificada])
    i = np.zeros(numeroDeNos + numComponentesAnaliseModificada)

    # For para identificar o componente e montar a matriz com base no seu valor
    if (tipoAnalise == 'DC'):
        for componente in listaConfig:

            if (componente[0][0] == 'I'):
                i[int(componente[1])] = i[int(componente[1])] - int(componente[4])
                i[int(componente[2])] = i[int(componente[2])] + int(componente[4])

            elif (componente[0][0] == 'G'):
                gm[int(componente[1])][int(componente[3])] = gm[int(componente[1])][int(componente[3])] + int(componente[5])
                gm[int(componente[1])][int(componente[4])] = gm[int(componente[1])][int(componente[4])] - int(componente[5])
                gm[int(componente[2])][int(componente[3])] = gm[int(componente[2])][int(componente[3])] - int(componente[5])
                gm[int(componente[2])][int(componente[4])] = gm[int(componente[2])][int(componente[4])] + int(componente[5])

            elif (componente[0][0] == 'R'):
                gm[int(componente[1])][int(componente[1])] = gm[int(componente[1])][int(componente[1])] + 1/int(componente[3])
                gm[int(componente[1])][int(componente[2])] = gm[int(componente[1])][int(componente[2])] - 1/int(componente[3])
                gm[int(componente[2])][int(componente[1])] = gm[int(componente[2])][int(componente[1])] - 1/int(componente[3])
                gm[int(componente[2])][int(componente[2])] = gm[int(componente[2])][int(componente[2])] + 1/int(componente[3])

            elif (componente[0][0] == 'V'):
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]
                
                gm[int(componente[1])][numeroDeNos + aux] = gm[int(componente[1])][numeroDeNos + aux] + 1
                gm[int(componente[2])][numeroDeNos + aux] = gm[int(componente[2])][numeroDeNos + aux] - 1
                gm[numeroDeNos + aux][int(componente[1])] = gm[numeroDeNos + aux][int(componente[1])] - 1
                gm[numeroDeNos + aux][int(componente[2])] = gm[numeroDeNos + aux][int(componente[2])] + 1

                i[numeroDeNos + aux] = i[numeroDeNos + aux] - int(componente[4])

    gm = gm[1:,1:]
    i = i[1:]
    return gm, i

# Funcao main, que, atraves das outras funcoes, fara a conta para encontrar as tensoes nodais
def main(arqNetlist, tipoSimulacao, nosDesejados, parametrosSimulacao = []):
    if (tipoSimulacao == 'DC'):
        listaConfig = listConfig(arqNetlist)
        numeroDeNos = calculoNos(listaConfig)
        componentesModificados, numComponentesModificados = calculoComponentesAnaliseModificada(listaConfig)
        gm, i = calculoMatrizes(listaConfig, numeroDeNos, tipoSimulacao, numComponentesModificados, componentesModificados)

        tensoesNodais = np.linalg.solve(gm, i)
        tensoesNodaisDesejadas = []

        for no in nosDesejados:
            tensoesNodaisDesejadas.append(tensoesNodais[no - 1])
            
    return tensoesNodaisDesejadas

if __name__ == '__main__':
    print(main('netlistDC1 - Copia.txt', 'DC', [2]))