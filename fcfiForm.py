from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow,\
    QHBoxLayout, QLabel, QDoubleSpinBox, QFrame, QFileDialog, QMessageBox, QInputDialog, QScrollArea
from PyQt5.QtCore import Qt
import sys
import pandas as pd
import os
import numpy as np

class fcfiForm(QMainWindow):
    def __init__(self, saved_eqs, df) -> None:
        super().__init__()
        uic.loadUi('fcfi2.ui', self)
        self.saved_eqs=saved_eqs
        self.df=df
        self.aplicar_PB.clicked.connect(self.calc_up_fcfi)


    def calc_up_fcfi(self):
        for eqp in self.saved_eqs.keys():
            media=self.df[self.saved_eqs[eqp].varDep].mean()
            denominador =1
            if self.max_RB.isChecked():
                denominador=self.df[self.saved_eqs[eqp].varDep].max()

            if self.quantil_RB.isChecked():
                denominador = self.df[self.saved_eqs[eqp].varDep].quantile(float(self.quantil_SB.value()) / 100)

            if self.potNom_RB.isChecked():
                denominador = self.saved_eqs[eqp].potNominal

            if self.potProc_RB.isChecked():
                denominador = self.saved_eqs[eqp].potProc

            FC = media/denominador

            ligado = self.df.loc[
                self.df[self.saved_eqs[eqp].varDep] > self.potOff_SB.value(), self.saved_eqs[eqp].varDep].count()
            total = self.df[self.saved_eqs[eqp].varDep].count()

            FI = ligado / total

            self.saved_eqs[eqp].fc = FC
            self.saved_eqs[eqp].fi = FI

        self.close()

