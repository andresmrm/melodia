#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------
# Copyright 2009 Andrés Mantecon Ribeiro Martano
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#-----------------------------------------------------------------------------

import sys
import math
from struct import *

import pyaudio

from numpy import *
from numpy.fft import *

#import pygame
#from pygame import *
#from pygame.locals import *


sys.path.append('./ondas')
import ondas


class Melodia():
    
    def __init__(self):
        self.tam_amostra = 1024
        self.formato = pyaudio.paInt16
        self.canais = 1 
        self.frequencia = 44100
        
        self.audio = pyaudio.PyAudio()
        
        self.indice_entrada = -1
        self.indice_saida = -1
        
        for i in range(0, 10):
            try:
                info = self.audio.get_device_info_by_index(i)
                
                if self.indice_entrada == -1 and info["maxInputChannels"] > 0:
                    self.indice_entrada = i
                    
                if self.indice_saida == -1 and info["maxOutputChannels"] > 0:
                    self.indice_saida = i
                
                print info
                print "-------------------------\n"
            except:
                pass
            
        
        print "Iniciando Entrada " + str(self.indice_entrada)
        self.entrada = self.audio.open(format=self.formato,
                                  channels=self.canais,
                                  rate=self.frequencia,
                                  input=True,
                                  frames_per_buffer=self.tam_amostra,
                                  input_device_index=self.indice_entrada)
        
        self.entrada.stop_stream()
#        print(self.entrada.is_active())
        
        print "Iniciando Saida " + str(self.indice_saida)
        self.saida = self.audio.open(format=self.formato,
                                  channels=self.canais,
                                  rate=self.frequencia,
                                  output=True,
                                  output_device_index=self.indice_saida,
                                  frames_per_buffer=self.tam_amostra)
        
#        print(self.saida.is_active())
        
        # Valores básicos
        self.base = 55.0
        self.const = 1.0594630943592953
        self.notas = ["do", "do#", "re", "re#", "mi", "fa", "fa#",
                      "sol", "sol#", "la", "la#", "si"]        
        
    def encerrar(self):
        self.entrada.stop_stream()
        self.saida.stop_stream()
        self.entrada.close()
        self.saida.close()
        self.audio.terminate()

    def amostrar(self, tempo):
        
        self.entrada.start_stream()
        
        # Coleta as amostras do microfone
        amostras = []
        for i in range(0, int(self.frequencia / self.tam_amostra * tempo)):
            try:
                lido = self.entrada.read(self.tam_amostra)
            except:
                return 0, "0", 0
            amostras.append(lido)
        
        # Cria uma string com as amostras
        dados = ""
        for amostra in amostras:
            dados += amostra
        
        # Converte hex para floats
        som = []
        for i in range(len(dados) / 2):
            dado = unpack('h', dados[i * 2:i * 2 + 2])[0]
            som.append(float(dado))
            
        # Faz transformada
        asom = array(som)
        fourier = fft(asom)
        
        # Obtem os módulos das intensidades
        fou = []
        for f in fourier:
            fou.append(abs(f))
        fou.pop(0)
        
        # Acha índice da intensidade maior
        escolhido = max(fou)
        i = fou.index(escolhido)
        
        # Acha a frequência fundamental 
        freqs = fftfreq(len(asom), 1 / float(self.frequencia))
        frequencia = abs(freqs[i + 1])
        
        # Calcula nota e escala
        nota, escala = self.calc_not_esc(frequencia)
        
        self.entrada.stop_stream()
        
        return frequencia, nota, escala
    
    def parar_saida(self):
        self.saida.stop_stream()
#        self.saida.close()
        try:
            self.saida = self.audio.open(format=self.formato,
                                  channels=self.canais,
                                  rate=self.frequencia,
                                  output=True,
                                  output_device_index=self.indice_saida,
                                  frames_per_buffer=self.tam_amostra)
        except:
            print("Falhou ao tentar recriar stream")
    
    def calc_not_esc(self, frequencia):
        vnota = math.log(frequencia / self.base, self.const)
        vnota = int(round(vnota)) + 9
        nota = self.notas[vnota % 12]
        escala = vnota / 12
        return nota, escala
    
    def ajustar_base(self, freq):
        try:
            vnota = math.log(freq / self.base, self.const)
            dif = vnota - round(vnota)
            v = math.log(self.base, self.const)
            self.base = self.const ** (v + dif)
            vnota = math.log(freq / self.base, self.const)
        except:
            print("Falhou ao tentar mudar base")
        
    def voltar_base(self):
        self.base = 55.0
    
    def tocar2(self, lista_freq, tempo):
        
        # Gera onda
        frames = []
        for freq in lista_freq:
            for i in range(tempo * self.frequencia):
                valor = math.sin(2 * math.pi * (float(i) / 
                                                    float(self.frequencia)) * 
                                                    float(freq))
                frames.append(valor * 32000)
        
        # Tranforma onda para bytes puros
        dados = ""
        for i in frames:
            dados += pack("h", int(i))
        
        # Toca
        self.saida.start_stream()
        self.saida.write(dados)
        self.saida.stop_stream()
    
    def tocar(self, lista_freq, tempo):
        
         # Gera onda
        sons = []
        for freq in lista_freq:
            sons.append(self.gerar_onda(freq, tempo))
        
        # Tranforma onda para bytes puros
        dados = ""
        for som in sons:
            for i in som:
                dados += pack("h", int(i))
        
        # Toca
        self.saida.start_stream()
        self.saida.write(dados)
        self.saida.stop_stream()
        
    def tocart(self, lista_freqt, tempo):
        
        # Gera onda
        sons = []
        for freqt in lista_freqt:
            freq, t = freqt
            tempo_nota = tempo / float(2 ** t)
            sons.append(self.gerar_onda(freq, tempo_nota))
        
        # Tranforma onda para bytes puros
        dados = ""
        for som in sons:
            for i in som:
                dados += pack("h", int(i))
        
        # Toca
        try:
            self.saida.start_stream()
            self.saida.write(dados)
            self.saida.stop_stream()
        except:
            print("Falhou ao tentar esperar tocar")
        
    def gerar_onda(self, freq, tempo_nota):
        return ondas.gerar_onda(float(freq), float(tempo_nota), float(self.frequencia))
