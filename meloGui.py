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

from threading import Thread

try:
    import pygtk
    pygtk.require("2.0")
except:
    pass
try:
    import gtk
    import gtk.glade
except:
    sys.exit(1)
    
from melodia import Melodia


class gui():
    
    def __init__(self, melodia):
        
        self.melodia = melodia
        
        self.gladefile = "melodia.glade"  
        self.wTree = gtk.glade.XML(self.gladefile) 
        
        #Create our dictionay and connect it
        dic = { "on_b1t_toggled" : self.tocar1,
               "on_b1g_toggled" : self.gravar1,
               "on_b1ga_toggled" : self.gravar_auto1,
               "on_b1sim_clicked" : self.aceitar,
               "on_b1a_clicked" : self.abrir,
               "on_b1s_clicked" : self.salvar,
               "on_b1sc_clicked" : self.salvar_como,
               "on_w1_destroy" : self.fechar }
        self.wTree.signal_autoconnect(dic)
        
        self.texto1 = self.wTree.get_widget("t1")
        self.buffer_texto = gtk.TextBuffer(None)
        self.texto1.set_buffer(self.buffer_texto)
        
        self.label1 = self.wTree.get_widget("l1")
        
        self.b1g = self.wTree.get_widget("b1g")
        self.b1ga = self.wTree.get_widget("b1ga")
        self.b1t = self.wTree.get_widget("b1t")
        
        self.gravador_auto = None
        self.gravador1 = None
        self.tocador = None
        
        self.arquivo = None
        
    def fechar(self, widget):
        if self.gravador1 != None:
            self.gravador1.parar()
            self.gravador1.join()
        if self.gravador_auto != None:
            self.gravador_auto.parar()
            self.gravador_auto.join()
        if self.tocador != None:
            self.melodia.parar_saida()
            self.tocador.parar()
        gtk.main_quit()

    def tocar1(self, widget):
        if self.tocador == None:
            self.tocador = Executor(self.tocar)
            self.tocador.start()
        else:
            self.melodia.parar_saida()
            self.tocador.parar()
            self.tocador = None

    def tocar(self):
        try:
            com, fim = self.buffer_texto.get_selection_bounds()
        except:
            com, fim = self.buffer_texto.get_bounds()
        texto = self.buffer_texto.get_text(com, fim)
        m.tocart(m.ler_texto(texto), 10)
        if self.tocador != None:
            self.b1t.set_active(False)

    def gravar1(self, widget):
        if self.gravador_auto != None:
            self.b1ga.set_active(False)
            if self.gravador_auto != None:
                try:
                    self.gravador_auto.join()
                except:
                    print("Falhou ao tentar esperar gravador_auto")
        
        if self.gravador1 == None:
            f, n, e = self.melodia.amostrar(1)
            self.melodia.ajustar_base(f)
            self.gravador1 = Executor(self.gravar)
            self.gravador1.start()
        else:
            self.gravador1.parar()
            self.gravador1.join()
            self.gravador1 = None
            self.melodia.voltar_base()
    
    def gravar(self):
        f, n, e = self.melodia.amostrar(0.2)
        if f >= 200:
            self.buffer_texto.insert_at_cursor(n + str(e) + "/6 ")
        else:
            self.buffer_texto.insert_at_cursor("o" + "/6 ")
    
    def gravar_auto1(self, widget):
        if self.gravador1 != None:
            self.b1g.set_active(False)
            if self.gravador1 != None:
                try:
                    self.gravador1.join()
                except:
                    print("Falhou ao tentar esperar gravador")
        
        if self.gravador_auto == None:
            self.gravador_auto = Executor(self.gravar_auto)
            self.gravador_auto.start()
        else:
            self.gravador_auto.parar()
            self.gravador_auto.join()
            self.gravador_auto = None
            
    def gravar_auto(self):
        f, n, e = self.melodia.amostrar(0.2)
        if f > 100:
            self.label1.set_text(n + str(e) + " ")
                
    def aceitar(self, widget):
        self.buffer_texto.insert_at_cursor(self.label1.get_text())
        
    def abrir(self, widget):
        dialog = gtk.FileChooserDialog("Abrir...",
                                  None,
                                  gtk.FILE_CHOOSER_ACTION_OPEN,
                                  (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                  gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
         
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.buffer_texto.set_text(open(dialog.get_filename()).read())
            self.arquivo = dialog.get_filename()
        elif response == gtk.RESPONSE_CANCEL:
            pass
        dialog.destroy()
        
    def salvar(self, widget):
        if self.arquivo != None:
            com, fim = self.buffer_texto.get_bounds()
            texto = self.buffer_texto.get_text(com, fim)
            arq = open(self.arquivo, "w")
            arq.write(texto)
        else:
            self.salvar_como(widget)
        
    def salvar_como(self, widget):
        dialog = gtk.FileChooserDialog("Salvar...",
                                  None,
                                  gtk.FILE_CHOOSER_ACTION_SAVE,
                                  (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                  gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
         
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            com, fim = self.buffer_texto.get_bounds()
            texto = self.buffer_texto.get_text(com, fim)
            arq = open(dialog.get_filename(), "w")
            arq.write(texto)
            
            self.arquivo = dialog.get_filename()
        elif response == gtk.RESPONSE_CANCEL:
            pass
        dialog.destroy()
        
        
class Executor(Thread):
    
    def __init__(self, funcao):
        Thread.__init__(self)
        self.funcao = funcao
        self.gravando = True
        
    def run(self):
        while self.gravando:
            self.funcao()
            
    def parar(self):
        self.gravando = not self.gravando
                 
                
if __name__ == "__main__":   

    m = Melodia()
    
    g = gui(m)
    gtk.gdk.threads_init()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()
    m.encerrar()
