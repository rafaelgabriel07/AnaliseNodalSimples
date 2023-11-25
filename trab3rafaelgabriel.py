# Aluno: Rafael Gabriel
# DRE: 121087555

import numpy as np
from matplotlib import pyplot

# A funcao abaixo foi criado com para eu dispor os dados da netlist de uma maneira que acho mais simples de trabalhar
def listConfig(nomeArq):
    arqNetlist = open(nomeArq, 'r')
    linhasArq = arqNetlist.readlines()
    listaConfig = []
    for linha in linhasArq:
        auxList = []
        auxList2 = []
        
        # Fazendo a organizacao da lista
        # De maneira resumida, o que estou fazendo é separar cada linha da netlist em uma linha da minha matriz de dados
        # E em cada linha, os dados estao despostos de uma maneira mais intuitica
        for caracter in linha:
            if (caracter != ' ' and caracter != '\n'):
                auxList.append(caracter)

            else:
                auxList2.append(''.join(auxList))
                auxList = []

        # Por conta dos arquivos de texto nao terem um \n na ultima linha, eu tenho que adicionar o ultimo caracter do arquivo manualmente com esse if
        if (len(auxList) != 0):
            auxList2.append(''.join(auxList))

        listaConfig.append(auxList2)
    arqNetlist.close()

    
    return listaConfig[4:]

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
def calculoComponentesAnaliseModificada(listaConfig, tipoAnalise):
    # Essa lista vai nos auxiliar para falar da corrente do componente na matriz
    componentesAnaliseModificada = []

    # Essa variavel vai indicar quantas linhas e colunas terei que adicionar na matriz
    numComponentesAnaliseModificada = 0

    # Separei nesse if por que para a analise DC, nos podemos considerar o capacitor como um circuito aberto
    if (tipoAnalise == 'DC'):
        for componente in listaConfig:
            if (componente[0][0] == 'L' or componente[0][0] == 'F' or componente[0][0] == 'E' or componente[0][0] == 'V'):
                componentesAnaliseModificada.append([componente[0], numComponentesAnaliseModificada])
                numComponentesAnaliseModificada += 1

            elif (componente[0][0] == 'H' or componente[0][0] == 'K'):
                componentesAnaliseModificada.append([componente[0], numComponentesAnaliseModificada, numComponentesAnaliseModificada + 1])
                numComponentesAnaliseModificada += 2
    
    else:
        for componente in listaConfig:
            if (componente[0][0] == 'F' or componente[0][0] == 'E' or componente[0][0] == 'V'):
                componentesAnaliseModificada.append([componente[0], numComponentesAnaliseModificada])
                numComponentesAnaliseModificada += 1

            elif (componente[0][0] == 'H'):
                componentesAnaliseModificada.append([componente[0], numComponentesAnaliseModificada, numComponentesAnaliseModificada + 1])
                numComponentesAnaliseModificada += 2

    return componentesAnaliseModificada, numComponentesAnaliseModificada

