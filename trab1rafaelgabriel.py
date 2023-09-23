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
            if (caracter != ' '):
                auxList.append(caracter)

            elif (caracter == ' '):
                auxList2.append(''.join(auxList))
                auxList = []

        listaConfig.append(auxList2)
        linhaNetlist = arqNetlist.readline()
    arqNetlist.close()
    #print(listaConfig)

    return listaConfig
