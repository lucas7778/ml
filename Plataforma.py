import pandas as pd
from pandas import DataFrame as dataFrame
class Eqp_Proc:

    def __init__(self, nome:str, potNominal:float, fP:float, potProc:float, df:dataFrame, varDep:str, varProc:list,
                 fc:float, fi:float, outpredict:float):
        self.nome = nome
        self.potNominal = potNominal
        self.fP = fP
        self.varDep = varDep
        self.varProc = varProc
        self.potProc = potProc
        # essa abordagem pode gerar um grande consumo de memória
        self.df = df
        self.fc = fc
        self.fi = fi
        self.outpredict = outpredict

        self.modelo_nome = None
        self.modelo = None
        self.estProc = None

        self.novo=True

    
    def calcEstmativa(self,variaveis:list):
        if self.modelo != None:
            self.estProc= self.modelo.getEstimativa(variaveis)
        return self.estProc

    
class Eqp_Rede:
    def __init__(self, nome:str, **parametros):
        self.nome=nome
        self.parametros=parametros

class Plataforma:
    def __init__(self,eqpProc:list, eqpRede=None, subsistemas=None,  circuito=None):
        self.eqpProc=eqpProc
        self.eqpRede=eqpRede
        self.subsistemas=subsistemas
        self.circuito=circuito