#        frames = []
#        ampli = [1.0]
#        for i in range(int(tempo_nota * self.frequencia)):
#            inst = 0
#            for j in range(len(ampli)):
#                inst += ampli[j] * math.sin(2 * math.pi * (float(i) / 
#                                            float(self.frequencia * (j + 1))) * 
#                                            float(freq))
#            frames.append(inst * 1000)
#        return frames

    def formatar_texto(self, t):
        t = t.splitlines()
        t2 = ""
        for linha in t:
            if linha.strip()[0] != "%":
                t2 += linha + " "
        t2 = t2.split(" ")
        return t2
        
    # Lê um arquivo e retorna as frequencias e tempos nele
    def ler_arq(self, nome):        
        texto = open(nome, "r").read()
        texto = self.formatar_texto(texto)
        freqs = []
        for nota in texto:
            try:
                freqs.append(self.calc_freq(nota))
            except:
                pass
        return freqs
    
    def ler_texto(self, texto):        
        texto = self.formatar_texto(texto)
        freqs = []
        for nota in texto:
            try:
                freqs.append(self.calc_freq(nota))
            except:
                pass
        return freqs
        
    def calc_freq(self, nnota):
        j = nnota.find("/")
        if nnota[0] is not "o":
            i = 1
            while not nnota[i].isdigit() and nnota[i] != "/":
                i += 1
                if i == len(nnota):
                    break
    
            nota = nnota[:i]
            if i == len(nnota) or nnota[i] is "/":
                escala = 4
            elif j is - 1:
                escala = nnota[i:]
            else:
                escala = nnota[i:j]
    
            if j is - 1:
                tempo = 4
            else:
                tempo = int(nnota[j + 1:])
                
#            print nota,escala,"/",tempo
            
            vnota = int(escala) * 12 + self.notas.index(nota) - 9
            freq = (self.const ** vnota) * self.base
            return (freq, tempo)
        else:    
            if j is - 1:
                tempo = 4
            else:
                tempo = int(nnota[j + 1:])
            return (0, tempo)

def configurar():
    teclas = []
    while True:
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        
        for i in keys:
            if i:
                indice = keys.index(i)
                if indice not in teclas:
                    teclas.append(indice)
                        
        if keys[pygame.K_ESCAPE]:
            arq = open("teclas", "w")
            for t in teclas:
                arq.write(str(t) + "\n")
            arq.close()
            break
        
def teclado():
    pygame.init()
    pygame.display.set_mode((100, 100))
    teclas = open("teclas", "r").read().splitlines()
    while True:
            pygame.event.pump()
            keys = pygame.key.get_pressed()
            
            for i in keys:
                if i:
                    indice = keys.index(i)
                    f = teclas.index(str(indice))
                    freq = m.const ** f * m.base
                    m.tocar([freq], 0.2)
                    print (m.calc_not_esc(freq))
                            
            if keys[pygame.K_ESCAPE]:
                break


if __name__ == "__main__":

    m = Melodia()

    try:
        resp = 0
        while resp is not "s":
            resp = raw_input()
            
            if resp is "n":
                f, n, e = m.amostrar(1)
                print("Freq: " + str(f))
                print("Nota: " + str(n) + " " + str(e))
                m.tocar([f], 1)
                #m.base = f
                
            elif resp is "g":
                lim = 200
                musica = []
                freqs = []
                for i in range(100):
                    f, n, e = m.amostrar(0.05)
                    if f > lim:
                        musica.append(n + str(e))
                        freqs.append(f)
                    else:
                        musica.append("o")
                        freqs.append(0)
                part = ""
                for n in musica:
                    part += n + " "
                print(part)
                m.tocar(freqs, 0.05)
                
            elif resp is "x":
                pass
                
            elif resp is "a":
                while resp is not "audio":
                    f, n, e = m.amostrar(0.2)
                    print("Freq: " + str(f))
                    print("Nota: " + str(n) + " " + str(e))
                    
            elif resp is "t":
                teclado()
                        
            elif resp is "l":
                m.tocart(m.ler_arq("musicas/bh"), 10)
    #            m.ler_arq("ode")
            
    except:
        m.encerrar()
        raise
    
    m.encerrar()
