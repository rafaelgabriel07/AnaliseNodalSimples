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
def calculoMatrizes(listaConfig, numeroDeNos, tipoAnalise, numComponentesAnaliseModificada, componentesAnaliseModificada, omega = 0):

    # For para identificar o componente e montar a matriz com base no seu valor
    if (tipoAnalise == 'DC'):

        # Criando as matrizes com base no numero de nos do circuito
        gm = np.zeros([numeroDeNos + numComponentesAnaliseModificada, numeroDeNos + numComponentesAnaliseModificada])
        i = np.zeros(numeroDeNos + numComponentesAnaliseModificada)

        # Obs: nao temos a estampa para capacitor aqui pois ele representa, em DC, um circuito aberto, logo nao precisamos adicionar nada
        for componente in listaConfig:

            if (componente[0][0] == 'I'):
                i[int(componente[1])] = i[int(componente[1])] - float(componente[4])
                i[int(componente[2])] = i[int(componente[2])] + float(componente[4])

            elif (componente[0][0] == 'G'):
                gm[int(componente[1])][int(componente[3])] = gm[int(componente[1])][int(componente[3])] + float(componente[5])
                gm[int(componente[1])][int(componente[4])] = gm[int(componente[1])][int(componente[4])] - float(componente[5])
                gm[int(componente[2])][int(componente[3])] = gm[int(componente[2])][int(componente[3])] - float(componente[5])
                gm[int(componente[2])][int(componente[4])] = gm[int(componente[2])][int(componente[4])] + float(componente[5])

            elif (componente[0][0] == 'R'):
                gm[int(componente[1])][int(componente[1])] = gm[int(componente[1])][int(componente[1])] + 1/float(componente[3])
                gm[int(componente[1])][int(componente[2])] = gm[int(componente[1])][int(componente[2])] - 1/float(componente[3])
                gm[int(componente[2])][int(componente[1])] = gm[int(componente[2])][int(componente[1])] - 1/float(componente[3])
                gm[int(componente[2])][int(componente[2])] = gm[int(componente[2])][int(componente[2])] + 1/float(componente[3])

            elif (componente[0][0] == 'L'):
                # Aqui o que fiz foi utilizar a mesma estampa da fonte de tensão, mas com uma fonte de tensão de 0V, representando assim um curto
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]
                
                gm[int(componente[1])][numeroDeNos + aux] = gm[int(componente[1])][numeroDeNos + aux] + 1
                gm[int(componente[2])][numeroDeNos + aux] = gm[int(componente[2])][numeroDeNos + aux] - 1
                gm[numeroDeNos + aux][int(componente[1])] = gm[numeroDeNos + aux][int(componente[1])] - 1
                gm[numeroDeNos + aux][int(componente[2])] = gm[numeroDeNos + aux][int(componente[2])] + 1
                i[numeroDeNos + aux] = i[numeroDeNos + aux] - 0
                
            elif (componente[0][0] == 'K'):
                # Aqui eu fiz a mesma coisa que fiz para o indutor, coloquei duas fontes de tensão de 0V
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]
                        aux2 = componenteAnaliseModificada[2]

                gm[int(componente[1])][numeroDeNos + aux] = gm[int(componente[1])][numeroDeNos + aux] + 1
                gm[int(componente[2])][numeroDeNos + aux] = gm[int(componente[2])][numeroDeNos + aux] - 1
                gm[numeroDeNos + aux][int(componente[1])] = gm[numeroDeNos + aux][int(componente[1])] - 1
                gm[numeroDeNos + aux][int(componente[2])] = gm[numeroDeNos + aux][int(componente[2])] + 1
                i[numeroDeNos + aux] = i[numeroDeNos + aux] - 0

                gm[int(componente[3])][numeroDeNos + aux2] = gm[int(componente[1])][numeroDeNos + aux2] + 1
                gm[int(componente[4])][numeroDeNos + aux2] = gm[int(componente[2])][numeroDeNos + aux2] - 1
                gm[numeroDeNos + aux2][int(componente[3])] = gm[numeroDeNos + aux2][int(componente[3])] - 1
                gm[numeroDeNos + aux2][int(componente[4])] = gm[numeroDeNos + aux2][int(componente[4])] + 1
                i[numeroDeNos + aux2] = i[numeroDeNos + aux2] - 0

            elif (componente[0][0] == 'V'):
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]
                
                gm[int(componente[1])][numeroDeNos + aux] = gm[int(componente[1])][numeroDeNos + aux] + 1
                gm[int(componente[2])][numeroDeNos + aux] = gm[int(componente[2])][numeroDeNos + aux] - 1
                gm[numeroDeNos + aux][int(componente[1])] = gm[numeroDeNos + aux][int(componente[1])] - 1
                gm[numeroDeNos + aux][int(componente[2])] = gm[numeroDeNos + aux][int(componente[2])] + 1

                if (componente[3] != 'AC'):
                    i[numeroDeNos + aux] = i[numeroDeNos + aux] - int(componente[4])

            elif (componente[0][0] == 'E'):
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]

                gm[int(componente[1])][numeroDeNos + aux] = gm[int(componente[1])][numeroDeNos + aux] + 1
                gm[int(componente[2])][numeroDeNos + aux] = gm[int(componente[2])][numeroDeNos + aux] - 1
                gm[numeroDeNos + aux][int(componente[1])] = gm[numeroDeNos + aux][int(componente[1])] - 1
                gm[numeroDeNos + aux][int(componente[2])] = gm[numeroDeNos + aux][int(componente[2])] + 1
                gm[numeroDeNos + aux][int(componente[3])] = gm[numeroDeNos + aux][int(componente[3])] + float(componente[5])
                gm[numeroDeNos + aux][int(componente[4])] = gm[numeroDeNos + aux][int(componente[4])] - float(componente[5])

            elif (componente[0][0] == 'H'):
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]
                        aux2 = componenteAnaliseModificada[2]
                
                gm[int(componente[1])][numeroDeNos + aux2] = gm[int(componente[1])][numeroDeNos + aux2] + 1
                gm[int(componente[2])][numeroDeNos + aux2] = gm[int(componente[2])][numeroDeNos + aux2] - 1
                gm[int(componente[3])][numeroDeNos + aux] = gm[int(componente[3])][numeroDeNos + aux] + 1
                gm[int(componente[4])][numeroDeNos + aux] = gm[int(componente[4])][numeroDeNos + aux] - 1
                gm[numeroDeNos + aux][int(componente[3])] = gm[numeroDeNos + aux][int(componente[3])] - 1
                gm[numeroDeNos + aux][int(componente[4])] = gm[numeroDeNos + aux][int(componente[4])] + 1
                gm[numeroDeNos + aux2][int(componente[1])] = gm[numeroDeNos + aux2][int(componente[1])] - 1
                gm[numeroDeNos + aux2][int(componente[2])] = gm[numeroDeNos + aux2][int(componente[2])] + 1
                gm[numeroDeNos + aux2][numeroDeNos + aux] = gm[numeroDeNos + aux2][numeroDeNos + aux] + float(componente[5])

            elif (componente[0][0] == 'F'):
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]
                
                gm[int(componente[1])][numeroDeNos + aux] = gm[int(componente[1])][numeroDeNos + aux] + int(componente[5])
                gm[int(componente[2])][numeroDeNos + aux] = gm[int(componente[2])][numeroDeNos + aux] - int(componente[5])
                gm[int(componente[3])][numeroDeNos + aux] = gm[int(componente[3])][numeroDeNos + aux] + 1
                gm[int(componente[4])][numeroDeNos + aux] = gm[int(componente[4])][numeroDeNos + aux] - 1
                gm[numeroDeNos + aux][int(componente[3])] = gm[numeroDeNos + aux][int(componente[3])] - 1
                gm[numeroDeNos + aux][int(componente[4])] = gm[numeroDeNos + aux][int(componente[4])] + 1

    else:

        # Criando as matrizes com base no numero de nos do circuito
        gm = np.zeros(([numeroDeNos + numComponentesAnaliseModificada, numeroDeNos + numComponentesAnaliseModificada]), dtype = 'complex_')
        i = np.zeros((numeroDeNos + numComponentesAnaliseModificada), dtype = 'complex_')

        for componente in listaConfig:

            if (componente[0][0] == 'R'):
                gm[int(componente[1])][int(componente[1])] = gm[int(componente[1])][int(componente[1])] + 1/float(componente[3])
                gm[int(componente[1])][int(componente[2])] = gm[int(componente[1])][int(componente[2])] - 1/float(componente[3])
                gm[int(componente[2])][int(componente[1])] = gm[int(componente[2])][int(componente[1])] - 1/float(componente[3])
                gm[int(componente[2])][int(componente[2])] = gm[int(componente[2])][int(componente[2])] + 1/float(componente[3])

            elif (componente[0][0] == 'G'):
                gm[int(componente[1])][int(componente[3])] = gm[int(componente[1])][int(componente[3])] + float(componente[5])
                gm[int(componente[1])][int(componente[4])] = gm[int(componente[1])][int(componente[4])] - float(componente[5])
                gm[int(componente[2])][int(componente[3])] = gm[int(componente[2])][int(componente[3])] - float(componente[5])
                gm[int(componente[2])][int(componente[4])] = gm[int(componente[2])][int(componente[4])] + float(componente[5])

            elif (componente[0][0] == 'L'):
                gm[int(componente[1])][int(componente[1])] = gm[int(componente[1])][int(componente[1])] + 1/(1j*omega*float(componente[3]))
                gm[int(componente[1])][int(componente[2])] = gm[int(componente[1])][int(componente[2])] - 1/(1j*omega*float(componente[3]))
                gm[int(componente[2])][int(componente[1])] = gm[int(componente[2])][int(componente[1])] - 1/(1j*omega*float(componente[3]))
                gm[int(componente[2])][int(componente[2])] = gm[int(componente[2])][int(componente[2])] + 1/(1j*omega*float(componente[3]))

            elif (componente[0][0] == 'C'):
                gm[int(componente[1])][int(componente[1])] = gm[int(componente[1])][int(componente[1])] + (1j*omega*float(componente[3]))
                gm[int(componente[1])][int(componente[2])] = gm[int(componente[1])][int(componente[2])] - (1j*omega*float(componente[3]))
                gm[int(componente[2])][int(componente[1])] = gm[int(componente[2])][int(componente[1])] - (1j*omega*float(componente[3]))
                gm[int(componente[2])][int(componente[2])] = gm[int(componente[2])][int(componente[2])] + (1j*omega*float(componente[3]))

            elif (componente[0][0] == 'K'):

                gama11 = float(componente[6])/(float(componente[5])*float(componente[6])-(float(componente[7]))**2)
                gama22 = float(componente[5])/(float(componente[5])*float(componente[6])-(float(componente[7]))**2)
                gama12_21 = -float(componente[7])/(float(componente[5])*float(componente[6])-(float(componente[7]))**2)

                gm[int(componente[1])][int(componente[1])] = gm[int(componente[1])][int(componente[1])] + gama11/(1j*omega)
                gm[int(componente[1])][int(componente[2])] = gm[int(componente[1])][int(componente[2])] - gama11/(1j*omega)
                gm[int(componente[1])][int(componente[3])] = gm[int(componente[1])][int(componente[3])] + gama12_21/(1j*omega)
                gm[int(componente[1])][int(componente[4])] = gm[int(componente[1])][int(componente[4])] - gama12_21/(1j*omega)
                gm[int(componente[2])][int(componente[1])] = gm[int(componente[2])][int(componente[1])] - gama11/(1j*omega)
                gm[int(componente[2])][int(componente[2])] = gm[int(componente[2])][int(componente[2])] + gama11/(1j*omega)
                gm[int(componente[2])][int(componente[3])] = gm[int(componente[2])][int(componente[3])] - gama12_21/(1j*omega)
                gm[int(componente[2])][int(componente[4])] = gm[int(componente[2])][int(componente[4])] + gama12_21/(1j*omega)
                gm[int(componente[3])][int(componente[1])] = gm[int(componente[3])][int(componente[1])] + gama12_21/(1j*omega)
                gm[int(componente[3])][int(componente[2])] = gm[int(componente[3])][int(componente[2])] - gama12_21/(1j*omega)
                gm[int(componente[3])][int(componente[3])] = gm[int(componente[3])][int(componente[3])] + gama22/(1j*omega)
                gm[int(componente[3])][int(componente[4])] = gm[int(componente[3])][int(componente[4])] - gama22/(1j*omega)
                gm[int(componente[4])][int(componente[1])] = gm[int(componente[4])][int(componente[1])] - gama12_21/(1j*omega)
                gm[int(componente[4])][int(componente[2])] = gm[int(componente[4])][int(componente[2])] + gama12_21/(1j*omega)
                gm[int(componente[4])][int(componente[3])] = gm[int(componente[4])][int(componente[3])] - gama22/(1j*omega)
                gm[int(componente[4])][int(componente[4])] = gm[int(componente[4])][int(componente[4])] + gama22/(1j*omega)

            elif (componente[0][0] == 'F'):
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]
                
                gm[int(componente[1])][numeroDeNos + aux] = gm[int(componente[1])][numeroDeNos + aux] + int(componente[5])
                gm[int(componente[2])][numeroDeNos + aux] = gm[int(componente[2])][numeroDeNos + aux] - int(componente[5])
                gm[int(componente[3])][numeroDeNos + aux] = gm[int(componente[3])][numeroDeNos + aux] + 1
                gm[int(componente[4])][numeroDeNos + aux] = gm[int(componente[4])][numeroDeNos + aux] - 1
                gm[numeroDeNos + aux][int(componente[3])] = gm[numeroDeNos + aux][int(componente[3])] - 1
                gm[numeroDeNos + aux][int(componente[4])] = gm[numeroDeNos + aux][int(componente[4])] + 1

            elif (componente[0][0] == 'E'):
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]

                gm[int(componente[1])][numeroDeNos + aux] = gm[int(componente[1])][numeroDeNos + aux] + 1
                gm[int(componente[2])][numeroDeNos + aux] = gm[int(componente[2])][numeroDeNos + aux] - 1
                gm[numeroDeNos + aux][int(componente[1])] = gm[numeroDeNos + aux][int(componente[1])] - 1
                gm[numeroDeNos + aux][int(componente[2])] = gm[numeroDeNos + aux][int(componente[2])] + 1
                gm[numeroDeNos + aux][int(componente[3])] = gm[numeroDeNos + aux][int(componente[3])] + float(componente[5])
                gm[numeroDeNos + aux][int(componente[4])] = gm[numeroDeNos + aux][int(componente[4])] - float(componente[5])

            elif (componente[0][0] == 'H'):
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]
                        aux2 = componenteAnaliseModificada[2]
                
                gm[int(componente[1])][numeroDeNos + aux2] = gm[int(componente[1])][numeroDeNos + aux2] + 1
                gm[int(componente[2])][numeroDeNos + aux2] = gm[int(componente[2])][numeroDeNos + aux2] - 1
                gm[int(componente[3])][numeroDeNos + aux] = gm[int(componente[3])][numeroDeNos + aux] + 1
                gm[int(componente[4])][numeroDeNos + aux] = gm[int(componente[4])][numeroDeNos + aux] - 1
                gm[numeroDeNos + aux][int(componente[3])] = gm[numeroDeNos + aux][int(componente[3])] - 1
                gm[numeroDeNos + aux][int(componente[4])] = gm[numeroDeNos + aux][int(componente[4])] + 1
                gm[numeroDeNos + aux2][int(componente[1])] = gm[numeroDeNos + aux2][int(componente[1])] - 1
                gm[numeroDeNos + aux2][int(componente[2])] = gm[numeroDeNos + aux2][int(componente[2])] + 1
                gm[numeroDeNos + aux2][numeroDeNos + aux] = gm[numeroDeNos + aux2][numeroDeNos + aux] + float(componente[5])

            elif (componente[0][0] == 'I' and componente[3] == 'AC'):
                amp = float(componente[4])
                fase = float(componente[5])

                i[int(componente[1])] = i[int(componente[1])] - amp*np.exp(1j*fase)
                i[int(componente[2])] = i[int(componente[2])] + amp*np.exp(1j*fase)

            elif (componente[0][0] == 'V'):
                for componenteAnaliseModificada in componentesAnaliseModificada:
                    if (componente[0] == componenteAnaliseModificada[0]):
                        aux = componenteAnaliseModificada[1]
                
                gm[int(componente[1])][numeroDeNos + aux] = gm[int(componente[1])][numeroDeNos + aux] + 1
                gm[int(componente[2])][numeroDeNos + aux] = gm[int(componente[2])][numeroDeNos + aux] - 1
                gm[numeroDeNos + aux][int(componente[1])] = gm[numeroDeNos + aux][int(componente[1])] - 1
                gm[numeroDeNos + aux][int(componente[2])] = gm[numeroDeNos + aux][int(componente[2])] + 1

                if (componente[3] == 'AC'):
                    amp = float(componente[4])
                    fase = float(componente[5])

                    i[numeroDeNos + aux] = i[numeroDeNos + aux] - amp*np.exp(1j*fase)

    gm = gm[1:,1:]
    i = i[1:]

    return gm, i

