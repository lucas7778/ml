# tem uma estranha dependência do openpyxl
#import MyWidgets
from PyQt5 import QtWidgets
import io
import os
import sys
import threading
import concurrent.futures
import openpyxl     # previne usar a biblioteca errada para abrir o arquivo .xlsx

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QApplication, QInputDialog, QLabel, QTreeWidgetItem,\
    QScrollArea
from PyQt5 import QtGui
from PyQt5.uic import loadUi
import pandas as pd
import numpy as np
import dashboard3 as db
import eq
from subsistema import *
import pickle
from Plataforma import *
from fcfi import *

from filterSelection import *

from fcfiForm import *

from machine_learning import bml_model
from machine_learning.bml_dtmn import bdm_DtMn
from machine_learning import bml_mman

pd.set_option('display.max_columns', None)


class Demo(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        loadUi("fpso_interface2.ui", self)
        self.setWindowState(Qt.WindowMaximized)
        self.setWindowTitle("FPDA")

        # a princípio a linha abaixo será excluída
        self.threads = []

        #inicialização do dataframe da app principal
        self.df = None

        # objeto responsável por fazer a comunicação entre o dashboard e a app principal
        # este objeto recebe as coordenadas de um "box_select" do gráfico de dispersão para análise de fator de carga
        # quando isso é feito ele emite um sinal que dispara "self.newDF", que altera o dataframe para cálculo de FC e
        # FI em batelada
        self.objTransf=filterSelect1()
        self.objTransf.itemChanged.connect(self.newDF)

        # Menu-> Arquivo-> Abrir
        self.actionAbrir.triggered.connect(self.open_data)
        # Associação ao ícone
        self.actionAbrir.setIcon(QtGui.QIcon("imgs/db_icon.png"))
        self.actionML.setIcon(QtGui.QIcon("imgs/ml_icon.png"))

        # replace_combobox relacionada ao botão "Substituir valores"(replace_button) +++++ 4a linha
        self.operations = ['Valor Médio', 'Valor Posterior', 'Valor Anterior']
        self.replace_combobox.addItems(self.operations)
        # botão "Substituir valores" associado ao replace_combobox
        self.replace_button.clicked.connect(self.replace_values2)


        # remove_button relacionado ao botão 1 "Eliminar colunas"(remove_button) +++++ 2a linha
        self.remove_button.clicked.connect(self.remove_update_combobox)

        self.manter_button.clicked.connect(self.keep_update_combobox)

        # relacionado ao remove_combobox
        self.reset2.clicked.connect(self.Reset2)

        # limiar_button relacionado ao botão 2 "Eliminar colunas"(limiar_button) (limiar_spin) +++++ 3a linha
        self.limiar_button.clicked.connect(self.remove_update_filter)

        # relacionado ao sub_combobox, sub_lineEdit1 e sub_lineEdit2 ++++++ 1a linha
        self.sub_button.clicked.connect(self.replace_line2)

        # relacionado ao sub_combobox
        self.reset1.clicked.connect(self.Reset1)


        # Botão "Base original" +++++ 5a linha
        self.reset_button.clicked.connect(self.clear_infobase)

        # Botão "Exibir análise" +++++ 6a linha
        self.run_dash_button.clicked.connect(self.run_dash2)

        # Botão "Visualizar dataframe" +++++ 5a linha
        self.df_show_button.clicked.connect(self.excel_show)
        self.tags_button.clicked.connect(self.tags_show)
        # inicialização da porta do dash, quando acionado pela app principal
        self.port = 8050
        # objeto que controla as portas do dashboard acionado na tela de equipamento
        self.portEqp = db.Porta()

        ############ subsistema : Essa parte do código será substituída ###################
        self.sbWindow = Subsistema_Window()
        self.sb_button.clicked.connect(self.subsistema_show)
        self.sbWindow.subvalidate_button.clicked.connect(self.addSubsistema)

        #Inicialização da variável que receberá as unidades referentes as tags do sistema. Será utilizada no dashboard
        # para que as unidades aparecçam nos eixos dos gráficos
        self.dfTag = None

        # criação de um novo equipamento
        self.actionML.triggered.connect(self.getdataframe)
        # edição de um equipamento existente, a partir de um duploclick em um item da árvore
        self.eq_treewidget.doubleClicked.connect(self.open_eq2)

        # inicialização de do dicionário que armazena os equipamentos de processo (Plataforma.py -> classe: Eqp_Proc
        self.saved_eqs = {}

        # a princípio, duas janelas para fazer a mesma coisa
        # inicialização da janela com formulário para criação de equipamentos
        self.eq_wd = None
        # inicialização da janela com formulário para edição de equipamentos
        self.eqpForm = None

        # método que recupera o dicionário de equipamentos de um arquivo local (eqs.pickle) e que tem um argumento
        # default treeLoad=True, que faz a árvore de equipamentos ser atualizada
        self.load_eq()

        # Cálculo do FC e FI em batelada
        self.actionFC_e_FI.triggered.connect(self.run_fcfi2)
        #self.fcfi_wd = None
        #inicialização da janela de configuração para cálculo de FC e FI em batelada
        self.fcfiForm = None

    # Evento: Menu-> Arquivo-> Abrir ou ícone
    def open_data(self):
        filter = "Planilhas (*.xls *.xlsx *.csv)"
        self.path = QFileDialog.getOpenFileName(self, 'Base de dados', '', filter)[0]
        self.filetype = os.path.splitext(os.path.basename(self.path))[1]

        # limpa os combobox das 1a e 2a linhas
        self.sub_combobox.clear()
        self.remove_combobox.clear()
        # ??????????????
        self.sub_combobox.setCurrentIndex(0)
        self.remove_combobox.setCurrentIndex(0)

        # zera o valor do limiar_spin na 3a linha
        self.limiar_spin.setValue(0)

        if self.filetype in ['.xls', '.xlsx', '.csv']:
            if self.filetype in ['.xls', '.xlsx']:
                # dataframe_original
                self.df = pd.read_excel(self.path, engine='openpyxl')

            else:
                # dataframe_original
                self.df = pd.read_csv(self.path)

            self.df = self.df.replace('Bad', np.nan)
            self.df.iloc[:, 1:] = self.df.iloc[:, 1:].apply(pd.to_numeric)
            #self.df.fillna(0)

            # dataframe_trabalho
            self.df2 = self.df.copy(deep=True)
            self.dfFCFI = self.df.copy(deep=True)

            # relacionada à tela de subsistema que será refatorada
            self.clear_sb()

            # populando o combobox da 1a linha com as colunas do dataframe_trabalho
            self.fill_combobox(self.sub_combobox, self.df2, 'Todas')

            # inserindo a opção "Todas" na primeira posição
            #self.sub_combobox.insertItem(0, 'Todas')
            # primeira posição apresentada
            self.sub_combobox.setCurrentIndex(0)

            # populando o combobox da 2a linha com as colunas do dataframe_trabalho
            self.fill_combobox(self.remove_combobox, self.df2)

            # atualiza a label com o número de colunas do df de trabalho (self.df2)
            self.counter_cols()
            # atualiza a label com o path do arquivo gerador do df de trabalho
            self.name_base_label.setText(self.path)
            # preenche a área de texto da app com as estatísticas e info do df de trabalho
            self.estatic_show()

            # relacionado a tela de subsistema que será refatorada
            self.remove_from_loaded_obj()

        else:
            self.name_base_label.setText('Nenhuma')
            self.est_label.setText("Estatísticas da base de dados.")
            self.corr_label.setText("Correlação da base de dados.")
            self.col_label.setText('')
            self.df = None
            self.clear_sb()
            self.sbWindow.subcol_combobox.clear()

    # cols é um objeto combobox e dfs um dataframe
    def fill_combobox(self, cols, dfs, text=None):
        cols.clear()
        col = list(dfs.columns.values)
        col.remove('index')
        if text != None:
            col = [text]+col
        cols.addItems(col)

    # conta o numero de colunas do dataframe_trabalho ?????????
    def counter_cols(self):
        self.col_label.setText(str(len(self.df2.columns)-1))

    # apresentação das estatísticas
    def estatic_show(self):
        self.est_label.setText('Estatísticas da base de dados.')
        self.corr_label.setText('Correlação da base de dados.')
        try:
            # a princípio isso é uma variável local e não um atributo da classe principal
            # não precisa do self
            self.df3 = self.df2.copy()
            self.df3 = self.df3.drop('index', axis=1)
            corr = self.df3.corr()
            desc = self.df3.describe(include=[np.number])

            # as estatísticas estão sendo apresentadas como labels e não como uma Text Edit .... avaliar
            self.est_label.setText(str(desc))
            self.corr_label.setText(str(corr))
        # parece tratar o caso de dataframes não numéricos: usa o info() ao invés do describe()
        except Exception as e:
            if type(e).__name__ == "ValueError":
                self.df3 = self.df2.copy()
                self.df3 = self.df3.drop('index', axis=1)
                buffer = io.StringIO()

                desc = self.df3.info(buf=buffer)
                s = buffer.getvalue()
                self.est_label.setText(s)

    # Evento do botão 1 "Eliminar colunas"(remove_button) +++++ 2a linha
    def remove_update_combobox(self):
        if len(self.remove_combobox.currentData()) == 0:
            QMessageBox.warning(self, "Alerta", "Nenhuma coluna foi selecionada ...")
            return
        try:
            col_selected = self.remove_combobox.currentData()
            # elimina a coluna( por enquanto apenas uma) do dataframe_trabalho
            self.df2 = self.df2.drop(col_selected, axis=1)
            self.dfFCFI = self.df.copy(deep=True)

            self.remove_from_loaded_obj()

            # atualiza os comboboxes das 1a e 2a linhas
            self.fill_combobox(self.remove_combobox, self.df2)
            self.fill_combobox(self.sub_combobox, self.df2, 'Todas')

            #self.sub_combobox.insertItem(0, 'Todas')
            self.sub_combobox.setCurrentIndex(0)

            # atualiza o label (label_2) com o número de colunas
            self.counter_cols()
            # atualiza as estatísticas com o novo dataframe_trabalho
            self.estatic_show()

        except Exception as e:
            if type(e).__name__ == "AttributeError":
                pass

    # Evento do botão  "Manter"(manter_button) +++++ 2a linha
    def keep_update_combobox(self):
        if len(self.remove_combobox.currentData()) == 0:
            QMessageBox.warning(self, "Alerta", "Nenhuma coluna foi selecionada ...")
            return
        try:
            col_selected = self.remove_combobox.currentData()
            col_selected = ['index']+col_selected
            # elimina a coluna( por enquanto apenas uma) do dataframe_trabalho
            self.df2 = self.df2[col_selected]
            self.dfFCFI = self.df.copy(deep=True)
            # atualiza os comboboxes das 1a e 2a linhas

            self.remove_from_loaded_obj()

            self.fill_combobox(self.remove_combobox, self.df2)
            self.fill_combobox(self.sub_combobox, self.df2, 'Todas')

            # self.sub_combobox.insertItem(0, 'Todas')
            self.sub_combobox.setCurrentIndex(0)

            # atualiza o label (label_2) com o número de colunas
            self.counter_cols()
            # atualiza as estatísticas com o novo dataframe_trabalho
            self.estatic_show()
        except Exception as e:
            if type(e).__name__ == "AttributeError":
                pass

    # Evento do botão 2 "Eliminar colunas"(limiar_button) (limiar_spin) +++++ 3a linha
    def remove_update_filter(self):
        try:
            if self.df is None:
                QMessageBox.warning(self, "Alerta", "Nenhum arquivo carregado ...")
            else:
                pfilter = self.limiar_spin.value() / 100

                for col in list(self.df2.columns.values):
                    if self.df2[col].isna().sum() / len(self.df2.index) > pfilter:
                        self.df2 = self.df2.drop(col, axis=1)
                        self.dfFCFI = self.df.copy(deep=True)

                self.remove_from_loaded_obj()

                self.fill_combobox(self.remove_combobox, self.df2)
                self.fill_combobox(self.sub_combobox, self.df2,'Todas')
                #self.sub_combobox.insertItem(0, 'Todas')
                self.sub_combobox.setCurrentIndex(0)
                self.counter_cols()
                self.estatic_show()

        except Exception as e:
            if type(e).__name__ == "ValueError":
                self.est_label.setText("Estatísticas da base de dados.")
                self.corr_label.setText("Correlação da base de dados.")

    # Evento do botão "Substituir valores" associado ao replace_combobox ++++ 4a linha
    def replace_values2(self):
        try:

            if self.replace_combobox.currentText() == self.operations[0]:
                for col in list(self.df2.columns.values):
                    if col != 'index':
                        # substituindo 0 pela média. Era para substituir valores faltantes
                        self.df2[col] = self.df2[col].fillna(self.df2[col].mean())
                        self.dfFCFI = self.df.copy(deep=True)

            elif self.replace_combobox.currentText() == self.operations[1]:
                for col in list(self.df2.columns.values):
                    if col != 'index':
                        # substitui o 0 por NaN (faltante) e depois substitui NaN pelo anterior
                        self.df2[col] = self.df2[col].fillna(method='bfill')
                        self.dfFCFI = self.df.copy(deep=True)

            elif self.replace_combobox.currentText() == self.operations[2]:
                for col in list(self.df2.columns.values):
                    if col != 'index':
                        self.df2[col] = self.df2[col].fillna(method='ffill')
                        self.dfFCFI = self.df.copy(deep=True)

            self.estatic_show()
        except Exception as e:
            if type(e).__name__ == "AttributeError":
                QMessageBox.warning(self, "Alerta", "Nenhum arquivo carregado ...")

    # Evento do botão "Base original" +++++ 5a linha
    def clear_infobase(self):
        try:
            if self.df is None:
                QMessageBox.warning(self, "Alerta", "Nenhum arquivo carregado ...")
            else:
                self.df2 = self.df.copy(deep=True)
                self.dfFCFI = self.df.copy(deep=True)
                self.clear_sb()

                self.fill_combobox(self.sub_combobox, self.df2, 'Todas')
                #self.sub_combobox.insertItem(0, 'Todas')
                self.sub_combobox.setCurrentIndex(0)
                self.fill_combobox(self.remove_combobox, self.df2)
                self.counter_cols()
                self.estatic_show()
                self.remove_from_loaded_obj()
        except Exception as e:
            if type(e).__name__ == "AttributeError":
                # print('No dateframe loaded.')
                pass

    # Evento do botão "Exibir análise" +++++ 6a linha
    def run_dash2(self):
        if self.df is None:
            QMessageBox.warning(
                self, "Alerta",
                "É preciso abrir um arquivo de dados antes de exibir a análise")
        else:
            t = db.DashThread(self.df2, self.objTransf, dataTags=self.dfTag,  port=self.port)
            self.port += 1
            t.start()

    # Evento do botão "Visualizar dataframe" +++++ 5a linha
    def show_excel(self):
        try:
            # desenecessária a cópia do dataframe de trabalho
            self.df4 = self.df2.copy()
            self.df4.to_excel('dataframe_de_trabalho.xlsx', index=False)

            os.system('start excel.exe dataframe_de_trabalho.xlsx')
        except Exception as e:
            if type(e).__name__ == "AttributeError":
                pass

    # Thread para chamar a função acima
    def excel_show(self):
        try:
            if self.df is None:
                QMessageBox.warning(self, "Alerta", "Nenhum arquivo carregado ...")
            else:
                threading.Thread(target=self.show_excel).start()
        except Exception as e:
            pass

    # Evento do botão "Substituir por"
    def replace_line2(self):

        if len(self.sub_combobox.currentData()) == 0:
            QMessageBox.warning(self, "Alerta", "Nenhuma coluna foi selecionada ...")
            return

        value1 = self.sub_lineEdit1.text()
        value2 = self.sub_lineEdit2.text()

        if self.isanumber(self.sub_lineEdit1.text()) == True:
            value1 = float(self.sub_lineEdit1.text())

        if self.isanumber(self.sub_lineEdit2.text()) == True:
            value2 = float(self.sub_lineEdit2.text())

        # permite que os valores faltantes (designados por null) sejam substituídos por qualquer valor
        if value1 == 'null':
            value1 = np.nan

        try:
            if 'Todas' in self.sub_combobox.currentData():
                self.df2.iloc[:, 1:] = self.df2.iloc[:, 1:].replace(value1, value2)
            else:
                col = self.sub_combobox.currentData()
                self.df2[col] = self.df2[col].replace(value1, value2)
            self.dfFCFI = self.df.copy(deep=True)
            self.estatic_show()

        except Exception as e:
            print(e)
            if type(e).__name__ == "AttributeError":
                print('No dateframe loaded.')
                pass

    # método suporte para a função acima
    def isanumber(self, value):
        try:
            float(value)
        except ValueError:
            return False
        else:
            return True

    # Evento do botão Reset da seção "Substituir valores"
    def Reset1(self):
        if self.df is None:
            QMessageBox.warning(self, "Alerta", "Nenhuma coluna disponível ...")
        else:
            self.sub_combobox.unCheckAll()

    # Evento do botão Reset da seção "Manipular colunas"
    def Reset2(self):
        if self.df is None:
            QMessageBox.warning(self, "Alerta", "Nenhuma coluna disponível ...")
        else:
            self.remove_combobox.unCheckAll()

    # def closeEvent(self, event):
    #     """Generate 'question' dialog on clicking 'X' button in title bar.
    #
    #     Reimplement the closeEvent() event handler to include a 'Question'
    #     dialog with options on how to proceed - Save, Close, Cancel buttons
    #     """
    #     reply = QMessageBox.question(
    #         self, "Message",
    #         "Você quer realmente fechar a aplicação?",
    #         QMessageBox.Close | QMessageBox.Cancel,
    #         QMessageBox.Close)
    #
    #     if reply == QMessageBox.Close:
    #         #for t in self.threads:
    #             #t.kill()
    #         event.accept()
    #     else:
    #         event.ignore()

    # Evento do botão "Carregar unidades" que antes era "Visualizar tags"
    # Não há mais visualização de tags, apenas atualização do dfTags com
    # as unidades de engenharia. Mudar o nome do método é uma boa alternativa
    def tags_excel(self):
        filter = "Planilhas (*.xls *.xlsx *.csv)"
        #dfTag = None
        path = QFileDialog.getOpenFileName(self, 'Base de dados', '', filter)[0]
        filetype = os.path.splitext(os.path.basename(path))[1]
        if filetype in ['.xls', '.xlsx', '.csv']:
            if filetype in ['.xls', '.xlsx']:
                # dataframe_original
                self.dfTag = pd.read_excel(path, engine='openpyxl')

            else:
                # dataframe_original
                self.dfTag = pd.read_csv(path)
        if self.dfTag is None:
            print('dftag eh none no main')
        else:
            print('dftag nao e none no main')

        # tag_desc = zip(dfTag[dfTag[0].isin(self.df2.columns)][0], dfTag[dfTag[0].isin(self.df2.columns)][1])
        # D_tag_desc = dict(tag_desc)
        # frameTag = pd.DataFrame(D_tag_desc, index=[0])
        # frameTag = frameTag.T
        # try:
        #     frameTag.to_excel('Tags_de_trabalho.xlsx', index=True)
        #     os.system('start excel.exe Tags_de_trabalho.xlsx')
        # except Exception as e:
        #     if type(e).__name__ == "AttributeError":
        #         pass

    # Thread para lançar o método acima
    def tags_show(self):
        try:
            if self.df is None:
                QMessageBox.warning(self, "Alerta", "Nenhum arquivo carregado ...")
            else:
                threading.Thread(target=self.tags_excel).start()
        except Exception as e:
            pass

    # relacionado à tela de subsistema que será refatorada
    def subsistema_show(self):
        try:
            self.fill_combobox(self.sbWindow.subcol_combobox, self.df2)
            self.fill_combobox(self.sbWindow.subcol_combobox_2, self.df2)
        except Exception as e:
            pass
        self.sbWindow.displayInfo()

    # relacionado à tela de subsistema que será refatorada
    def addSubsistema(self):
        try:
            if self.sbWindow.global_v is True:
                df1 = self.df2[self.sbWindow.temp[1]]
                df2 = self.df2[self.sbWindow.temp[2]]
                dftrab = df1.sum(axis=1).subtract(df2.sum(axis=1))
                self.df2[self.sbWindow.temp[0]] = dftrab
                self.dfFCFI = self.df.copy(deep=True)

                self.fill_combobox(self.remove_combobox, self.df2)
                self.fill_combobox(self.sub_combobox, self.df2, 'Todas')

                self.sub_combobox.setCurrentIndex(0)

                # atualiza o label (label_2) com o número de colunas
                self.counter_cols()
                # atualiza as estatísticas com o novo dataframe_trabalho
                self.estatic_show()

        except Exception as e:
            pass

    # relacionado à tela de subsistema que será refatorada
    def clear_sb(self):
        self.sbWindow.loaded_obj.clear()
        self.sbWindow.subnewsystem_editline.clear()
        self.sbWindow.sb_listWidget.clear()
        self.sbWindow.sb_listWidget2.clear()

    # relacionado à tela de subsistema que será refatorada
    def remove_from_loaded_obj(self):
        try:
            templist = []
            for i in range(len(self.sbWindow.loaded_obj)):
                if self.sbWindow.loaded_obj[i][0] not in list(self.df2.columns):
                    templist.append(self.sbWindow.loaded_obj[i])
            if len(templist) != 0:
                for sub in templist:
                    self.sbWindow.loaded_obj.remove(sub)

                self.sbWindow.sb_listWidget2.clear()

                self.sbWindow.fill_listwidget()

        except Exception as e:
            pass


    # Esse método é chamado pelo "getDataframe" para abrir uma janela de seleção de arquivo, caso nenhuma base tenha
    # sido carregada. o getDataframe está relacionado ao evento de criação de um novo equipamento. A sugestão é associar
    # o new_eq a esse evento, com o trecho de código que está comentado
    def new_eq(self):
        try:
            self.eq_wd = eq.EQ_wd(self.portEqp, tree=self.eq_treewidget,eqps= self.saved_eqs, dfTags=self.dfTag)
            self.eq_wd.open_data_ml()
            if self.eq_wd.df_ml is None:
                self.eq_wd.close()
                return
            #self.eq_wd.save_eq_pushbutton.clicked.connect(self.save_eq)
            self.eq_wd.show()
        except Exception as e:
            print(e)

        # try:
        #     if self.df is None:
        #         self.open_data()
        #         return
        #
        #     # chamar um formulário de equipamento para preenchimento
        #     self.eqpForm = eq.EQ_wd(self.portEqp, tree=self.eq_treewidget, eqps=self.saved_eqs, dfTags=self.dfTag)
        #     self.eqpForm.setDataframe(self.df2)
        #     self.eqpForm.show()
        # except Exception as e:
        #     print(e)

    # método para gravar o dicionário de equipamentos em um arquivo de sistema
    def dump_eq(self):
        try:
            with open('eqs.pickle', 'wb') as fp:
                pickle.dump(self.saved_eqs, fp)
        except Exception as e:
            print(e)

    # método para carregar o dicionário de equipamentos, a partir de um arquivo do sistema
    # por default também atualiza a árvore de equipamentos
    def load_eq(self,treeLoad=True):
        try:
            with open('eqs.pickle', 'rb') as fp:
                self.saved_eqs = pickle.load(fp)
            if treeLoad:
                for i in self.saved_eqs.keys():
                    mainItem = QTreeWidgetItem([i])
                    self.eq_treewidget.addTopLevelItem(mainItem)

        except Exception as e:
            print(e)


    # def save_eq(self):
    #     print(-1)
    #     if True:  # self.eq_wd.model_saved is True:
    #         print(0)
    #         self.eq_wd.defcurent_model()
    #         print(1)
    #         obj_to_save = Eqp_Proc(self.eq_wd.name_eq.text(), self.eq_wd.pot_nom.value(), self.eq_wd.fat_pot.value(),
    #                                self.eq_wd.pot_proc.value(), self.eq_wd.df2_ml, self.eq_wd.var_dep.currentText(),
    #                                self.eq_wd.feed_ml(), float(self.eq_wd.fc_Label.text()),float(self.eq_wd.fi_Label.text()), float(self.eq_wd.output_predict.text()))
    #         print(2)
    #         obj_to_save.modelo = self.eq_wd.current_model
    #         print(3)
    #         obj_to_save.modelo_nome = self.eq_wd.sel_models_combobox.currentText()
    #         print(4)
    #         self.saved_eqs[self.eq_wd.name_eq.text()] = obj_to_save
    #
    #
    #         print(5)
    #         if not (self.eq_wd.name_eq.text() in self.saved_eqs):
    #             print(6)
    #             mainItem = QTreeWidgetItem([self.eq_wd.name_eq.text()])
    #             self.eq_treewidget.addTopLevelItem(mainItem)
    #         self.dump_eq()
    #         print(7)
    #     self.eq_wd.close()

    # Evento de duplo click em um item da árvore de equipamentos
    def open_eq2(self, Qtindex):
        try:
            if self.df is None:
                self.open_data()
                return

            # referência do item selecionado na árvore
            item = self.eq_treewidget.itemFromIndex(Qtindex)
            print(item.text(0))

            # resgatar obj do dicionário de persistência
            objEqp = self.saved_eqs[item.text(0)]

            # chamar um formulário de equipamento para preenchimento
            self.eqpForm = eq.EQ_wd(self.portEqp, tree=self.eq_treewidget, eqps=self.saved_eqs, dfTags=self.dfTag)
            self.eqpForm.setDataframe(self.df2)

            # preencher os campos do formulário com os dados do objEqp

            ############################ Seção Configuração ##############################
            self.eqpForm.name_eq.setText(objEqp.nome)
            self.eqpForm.pot_nom.setValue(objEqp.potNominal)
            self.eqpForm.pot_proc.setValue(objEqp.potProc)
            print('load_obj_eq 2')
            self.eqpForm.fat_pot.setValue(objEqp.fP)

            #self.eqpForm.df2_ml = objEqp.df
            #self.eqpForm.setDataframe(self.df2)
            # populando o combobox da 1a linha com as colunas do dataframe_trabalho
            self.eqpForm.fill_combobox(self.eqpForm.var_pro, objEqp.df, 'Todas')

            # primeira posição apresentada
            self.eqpForm.var_pro.setCurrentIndex(0)

            # populando o combobox da 2a linha com as colunas do dataframe_trabalho
            self.eqpForm.fill_combobox(self.eqpForm.var_dep, objEqp.df)

            # marcando as variáveis que foram usadas para descrever o equipamento e, com elas, populando
            # a seção Estimativa

            indexDep = self.eqpForm.var_dep.findText(objEqp.varDep)
            self.eqpForm.var_dep.setCurrentIndex(indexDep)
            #QtItem = self.eqpForm.var_dep.model().item(indexDep)
            #QtItem.setCheckState(Qt.Checked)


            for var in objEqp.varProc:
                index = self.eqpForm.var_pro.findText(var[0])
                QtItem = self.eqpForm.var_pro.model().item(index)
                QtItem.setCheckState(Qt.Checked)
                label = QLabel(var[0])
                label.setObjectName('label: ' + var[0])
                spin = QDoubleSpinBox()
                spin.setMaximum(9000000000.00)
                spin.setObjectName('num: ' + var[0])
                spin.setValue(var[1])

                self.eqpForm.textLayout.addWidget(label)
                self.eqpForm.numLayout.addWidget(spin)

            ############################ Seção Machine Learning ##############################

            # a lista de modelos de ML é carregada na chamada do construtor do formulário (eqpForm) em models_combobox

            # resgatando o modelo do objEqp
            self.eqpForm.current_model = objEqp.modelo


            # marcando o modelo gravado em models_combobox
            indexMod = self.eqpForm.models_combobox.findText(objEqp.modelo_nome)
            QtItem = self.eqpForm.models_combobox.model().item(indexMod)
            QtItem.setCheckState(Qt.Checked)

            # populando a tab Modelos com ao informação do modelo e respectivas estatísticas
            text = QLabel(
                f"{self.eqpForm.current_model.bbb_info()}\n\n Estatísticas:\n{self.eqpForm.current_model.bbb_stats()}")
            scroll = QScrollArea()
            scroll.setWidget(text)
            print('load_obj_eq 5')
            self.eqpForm.stats_tab.clear()
            print('load_obj_eq 6')
            self.eqpForm.stats_tab.addTab(scroll, objEqp.modelo_nome)
            print('load_obj_eq 7')
            self.eqpForm.sel_models_combobox.addItem(objEqp.modelo_nome)
            print('load_obj_eq 8')
            self.eqpForm.output_predict.setText(str(objEqp.outpredict))
            print('load_obj_eq 9')
            ############################ Seção FC e FI ##############################

            self.eqpForm.fc_Label.setText(str(objEqp.fc))
            print('load_obj_eq 10')
            self.eqpForm.fi_Label.setText(str(objEqp.fi))
            print('load_obj_eq 11')
            self.eqpForm.show()
            print('load_obj_eq 12')
        except Exception as e:
            print(e)



    # def load_obj_eq(self, obj):
    #     print(self.saved_eqs.keys())
    #     item = eq.EQ_wd(self.portEqp, tree=self.eq_treewidget, eqps=self.saved_eqs, dfTags=self.dfTag)
    #     print('load_obj_eq 1')
    #     try:
    #         item.name_eq.setText(obj.nome)
    #         item.pot_nom.setValue(obj.potNominal)
    #         item.pot_proc.setValue(obj.potProc)
    #         print('load_obj_eq 2')
    #         item.fat_pot.setValue(obj.fP)
    #         item.df2_ml = obj.df
    #         print('load_obj_eq 3')
    #         item.fill_combobox(item.var_dep, item.df2_ml)
    #         item.var_dep.setCurrentIndex(item.var_dep.findText(obj.varDep, Qt.MatchFixedString))
    #         print('load_obj_eq 4')
    #         #item.current_model = obj.modelo
    #
    #         #text = QLabel(
    #             #f"{item.current_model.bbb_info()}\n\n Estatísticas:\n{item.current_model.bbb_stats()}")
    #         #scroll = QScrollArea()
    #         #scroll.setWidget(text)
    #         print('load_obj_eq 5')
    #         item.stats_tab.clear()
    #         #item.stats_tab.addTab(scroll, obj.modelo_nome)
    #
    #         item.sel_models_combobox.addItem(obj.modelo_nome)
    #         item.fill_combobox(item.var_pro, item.df2_ml, 'Todas')
    #
    #         # item.current_model = obj.modelo
    #
    #         # text = QLabel(
    #         # f"{item.current_model.bbb_info()}\n\n Estatísticas:\n{item.current_model.bbb_stats()}")
    #         # scroll = QScrollArea()
    #         # scroll.setWidget(text)
    #
    #         item.fc_Label.setText(str(obj.fc))
    #         item.fi_Label.setText(str(obj.fi))
    #         item.output_predict.setText(str(obj.outpredict))
    #         print('load_obj_eq 6')
    #
    #         index = item.models_combobox.findText(obj.modelo_nome)
    #         QtItem = item.models_combobox.model().item(index)
    #         QtItem.setCheckState(Qt.Checked)
    #         print('load_obj_eq 7')
    #         item.rec_var_pro(obj)
    #         print('load_obj_eq 8')
    #
    #     except Exception as e:
    #         print(e)
    #
    #     return item

    # def open_eq(self, Qtindex):
    #     try:
    #         # referência do item selecionado na árvore
    #         item = self.eq_treewidget.itemFromIndex(Qtindex)
    #         print(item.text(0))
    #         self.eq_wd = self.load_obj_eq(self.saved_eqs[item.text(0)])
    #         self.eq_wd.show()
    #     except Exception as e:
    #         print(e)

    # A princípio este método deve ser suprimido, depois que o evento de criar um novo equipamento for associado ao
    # método new_eq
    def getdataframe(self):
        if self.df is not None:
            try:
                self.eq_wd = eq.EQ_wd(self.portEqp, tree=self.eq_treewidget,eqps= self.saved_eqs, dfTags=self.dfTag)
                self.eq_wd.df_ml = self.df2
                self.eq_wd.check_df()
                #self.eq_wd.save_eq_pushbutton.clicked.connect(self.save_eq)
                self.eq_wd.show()
            except Exception as e:
                print(e)
        else:
            #self.new_eq()
            self.open_data()
            return

    # Evento gerado pelo self.objTransf, alterado dentro do dashboard. Atualiza o df para cálculo de FC e FI em batelada
    def newDF(self):
        coords=self.objTransf.getCoord()
        xmin = coords[0]
        xmax = coords[1]
        ymin = coords[2]
        ymax = coords[3]

        nomes=self.objTransf.getNames()

        r1 = self.df2[nomes[0]] > xmin
        r2 = self.df2[nomes[0]] <= xmax
        r3 = self.df2[nomes[1]] > ymin
        r4 = self.df2[nomes[1]] <= ymax
        self.dfFCFI=self.df2[r1 & r2 & r3 & r4]
        self.dfFCFI.to_excel('dataframeFCFI.xlsx', index=False)
        print('dataframe atualizado')

    # def save_fcfi(self):
    #     if self.fcfi_wd.saved_eqs != {}:
    #         self.saved_eqs = self.fcfi_wd.saved_eqs
    #         self.dump_eq()
    #         # self.eq_treewidget.clear()
    #         self.load_eq(treeLoad=False)
    #         self.fcfi_wd.close()
    #
    # def run_fcfi(self):
    #     self.fcfi_wd = FcFi_wd()
    #     self.fcfi_wd.saved_eqs = self.saved_eqs
    #     self.fcfi_wd.fsave_button.clicked.connect(self.fcfi_wd.calc_clicked)
    #     self.fcfi_wd.fsave_button.clicked.connect(self.save_fcfi)
    #     self.fcfi_wd.show()

    # evento associado ao botão "FC e FI" para cálculo em batelada
    def run_fcfi2(self):
        print('fcfi_1')
        self.fcfiForm=fcfiForm(self.saved_eqs,self.dfFCFI)
        print('fcfi_2')
        self.fcfiForm.show()
        #self.fcfiForm.calc_up_fcfi()
        print('fcfi_3')
        self.dump_eq()
        print('fcfi_4')
if __name__ == '__main__':
    app = QApplication([])
    window = Demo()
    window.show()
    app.exec_()