# Funcao para montar a matriz de condutancia e a matriz resultado
def calculoMatrizes(listaConfig, numeroDeNos, tipoAnalise, numComponentesAnaliseModificada, componentesAnaliseModificada, parametrosAnalise = [], omega = 0, tempoAtual = 0, deltaT = 0):

    # For para identificar o componente e montar a matriz com base no seu valor
    if (tipoAnalise == 'DC'):

        # Criando as matrizes com base no numero de nos do circuito
        fx = np.zeros([numeroDeNos + numComponentesAnaliseModificada, numeroDeNos + numComponentesAnaliseModificada])
        i = np.zeros(numeroDeNos + numComponentesAnaliseModificada)

        # Obs: nao temos a estampa para capacitor aqui pois ele representa, em DC, um circuito aberto, logo nao precisamos adicionar nada
        for componente in listaConfig:

            if (componente[0][0] == 'I'):
                i[int(componente[1])] = i[int(componente[1])] - float(componente[4])
                i[int(componente[2])] = i[int(componente[2])] + float(componente[4])

            elif (componente[0][0] == 'G'):
                fx[int(componente[1])][int(componente[3])] = fx[int(componente[1])][int(componente[3])] + float(componente[5])
                fx[int(componente[1])][int(componente[4])] = fx[int(componente[1])][int(componente[4])] - float(componente[5])
                fx[int(componente[2])][int(componente[3])] = fx[int(componente[2])][int(componente[3])] - float(componente[5])
                fx[int(componente[2])][int(componente[4])] = fx[int(componente[2])][int(componente[4])] + float(componente[5])

            elif (componente[0][0] == 'R'):
                fx[int(componente[1])][int(componente[1])] = fx[int(componente[1])][int(componente[1])] + 1/float(componente[3])
                fx[int(componente[1])][int(componente[2])] = fx[int(componente[1])][int(componente[2])] - 1/float(componente[3])
                fx[int(componente[2])][int(componente[1])] = fx[int(componente[2])][int(componente[1])] - 1/float(componente[3])
                fx[int(componente[2])][int(componente[2])] = fx[int(componente[2])][int(componente[2])] + 1/float(componente[3])

            elif (componente[0][0] == 'L'):
                # Aqui o que fiz foi utilizar a mesma estampa da fonte de tensão, mas com uma fonte de tensão de 0V, representando assim um curto
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]
                
                fx[int(componente[1])][numeroDeNos + aux] = fx[int(componente[1])][numeroDeNos + aux] + 1
                fx[int(componente[2])][numeroDeNos + aux] = fx[int(componente[2])][numeroDeNos + aux] - 1
                fx[numeroDeNos + aux][int(componente[1])] = fx[numeroDeNos + aux][int(componente[1])] - 1
                fx[numeroDeNos + aux][int(componente[2])] = fx[numeroDeNos + aux][int(componente[2])] + 1
                i[numeroDeNos + aux] = i[numeroDeNos + aux] - 0
                
            elif (componente[0][0] == 'K'):
                # Aqui eu fiz a mesma coisa que fiz para o indutor, coloquei duas fontes de tensão de 0V
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]
                        aux2 = componenteAnaliseModificada[2]

                fx[int(componente[1])][numeroDeNos + aux] = fx[int(componente[1])][numeroDeNos + aux] + 1
                fx[int(componente[2])][numeroDeNos + aux] = fx[int(componente[2])][numeroDeNos + aux] - 1
                fx[numeroDeNos + aux][int(componente[1])] = fx[numeroDeNos + aux][int(componente[1])] - 1
                fx[numeroDeNos + aux][int(componente[2])] = fx[numeroDeNos + aux][int(componente[2])] + 1
                i[numeroDeNos + aux] = i[numeroDeNos + aux] - 0

                fx[int(componente[3])][numeroDeNos + aux2] = fx[int(componente[1])][numeroDeNos + aux2] + 1
                fx[int(componente[4])][numeroDeNos + aux2] = fx[int(componente[2])][numeroDeNos + aux2] - 1
                fx[numeroDeNos + aux2][int(componente[3])] = fx[numeroDeNos + aux2][int(componente[3])] - 1
                fx[numeroDeNos + aux2][int(componente[4])] = fx[numeroDeNos + aux2][int(componente[4])] + 1
                i[numeroDeNos + aux2] = i[numeroDeNos + aux2] - 0

            elif (componente[0][0] == 'V'):
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]
                
                fx[int(componente[1])][numeroDeNos + aux] = fx[int(componente[1])][numeroDeNos + aux] + 1
                fx[int(componente[2])][numeroDeNos + aux] = fx[int(componente[2])][numeroDeNos + aux] - 1
                fx[numeroDeNos + aux][int(componente[1])] = fx[numeroDeNos + aux][int(componente[1])] - 1
                fx[numeroDeNos + aux][int(componente[2])] = fx[numeroDeNos + aux][int(componente[2])] + 1

                if (componente[3] != 'AC'):
                    i[numeroDeNos + aux] = i[numeroDeNos + aux] - int(componente[4])

            elif (componente[0][0] == 'E'):
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]

                fx[int(componente[1])][numeroDeNos + aux] = fx[int(componente[1])][numeroDeNos + aux] + 1
                fx[int(componente[2])][numeroDeNos + aux] = fx[int(componente[2])][numeroDeNos + aux] - 1
                fx[numeroDeNos + aux][int(componente[1])] = fx[numeroDeNos + aux][int(componente[1])] - 1
                fx[numeroDeNos + aux][int(componente[2])] = fx[numeroDeNos + aux][int(componente[2])] + 1
                fx[numeroDeNos + aux][int(componente[3])] = fx[numeroDeNos + aux][int(componente[3])] + float(componente[5])
                fx[numeroDeNos + aux][int(componente[4])] = fx[numeroDeNos + aux][int(componente[4])] - float(componente[5])

            elif (componente[0][0] == 'H'):
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]
                        aux2 = componenteAnaliseModificada[2]
                
                fx[int(componente[1])][numeroDeNos + aux2] = fx[int(componente[1])][numeroDeNos + aux2] + 1
                fx[int(componente[2])][numeroDeNos + aux2] = fx[int(componente[2])][numeroDeNos + aux2] - 1
                fx[int(componente[3])][numeroDeNos + aux] = fx[int(componente[3])][numeroDeNos + aux] + 1
                fx[int(componente[4])][numeroDeNos + aux] = fx[int(componente[4])][numeroDeNos + aux] - 1
                fx[numeroDeNos + aux][int(componente[3])] = fx[numeroDeNos + aux][int(componente[3])] - 1
                fx[numeroDeNos + aux][int(componente[4])] = fx[numeroDeNos + aux][int(componente[4])] + 1
                fx[numeroDeNos + aux2][int(componente[1])] = fx[numeroDeNos + aux2][int(componente[1])] - 1
                fx[numeroDeNos + aux2][int(componente[2])] = fx[numeroDeNos + aux2][int(componente[2])] + 1
                fx[numeroDeNos + aux2][numeroDeNos + aux] = fx[numeroDeNos + aux2][numeroDeNos + aux] + float(componente[5])

            elif (componente[0][0] == 'F'):
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]
                
                fx[int(componente[1])][numeroDeNos + aux] = fx[int(componente[1])][numeroDeNos + aux] + int(componente[5])
                fx[int(componente[2])][numeroDeNos + aux] = fx[int(componente[2])][numeroDeNos + aux] - int(componente[5])
                fx[int(componente[3])][numeroDeNos + aux] = fx[int(componente[3])][numeroDeNos + aux] + 1
                fx[int(componente[4])][numeroDeNos + aux] = fx[int(componente[4])][numeroDeNos + aux] - 1
                fx[numeroDeNos + aux][int(componente[3])] = fx[numeroDeNos + aux][int(componente[3])] - 1
                fx[numeroDeNos + aux][int(componente[4])] = fx[numeroDeNos + aux][int(componente[4])] + 1

            elif (componente[0][0] == 'D'):
                e10 = parametrosAnalise[int(componente[1])]
                e20 = parametrosAnalise[int(componente[2])]
                g0 = (float(componente[3])*np.e**((e10 - e20)/float(componente[4])))/float(componente[4])
                i0 = float(componente[3])*(np.e**((e10 - e20)/float(componente[4])) - 1) - g0*(e10 - e20)
                fx[int(componente[1])][int(componente[1])] = fx[int(componente[1])][int(componente[1])] + g0
                fx[int(componente[1])][int(componente[2])] = fx[int(componente[1])][int(componente[2])] - g0
                fx[int(componente[2])][int(componente[1])] = fx[int(componente[2])][int(componente[1])] - g0
                fx[int(componente[2])][int(componente[2])] = fx[int(componente[2])][int(componente[2])] + g0

                i[int(componente[1])] = i[int(componente[1])] - i0
                i[int(componente[2])] = i[int(componente[2])] + i0


    else:

        # Criando as matrizes com base no numero de nos do circuito
        fx = np.zeros(([numeroDeNos + numComponentesAnaliseModificada, numeroDeNos + numComponentesAnaliseModificada]), dtype = 'complex_')
        i = np.zeros((numeroDeNos + numComponentesAnaliseModificada), dtype = 'complex_')

        for componente in listaConfig:

            if (componente[0][0] == 'R'):
                fx[int(componente[1])][int(componente[1])] = fx[int(componente[1])][int(componente[1])] + 1/float(componente[3])
                fx[int(componente[1])][int(componente[2])] = fx[int(componente[1])][int(componente[2])] - 1/float(componente[3])
                fx[int(componente[2])][int(componente[1])] = fx[int(componente[2])][int(componente[1])] - 1/float(componente[3])
                fx[int(componente[2])][int(componente[2])] = fx[int(componente[2])][int(componente[2])] + 1/float(componente[3])

            elif (componente[0][0] == 'G'):
                fx[int(componente[1])][int(componente[3])] = fx[int(componente[1])][int(componente[3])] + float(componente[5])
                fx[int(componente[1])][int(componente[4])] = fx[int(componente[1])][int(componente[4])] - float(componente[5])
                fx[int(componente[2])][int(componente[3])] = fx[int(componente[2])][int(componente[3])] - float(componente[5])
                fx[int(componente[2])][int(componente[4])] = fx[int(componente[2])][int(componente[4])] + float(componente[5])

            elif (componente[0][0] == 'L'):
                fx[int(componente[1])][int(componente[1])] = fx[int(componente[1])][int(componente[1])] + 1/(1j*omega*float(componente[3]))
                fx[int(componente[1])][int(componente[2])] = fx[int(componente[1])][int(componente[2])] - 1/(1j*omega*float(componente[3]))
                fx[int(componente[2])][int(componente[1])] = fx[int(componente[2])][int(componente[1])] - 1/(1j*omega*float(componente[3]))
                fx[int(componente[2])][int(componente[2])] = fx[int(componente[2])][int(componente[2])] + 1/(1j*omega*float(componente[3]))

            elif (componente[0][0] == 'C'):
                fx[int(componente[1])][int(componente[1])] = fx[int(componente[1])][int(componente[1])] + (1j*omega*float(componente[3]))
                fx[int(componente[1])][int(componente[2])] = fx[int(componente[1])][int(componente[2])] - (1j*omega*float(componente[3]))
                fx[int(componente[2])][int(componente[1])] = fx[int(componente[2])][int(componente[1])] - (1j*omega*float(componente[3]))
                fx[int(componente[2])][int(componente[2])] = fx[int(componente[2])][int(componente[2])] + (1j*omega*float(componente[3]))

            elif (componente[0][0] == 'K'):

                gama11 = float(componente[6])/(float(componente[5])*float(componente[6])-(float(componente[7]))**2)
                gama22 = float(componente[5])/(float(componente[5])*float(componente[6])-(float(componente[7]))**2)
                gama12_21 = -float(componente[7])/(float(componente[5])*float(componente[6])-(float(componente[7]))**2)

                fx[int(componente[1])][int(componente[1])] = fx[int(componente[1])][int(componente[1])] + gama11/(1j*omega)
                fx[int(componente[1])][int(componente[2])] = fx[int(componente[1])][int(componente[2])] - gama11/(1j*omega)
                fx[int(componente[1])][int(componente[3])] = fx[int(componente[1])][int(componente[3])] + gama12_21/(1j*omega)
                fx[int(componente[1])][int(componente[4])] = fx[int(componente[1])][int(componente[4])] - gama12_21/(1j*omega)
                fx[int(componente[2])][int(componente[1])] = fx[int(componente[2])][int(componente[1])] - gama11/(1j*omega)
                fx[int(componente[2])][int(componente[2])] = fx[int(componente[2])][int(componente[2])] + gama11/(1j*omega)
                fx[int(componente[2])][int(componente[3])] = fx[int(componente[2])][int(componente[3])] - gama12_21/(1j*omega)
                fx[int(componente[2])][int(componente[4])] = fx[int(componente[2])][int(componente[4])] + gama12_21/(1j*omega)
                fx[int(componente[3])][int(componente[1])] = fx[int(componente[3])][int(componente[1])] + gama12_21/(1j*omega)
                fx[int(componente[3])][int(componente[2])] = fx[int(componente[3])][int(componente[2])] - gama12_21/(1j*omega)
                fx[int(componente[3])][int(componente[3])] = fx[int(componente[3])][int(componente[3])] + gama22/(1j*omega)
                fx[int(componente[3])][int(componente[4])] = fx[int(componente[3])][int(componente[4])] - gama22/(1j*omega)
                fx[int(componente[4])][int(componente[1])] = fx[int(componente[4])][int(componente[1])] - gama12_21/(1j*omega)
                fx[int(componente[4])][int(componente[2])] = fx[int(componente[4])][int(componente[2])] + gama12_21/(1j*omega)
                fx[int(componente[4])][int(componente[3])] = fx[int(componente[4])][int(componente[3])] - gama22/(1j*omega)
                fx[int(componente[4])][int(componente[4])] = fx[int(componente[4])][int(componente[4])] + gama22/(1j*omega)

            elif (componente[0][0] == 'F'):
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]
                
                fx[int(componente[1])][numeroDeNos + aux] = fx[int(componente[1])][numeroDeNos + aux] + int(componente[5])
                fx[int(componente[2])][numeroDeNos + aux] = fx[int(componente[2])][numeroDeNos + aux] - int(componente[5])
                fx[int(componente[3])][numeroDeNos + aux] = fx[int(componente[3])][numeroDeNos + aux] + 1
                fx[int(componente[4])][numeroDeNos + aux] = fx[int(componente[4])][numeroDeNos + aux] - 1
                fx[numeroDeNos + aux][int(componente[3])] = fx[numeroDeNos + aux][int(componente[3])] - 1
                fx[numeroDeNos + aux][int(componente[4])] = fx[numeroDeNos + aux][int(componente[4])] + 1

            elif (componente[0][0] == 'E'):
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]

                fx[int(componente[1])][numeroDeNos + aux] = fx[int(componente[1])][numeroDeNos + aux] + 1
                fx[int(componente[2])][numeroDeNos + aux] = fx[int(componente[2])][numeroDeNos + aux] - 1
                fx[numeroDeNos + aux][int(componente[1])] = fx[numeroDeNos + aux][int(componente[1])] - 1
                fx[numeroDeNos + aux][int(componente[2])] = fx[numeroDeNos + aux][int(componente[2])] + 1
                fx[numeroDeNos + aux][int(componente[3])] = fx[numeroDeNos + aux][int(componente[3])] + float(componente[5])
                fx[numeroDeNos + aux][int(componente[4])] = fx[numeroDeNos + aux][int(componente[4])] - float(componente[5])

            elif (componente[0][0] == 'H'):
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]
                        aux2 = componenteAnaliseModificada[2]
                
                fx[int(componente[1])][numeroDeNos + aux2] = fx[int(componente[1])][numeroDeNos + aux2] + 1
                fx[int(componente[2])][numeroDeNos + aux2] = fx[int(componente[2])][numeroDeNos + aux2] - 1
                fx[int(componente[3])][numeroDeNos + aux] = fx[int(componente[3])][numeroDeNos + aux] + 1
                fx[int(componente[4])][numeroDeNos + aux] = fx[int(componente[4])][numeroDeNos + aux] - 1
                fx[numeroDeNos + aux][int(componente[3])] = fx[numeroDeNos + aux][int(componente[3])] - 1
                fx[numeroDeNos + aux][int(componente[4])] = fx[numeroDeNos + aux][int(componente[4])] + 1
                fx[numeroDeNos + aux2][int(componente[1])] = fx[numeroDeNos + aux2][int(componente[1])] - 1
                fx[numeroDeNos + aux2][int(componente[2])] = fx[numeroDeNos + aux2][int(componente[2])] + 1
                fx[numeroDeNos + aux2][numeroDeNos + aux] = fx[numeroDeNos + aux2][numeroDeNos + aux] + float(componente[5])

            elif (componente[0][0] == 'I' and componente[3] == 'AC'):
                amp = float(componente[4])
                fase = float(componente[5])

                i[int(componente[1])] = i[int(componente[1])] - amp*np.exp(1j*fase)
                i[int(componente[2])] = i[int(componente[2])] + amp*np.exp(1j*fase)

            elif (componente[0][0] == 'V'):
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]
                
                fx[int(componente[1])][numeroDeNos + aux] = fx[int(componente[1])][numeroDeNos + aux] + 1
                fx[int(componente[2])][numeroDeNos + aux] = fx[int(componente[2])][numeroDeNos + aux] - 1
                fx[numeroDeNos + aux][int(componente[1])] = fx[numeroDeNos + aux][int(componente[1])] - 1
                fx[numeroDeNos + aux][int(componente[2])] = fx[numeroDeNos + aux][int(componente[2])] + 1

                if (componente[3] == 'AC'):
                    amp = float(componente[4])
                    fase = float(componente[5])

                    i[numeroDeNos + aux] = i[numeroDeNos + aux] - amp*np.exp(1j*fase)

    fx = fx[1:,1:]
    i = i[1:]

    return fx, i