# Funcao main, que, atraves das outras funcoes, fara a conta para encontrar as tensoes nodais
def main(arqNetlist, tipoSimulacao, nosDesejados, parametrosSimulacao = []):
    
    listaConfig = listConfig(arqNetlist)
    numeroDeNos = calculoNos(listaConfig)
    componentesModificados, numComponentesModificados = calculoComponentesAnaliseModificada(listaConfig, tipoSimulacao)
    
    if (tipoSimulacao == 'DC'):
        gm, i = calculoMatrizes(listaConfig, numeroDeNos, tipoSimulacao, numComponentesModificados, componentesModificados)

        tensoesNodais = np.linalg.solve(gm, i)
        tensoesNodaisDesejadas = []

        for no in nosDesejados:
            tensoesNodaisDesejadas.append(tensoesNodais[no - 1])

        return tensoesNodaisDesejadas

    else:
        freqs = np.logspace(np.log10(parametrosSimulacao[0]), np.log10(parametrosSimulacao[1]), parametrosSimulacao[2])
        omegas = 2*np.pi*freqs
        modulos = np.zeros([len(freqs), numeroDeNos - 1])
        fases = np.zeros([len(freqs), numeroDeNos - 1])

        for indice in range(len(freqs)):
            gm, i = gm, i = calculoMatrizes(listaConfig, numeroDeNos, tipoSimulacao, numComponentesModificados, componentesModificados, omegas[indice])
            tensoesNodais = np.linalg.solve(gm, i)

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

if __name__ == '__main__':
    print(listConfig('teste1.txt'))