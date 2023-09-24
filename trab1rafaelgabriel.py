import numpy as np

# A funcao abaixo foi criado com para eu dispor os dados da netlist de uma maneira que acho mais simples de trabalhar
def listConfig(nomeArq):
    arqNetlist = open(nomeArq + '.txt', 'r')
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
    for componente in listaConfig:
        if int(componente[1]) > maiorNo:
            maiorNo = int(componente[1])

        if int(componente[2]) > maiorNo:
            maiorNo = int(componente[2])

    return maiorNo

def calculoMatrizCondutancia(listaConfig, maiorNo):
    gm = np.zeros([maiorNo + 1,maiorNo + 1])
    i = np.zeros(maiorNo + 1)

    for componente in listaConfig:
        if (componente[0][0] == 'I'):
            i[int(componente[1])] = i[int(componente[1])] - int(componente[4])
            i[int(componente[2])] = i[int(componente[2])] + int(componente[4])

    return gm, i

gm, i = calculoMatrizCondutancia(listConfig('netlist1'), calculoNos(listConfig('netlist1')))
print(gm)
print(i)