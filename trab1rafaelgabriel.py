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

# Funcao para montar a matriz de condutancia e a matriz resultado
def calculoMatrizCondutancia(listaConfig, numeroDeNos):
    # Criando as matrizes com base no numero de nos do circuito
    gm = np.zeros([numeroDeNos,numeroDeNos])
    i = np.zeros(numeroDeNos)

    # For para identificar o componente e montar a matriz com base no seu valor
    for componente in listaConfig:
        if (componente[0][0] == 'I'):
            i[int(componente[1])] = i[int(componente[1])] - int(componente[4])
            i[int(componente[2])] = i[int(componente[2])] + int(componente[4])

        elif (componente [0][0] == 'G'):
            gm[int(componente[1])][int(componente[3])] = gm[int(componente[1])][int(componente[3])] + int(componente[5])
            gm[int(componente[1])][int(componente[4])] = gm[int(componente[1])][int(componente[4])] - int(componente[5])
            gm[int(componente[2])][int(componente[3])] = gm[int(componente[2])][int(componente[3])] - int(componente[5])
            gm[int(componente[2])][int(componente[4])] = gm[int(componente[2])][int(componente[4])] + int(componente[5])
            
        else:
            gm[int(componente[1])][int(componente[1])] = gm[int(componente[1])][int(componente[1])] + 1/int(componente[3])
            gm[int(componente[1])][int(componente[2])] = gm[int(componente[1])][int(componente[2])] - 1/int(componente[3])
            gm[int(componente[2])][int(componente[1])] = gm[int(componente[2])][int(componente[1])] - 1/int(componente[3])
            gm[int(componente[2])][int(componente[2])] = gm[int(componente[2])][int(componente[2])] + 1/int(componente[3])

    gm = gm[1:,1:]
    i = i[1:]
    return gm, i

# Funcao main, que, atraves das outras funcoes, fara a conta para encontrar as tensoes nodais
def main(arqNetlist, tipoSimulacao, nosDesejados, parametrosSimulacao = []):
    if (tipoSimulacao == 'DC'):
        listaConfig = listConfig(arqNetlist)
        numeroDeNos = calculoNos(listaConfig)
        gm, i = calculoMatrizCondutancia(listaConfig, numeroDeNos)

        tensoesNodais = np.linalg.solve(gm, i)
        tensoesNodaisDesejadas = []

        for no in nosDesejados:
            tensoesNodaisDesejadas.append(tensoesNodais[no - 1])
            
    return tensoesNodaisDesejadas

if __name__ == '__main__':
    print(main('netlist1.txt', 'DC', [2]))
    print('')
    print(main('netlist2.txt', 'DC', [2,4]))
    print('')
    print(main('netlist3.txt', 'DC', [1,5,7]))