# Funcao main, que, atraves das outras funcoes, fara a conta para encontrar as tensoes nodais
def main(arqNetlist, tipoSimulacao, nosDesejados, parametrosSimulacao):
    
    listaConfig = listConfig(arqNetlist)
    numeroDeNos = calculoNos(listaConfig)
    componentesModificados, numComponentesModificados = calculoComponentesAnaliseModificada(listaConfig, tipoSimulacao)
    
    if (tipoSimulacao == 'DC'):

        tol = float(parametrosSimulacao[0])
        aux = 0
        numComponentesNaoLineares = 0

        # Fazendo a contagem de componentes nao lineares
        for componente in listaConfig:
            if (componente[0][0] == 'D'):
                numComponentesNaoLineares += 1

        listaNosComponentesNaoLineares = np.zeros(2*numComponentesNaoLineares)
        indice = 0
        for componente in listaConfig:
            if (componente[0][0] == 'D'):
                listaNosComponentesNaoLineares[indice] = int(componente[1])
                listaNosComponentesNaoLineares[indice + 1] = int(componente[2])
                indice += 2

        while aux < 1000:
            menorTol = True
            fx, i = calculoMatrizes(listaConfig, numeroDeNos, tipoSimulacao, numComponentesModificados, componentesModificados, parametrosSimulacao[1])
            tensoesNodais = np.linalg.solve(fx, i)
    
            # Verificando as tolerancias
            for no in listaNosComponentesNaoLineares:
                no = int(no)
                if (parametrosSimulacao[1][no] != 0 and np.abs(tensoesNodais[no - 1] - parametrosSimulacao[1][no]) > tol):
                    menorTol = False
                    break

            if (menorTol):
                break

            # Alterando os parâmetros
            for no in listaNosComponentesNaoLineares:
                no = int(no)
                if (parametrosSimulacao[1][no] != 0):
                    parametrosSimulacao[1][no] = tensoesNodais[no - 1]

            aux += 1

        print(aux)
        tensoesNodaisDesejadas = []
        for no in nosDesejados:
            tensoesNodaisDesejadas.append(tensoesNodais[no - 1])
        return tensoesNodaisDesejadas

    elif (tipoSimulacao == 'AC'):
        freqs = np.logspace(np.log10(parametrosSimulacao[0]), np.log10(parametrosSimulacao[1]), parametrosSimulacao[2])
        omegas = 2*np.pi*freqs
        modulos = np.zeros([len(freqs), numeroDeNos - 1])
        fases = np.zeros([len(freqs), numeroDeNos - 1])

        for indice in range(len(freqs)):
            fx, i = calculoMatrizes(listaConfig, numeroDeNos, tipoSimulacao, numComponentesModificados, componentesModificados, [], omegas[indice])
            tensoesNodais = np.linalg.solve(fx, i)

            # Tirando as correntes que encontramos devida a analise modificada
            tensoesNodais = tensoesNodais[:numeroDeNos - 1]

            for i in range(len(tensoesNodais)):
                modulos[indice][i] = 20*np.log10(np.abs(tensoesNodais[i]))
                fases[indice][i] = np.degrees(np.angle(tensoesNodais[i]))

        # To fazendo a transposta para ficar no formato Tensao x Frequencia
        modulos = modulos.transpose()
        fases = fases.transpose()

        auxModulo = []
        auxFase = []
        modulosDesejados = []
        fasesDesejadas = []
        for noDesejado in nosDesejados:
            for indice in range(len(freqs)):
                auxModulo.append(modulos[noDesejado - 1][indice])
                auxFase.append(fases[noDesejado - 1][indice])
            modulosDesejados.append(auxModulo)
            fasesDesejadas.append(auxFase)
            auxModulo = []
            auxFase = []
            
        # Plotagem do gráfico
        for indice in range(len(modulosDesejados)):
            pyplot.plot(freqs,modulosDesejados[indice])
            pyplot.xscale("log")
        pyplot.title(arqNetlist[0].upper() + arqNetlist[1:7] + ' ' + arqNetlist[7:len(arqNetlist) - 4])
        pyplot.ylabel('Magnetude [dB]')
        pyplot.xlabel('Freq [Hz]')
        pyplot.show()

        for indice in range(len(fasesDesejadas)):
            pyplot.plot(freqs,fasesDesejadas[indice])
            pyplot.xscale("log")
        pyplot.title(arqNetlist[0].upper() + arqNetlist[1:7] + ' ' + arqNetlist[7:len(arqNetlist) - 4])
        pyplot.ylabel('Fase [Graus]')
        pyplot.xlabel('Freq [Hz]')
        pyplot.show()

        return freqs, modulosDesejados, fasesDesejadas
    
    else:
        tempoTotal = parametrosSimulacao[0]
        deltaT = parametrosSimulacao[1]
        tol = parametrosSimulacao[2]

        tempo = np.linspace(0, tempoTotal, deltaT)
        tensoes = np.zeros([len(tempo), numeroDeNos - 1])

        for indice in range(len(tempo)):
            tempoAtual = tempo[indice]
            fx, i = calculoMatrizes(listaConfig, numeroDeNos, tipoSimulacao, numComponentesModificados, componentesModificados, parametrosSimulacao[3], 0, tempoAtual, deltaT)

            tensoesNodais = np.linalg.solve(fx, i)

            # Tirando as correntes que encontramos devida a analise modificada
            tensoesNodais = tensoesNodais[:numeroDeNos - 1]

            for no in range(len(tensoesNodais)):
                tensoes[indice][no] = tensoesNodais[no]

        # Colocando a matriz de tensões no formato correto
        tensoes = np.transpose(tensoes)

        # Pegando apenas as tensoes desejadas
        tensoesNodaisDesejadas = []
        for noDesejado in nosDesejados:
            auxTensoes = []
            for indice in range(len(tempo)):
                auxTensoes.append(tensoes[noDesejado - 1][indice])
            tensoesNodaisDesejadas.append(auxTensoes)

        # Plotagem do gráfico
        for indice in range(len(tensoesNodaisDesejadas)):
            pyplot.plot(tempo, tensoesNodaisDesejadas[indice])
        # pyplot.title(arqNetlist[0].upper() + arqNetlist[1:7] + ' ' + arqNetlist[7:len(arqNetlist) - 4])
        pyplot.ylabel('Tensão [V]')
        pyplot.xlabel('Tempo [s]')
        pyplot.show()

        

if __name__ == '__main__':
    print('Testes')
    print(main('teste7.txt', 'DC', [1,2,3], [1e-14, [0,-5,4,5]]))