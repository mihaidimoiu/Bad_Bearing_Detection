from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import  QFileDialog
import pyqtgraph as pg

import pyaudio

import numpy as np

import wave

class Recorder(object):
    def __init__(self, channels=2, rate=44100, frames_per_buffer=1024):
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self._pa = pyaudio.PyAudio()
        self._stream = None
        self.frames = []
        self.in_data = []
        self.wf = None
        self.wf_read = None
        self.graf = GraphPlot()
        self.N = 512
        self.wave_x = 0
        self.wave_y = 0
        self.spec_x = 0
        self.spec_x = 0
        self.fft_out = 0
        self.fft_abs = 0
        self.y =  0
        self.count = 98
        self.statusRedare = False
        self.redare = None
        
    def start_recording(self):
        self.graf.graf1_params("FFT(Canal stang)", "Frecventa", "Putere", "Hz","", "r")
        self.graf.graf2_params("FFT(Canal drept)", "Frecventa", "Putere", "Hz","", "y")
        self.graf.graf3_params("PCM(Canal stang)", "Esantioane", "Amplitudine", "","", "r")
        self.graf.graf4_params("PCM(Canal drept)", "Esantioane", "Amplitudine", "","", "y")
        self.wf = self.save("output" + str(self.count) + ".wav")
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer,
                                        stream_callback=self.get_callback())
        self._stream.start_stream()
        self.count -= 1
        self.statusRedare = False
        return self
    
    def stop_recording(self):
        if self.statusRedare == True:
            #self._stream.stop_stream()
            self._stream.close()
            self.wf_read.close()
        else:
            if self._stream is not None:
                self._stream.stop_stream()
            if self.wf is not None:
                self.wf.close()
        
        return self

    
    def get_channels(self,filename):
        data = wave.open(filename,'rb')
        if data.getnchannels() == 1:
            data.close()
            return 1
        elif data.getnchannels() == 2:
            data.close()
            return 2
    
    def fft_full(self, filename):
        if filename != "":
            channels = 0
            from scipy.io import wavfile
            if self.get_channels(filename) == 1:
                self.graf.graf3_params("FFT(Mono)", "Frecventa", "Putere", "Hz", "","r")
                self.graf.graf4_params("", "", "", "", "","y")
                self.graf.plot_left([0,0,0],[0,0,0])
                self.graf.plot_right([0,0,0],[0,0,0])
                channels = 1
            elif self.get_channels(filename) == 2:
                self.graf.graf3_params("FFT(Canal Stang)", "Frecventa", "Putere", "Hz", "", "r")
                self.graf.graf4_params("FFT(Canal Drept)", "Frecventa", "Putere", "Hz", "", "y")
                self.graf.plot_left([0,0],[0,0])
                self.graf.plot_right([0,0],[0,0])
                channels = 2
            fs, data = wavfile.read(filename)
            data_ch1 = 0
            data_ch2 = 0
            if channels == 2:
                data_ch1 = data[:,0]
                data_ch2 = data[:,1]
                data_len1 = int(len(data_ch1))
                data_len2 = int(len(data_ch2))
                
                y1 = np.fft.fft(data_ch1[0 : data_len1])
                fft_out1 = np.fft.fftfreq(data_len1, d = 1.0/fs)
                
                fft_abs1 = np.abs(y1)
                self.graf.plot_left(fft_out1, fft_abs1)
                
                y2 = np.fft.fft(data_ch1[0 : data_len2])
                fft_out2 = np.fft.fftfreq(data_len2, d = 1.0/fs)
                
                fft_abs2 = np.abs(y2)
                self.graf.plot_right(fft_out2, fft_abs2)
            
            if channels == 1:
                data_len = int(len(data))
    
                y = np.fft.fft(data[0:data_len])
                fft_out = np.fft.fftfreq(data_len, d = 1.0/fs)
               
        
                fft_abs = np.abs(y) #[np.sqrt(c[0].real ** 2 + c[1].imag ** 2) for c in y]
               
                self.graf.plot_left(fft_out, fft_abs)

        else:
            print("plm acum merge")

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            self.wf.writeframes(in_data)
            data_int = np.frombuffer(in_data, dtype=np.int16)
            #data_int = np.reshape(data_int, (self.frames_per_buffer, 2))
            if self.channels == 1:
                
                self.wave_x = range(0,self.N)
                self.wave_y = data_int[0:self.N]
                
                self.y = np.fft.fft(data_int[0:self.N])
                 
                self.spec_x = np.fft.fftfreq(self.N,d = 1.0/self.rate)
                self.spec_y=[np.sqrt(c.real ** 2 + c.imag ** 2) for c in self.y]
                
                self.graf.plot_fft(self.spec_x, self.spec_y)
                self.graf.plot_pcm(self.wave_x, self.wave_y)
            elif self.channels == 2:
                data_int = np.reshape(data_int, (self.frames_per_buffer, 2))
                data_ch1 = data_int[:,0]
                data_ch2 = data_int[:,1]
                
                wave_x1 = range(0, self.N)
                wave_y1 = data_ch1[0:self.N]
                
                wave_x2 = range(0, self.N)
                wave_y2 = data_ch2[0:self.N]
                
                self.graf.plot_fft(wave_x1, wave_y1)
                self.graf.plot_pcm(wave_x2, wave_y2)
                
                data_len1 = int(len(data_ch1))
                data_len2 = int(len(data_ch2))
                
                y1 = np.fft.fft(data_ch1[0 : data_len1])
                fft_out1 = np.fft.fftfreq(data_len1, d = 1.0/self.rate)
                
                fft_abs1 = np.abs(y1)
                self.graf.plot_left(fft_out1, fft_abs1)
                
                y2 = np.fft.fft(data_ch1[0 : data_len2])
                fft_out2 = np.fft.fftfreq(data_len2, d = 1.0/self.rate)
                
                fft_abs2 = np.abs(y2)
                self.graf.plot_right(fft_out2, fft_abs2)
            #self.frames.append(in_data)
            return (in_data, pyaudio.paContinue)
        return callback
    def close(self):
        if self._stream is not None:
            self._stream.close()
        self._pa.terminate()
        if self.wf is not None:
            self.wf.close()
        
    def save(self, filename):
        wavefile = wave.open(filename, 'wb')
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate)
        return wavefile
        
    def clear(self):
        self.frames = []
        
    def _play(self,filename):
        
        #self.graf.graf1_params("PCM(Canal stang)", "Esantioane", "Amplitudine", "N","", "r")
        #self.graf.graf2_params("PCM(Canal drept)", "Esantioane", "Amplitudine", "N","", "y")
        #self.graf.graf3_params("FFT(Canal stang)", "Frecventa", "Putere", "Hz","", "r")
        #self.graf.graf4_params("FFT(Canal drept)", "Frecventa", "Putere", "Hz","", "y")
        channels = 0
        if self.get_channels(filename) == 1:
            self.graf.graf1_params("FFT(Mono)", "Frecventa", "Putere", "Hz", "","r")
            self.graf.graf2_params("PCM(Mono)", "Esantioane", "Amplitudine", "N", "","y")
            self.graf.plot_fft([0,0,0],[0,0,0])
            self.graf.plot_pcm([0,0,0],[0,0,0])
            channels = 1
        elif self.get_channels(filename) == 2:
            self.graf.graf1_params("PCM(Canal stang)", "Esantioane", "Amplitudine", "N","", "r")
            self.graf.graf2_params("PCM(Canal drept)", "Esantioane", "Amplitudine", "N","", "y")
            self.graf.graf3_params("FFT(Canal stang)", "Frecventa", "Putere", "Hz","", "r")
            self.graf.graf4_params("FFT(Canal drept)", "Frecventa", "Putere", "Hz","", "y")
            self.graf.plot_fft([0,0],[0,0])
            self.graf.plot_pcm([0,0],[0,0])
            self.graf.plot_left([0,0],[0,0])
            self.graf.plot_right([0,0],[0,0])
            channels = 2
        self.statusRedare = True
        self.wf_read = wave.open(filename,"rb")
        self._stream = self._pa.open(format = self._pa.get_format_from_width(self.wf_read.getsampwidth()),
                channels = self.wf_read.getnchannels(),
                rate = self.wf_read.getframerate(),
                output = True,
                stream_callback = self.callback_play(channels))
        self._stream.start_stream()
        #while _stream.is_active():
        #    sleep(0.1)
        #_stream.stop_stream()
            
    def callback_play(self,channels):
        def callbacki(in_data, frame_count, time_info, status):
            data = self.wf_read.readframes(frame_count)
            data_int = np.frombuffer(data, dtype=np.int16);
            #print(data_int)
            if channels == 1:
                
                self.wave_x = range(0,self.N)
                self.wave_y = data_int[0:self.N]
                
                self.y = np.fft.fft(data_int[0:self.N])
                 
                self.spec_x = np.fft.fftfreq(self.N,d = 1.0/self.rate)
                self.spec_y=[np.sqrt(c.real ** 2 + c.imag ** 2) for c in self.y]
                
                self.graf.plot_fft(self.spec_x, self.spec_y)
                self.graf.plot_pcm(self.wave_x, self.wave_y)
            elif channels == 2:
                data_int = np.reshape(data_int, (self.frames_per_buffer, 2))
                data_ch1 = data_int[:,0]
                data_ch2 = data_int[:,1]
                
                wave_x1 = range(0, self.N)
                wave_y1 = data_ch1[0:self.N]
                
                wave_x2 = range(0, self.N)
                wave_y2 = data_ch2[0:self.N]
                
                self.graf.plot_fft(wave_x1, wave_y1)
                self.graf.plot_pcm(wave_x2, wave_y2)
                
                data_len1 = int(len(data_ch1))
                data_len2 = int(len(data_ch2))
                
                y1 = np.fft.fft(data_ch1[0 : data_len1])
                fft_out1 = np.fft.fftfreq(data_len1, d = 1.0/self.rate)
                
                fft_abs1 = np.abs(y1)
                self.graf.plot_left(fft_out1, fft_abs1)
                
                y2 = np.fft.fft(data_ch1[0 : data_len2])
                fft_out2 = np.fft.fftfreq(data_len2, d = 1.0/self.rate)
                
                fft_abs2 = np.abs(y2)
                self.graf.plot_right(fft_out2, fft_abs2)
            '''self.wave_x = range(0,self.N)
            self.wave_y = data_int[0:self.N]
            
            self.y = np.fft.fft(data_int[0:self.N])
           
            self.spec_x = np.fft.fftfreq(self.N,d = 1.0/self.rate)
       
            self.spec_y=[np.sqrt(c.real ** 2 + c.imag ** 2) for c in self.y]
           
        
            self.graf.plot_fft(self.spec_x, self.spec_y)
            self.graf.plot_pcm(self.wave_x, self.wave_y)'''
            return (data, pyaudio.paContinue)
        return callbacki




class GraphPlot(object):
    def __init__(self, title = "Mecatronica", size_x= 640, size_y = 480):
        self.win = pg.GraphicsWindow()
        self.win.resize(size_x, size_y)
        self.win.setWindowTitle(title)
        
        self.graf = self.win.addPlot()
        self.curve = None
        
        self.graf2 = self.win.addPlot()
        self.curve2 = None
        
        self.win.nextRow()
        
        self.graf3 = self.win.addPlot()
        self.curve3 = None
 
        self.graf4 = self.win.addPlot()
        self.curve4 = None
        
        self.win.show()
    def graf1_params(self, title = "Graf 1", labelX = "", labelY = "", unitsX = "", unitsY = "", color = 'y'):
        self.graf.setLabel('left',labelY, units = unitsY)
        self.graf.setLabel('bottom',labelX,units = unitsX)
        self.graf.setTitle(title)
        self.curve = self.graf.plot(pen = color)
        
    def graf2_params(self, title = "Graf 2", labelX = "", labelY = "", unitsX = "", unitsY = "" ,color = 'y'):
        self.graf2.setLabel('left',labelY,units = unitsY)
        self.graf2.setLabel('bottom',labelX,units = unitsX)
        self.graf2.setTitle(title)
        self.curve2 = self.graf2.plot(pen = color)
        
    def graf3_params(self, title = "Graf 3", labelX = "", labelY = "", unitsX = "", unitsY = "", color = 'y'):
        self.graf3.setLabel('left',labelY, units = unitsY)
        self.graf3.setLabel('bottom',labelX,units = unitsX)
        self.graf3.setTitle(title)
        self.curve3 = self.graf3.plot(pen = color)
        
    def graf4_params(self, title = "Graf 4", labelX = "", labelY = "", unitsX = "", unitsY = "", color = 'y'):
        self.graf4.setLabel('left',labelY,units = unitsY)
        self.graf4.setLabel('bottom',labelX,units = unitsX)
        self.graf4.setTitle(title)
        self.curve4 = self.graf4.plot(pen = color)
        
    def clear_axis(self, number):
        if number == 1:
            self.graf.clear()
        if number == 2:
            self.graf2.clear()
        if number == 3:
            self.graf3.clear()
        if number == 4:
            self.graf4.clear()

    def plot_fft(self, data_x, data_y):
        self.curve.setData(data_x, data_y)
    def plot_pcm(self, data_x, data_y):
        self.curve2.setData(data_x, data_y)
    def plot_left(self, data_x, data_y):
        #self.graf3.setXRange(0,23000,padding=0)
        self.curve3.setData(data_x, data_y)
    def plot_right(self, data_x, data_y):
        self.curve4.setData(data_x, data_y)

    def open_graphic(self):
        self.win.show()
    def close(self):
        self.win.close()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.left = 10
        self.top = 10
        self.width = 1170
        self.height = 720
        self.rec = Recorder()
        self.limba_sel = "engleza"
        self.fileName = ""
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(961, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_imagine = QtWidgets.QLabel(self.centralwidget)
        self.label_imagine.setGeometry(QtCore.QRect(120, 130, 791, 301))
        self.label_imagine.setMinimumSize(QtCore.QSize(791, 0))
        self.label_imagine.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.label_imagine.setStyleSheet("#label_imagine{\n"
                                         "background-color: transparent;\n"
                                         "border-image: url(:img/Meca.png);\n"
                                         "background: none;\n"
                                         "border: none;\n"
                                         "background-repeat: none;\n"
                                         "width:100%;\n"
                                         "}")
        self.label_imagine.setText("")
        self.label_imagine.setWordWrap(False)
        self.label_imagine.setObjectName("label_imagine")
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(20, 30, 221, 31))
        self.comboBox.setEditable(False)
        self.comboBox.setCurrentText("")
        self.comboBox.setObjectName("comboBox")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 10, 81, 16))
        self.label_2.setObjectName("label_2")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(270, 10, 131, 20))
        self.label.setObjectName("label")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(430, 10, 161, 16))
        self.label_3.setObjectName("label_3")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(270, 30, 131, 31))
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser_2 = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser_2.setGeometry(QtCore.QRect(430, 30, 161, 31))
        self.textBrowser_2.setObjectName("textBrowser_2")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(620, 10, 147, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(790, 10, 171, 16))
        self.label_5.setObjectName("label_5")
        self.textBrowser_3 = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser_3.setGeometry(QtCore.QRect(620, 30, 147, 31))
        self.textBrowser_3.setObjectName("textBrowser_3")
        self.textBrowser_4 = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser_4.setGeometry(QtCore.QRect(790, 30, 151, 31))
        self.textBrowser_4.setObjectName("textBrowser_4")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 961, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuLanguage = QtWidgets.QMenu(self.menubar)
        self.menuLanguage.setObjectName("menuLanguage")
        self.menuOpen = QtWidgets.QMenu(self.menubar)
        self.menuOpen.setObjectName("menuOpen")
        self.menuExit = QtWidgets.QMenu(self.menubar)
        self.menuExit.setObjectName("menuExit")
        self.menuLanguage = QtWidgets.QMenu(self.menubar)
        self.menuLanguage.setObjectName("menuLanguage")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setGeometry(QtCore.QRect(350, 10, 100, 21))
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.toolBar.setIconSize(QtCore.QSize(48, 48))
        self.toolBar.setFloatable(True)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionEdit = QtWidgets.QAction(MainWindow)
        self.actionEdit.setObjectName("actionEdit")
        self.actionRecord = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/img/redare.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRecord.setIcon(icon)
        self.actionRecord.setObjectName("actionRecord")
        self.actionInregistrare = QtWidgets.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/img/record.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionInregistrare.setIcon(icon1)
        self.actionInregistrare.setObjectName("actionInregistrare")
        self.actionStop_inregistrare_2 = QtWidgets.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/img/recordoff.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionStop_inregistrare_2.setIcon(icon2)
        self.actionStop_inregistrare_2.setObjectName("actionStop_inregistrare_2")
        self.actionOpen_file = QtWidgets.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/img/open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpen_file.setIcon(icon3)
        self.actionOpen_file.setObjectName("actionOpen_file")
        self.actionShow_graphic = QtWidgets.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/img/grafic.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionShow_graphic.setIcon(icon4)
        self.actionShow_graphic.setObjectName("actionShow_graphic")
        self.actionClose_application = QtWidgets.QAction(MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/img/exit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionClose_application.setIcon(icon5)
        self.actionClose_application.setObjectName("actionClose_application")
        self.actionRomanian = QtWidgets.QAction(MainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/img/romania.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRomanian.setIcon(icon6)
        self.actionRomanian.setObjectName("actionRomanian")
        self.actionEnglish = QtWidgets.QAction(MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/img/uk.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionEnglish.setIcon(icon7)
        self.actionEnglish.setObjectName("actionEnglish")
        self.actionGerman = QtWidgets.QAction(MainWindow)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/img/german.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionGerman.setIcon(icon8)
        self.actionGerman.setObjectName("actionGerman")
        self.actionLoad_full_graphic = QtWidgets.QAction(MainWindow)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/img/grafic2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionLoad_full_graphic.setIcon(icon9)
        self.actionLoad_full_graphic.setObjectName("actionLoad_full_graphic")
        self.actionCompare = QtWidgets.QAction(MainWindow)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/img/compare.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCompare.setIcon(icon10)
        self.actionCompare.setObjectName("actionCompare")
        self.menuFile.addAction(self.actionRecord)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionInregistrare)
        self.menuFile.addAction(self.actionStop_inregistrare_2)
        self.menuFile.addSeparator()
        self.menuOpen.addAction(self.actionOpen_file)
        self.menuOpen.addSeparator()
        self.menuOpen.addAction(self.actionShow_graphic)
        self.menuOpen.addAction(self.actionLoad_full_graphic)
        self.menuOpen.addSeparator()
        self.menuOpen.addAction(self.actionCompare)
        self.menuExit.addAction(self.actionClose_application)
        self.menuLanguage.addAction(self.actionRomanian)
        self.menuLanguage.addAction(self.actionEnglish)
        self.menuLanguage.addAction(self.actionGerman)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuOpen.menuAction())
        self.menubar.addAction(self.menuLanguage.menuAction())
        self.menubar.addAction(self.menuExit.menuAction())
        self.toolBar.addAction(self.actionInregistrare)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionStop_inregistrare_2)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionRecord)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionOpen_file)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionLoad_full_graphic)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionShow_graphic)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionCompare)
        #self.toolBar.addSeparator() # compara
        self.toolBar.addAction(self.actionClose_application)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        self.actionClose_application.triggered.connect(self.iesire)
        self.actionInregistrare.triggered.connect(self.inreg)
        self.actionStop_inregistrare_2.triggered.connect(self.inreg_stop)
        self.actionRecord.triggered.connect(self.redare)
        self.actionOpen_file.triggered.connect(self.openFileNameDialog)
        self.actionShow_graphic.triggered.connect(self.fxn1)
        self.comboBox.addItem(None)
        self.comboBox.addItem("KOYO 6207 RSANB GA2")
      
       
        self.comboBox.currentIndexChanged.connect(self.calculare_frecv)
        self.textBrowser.setText("0")
        self.textBrowser_2.setText("0")
        self.textBrowser_3.setText("0")
        self.textBrowser_4.setText("0")
        
        self.actionCompare.setVisible(False) #compara
        
        self.actionLoad_full_graphic.triggered.connect(self.full_graphic)
        self.actionEnglish.triggered.connect(self.engli)
        self.actionEnglish.setShortcut('Ctrl+E')
        self.actionRomanian.triggered.connect(self.romani)
        self.actionRomanian.setShortcut('Ctrl+R')
        self.actionGerman.triggered.connect(self.germ)
        self.actionGerman.setShortcut('Ctrl+G')

        self.stats("Ready to run")

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        if self.limba_sel == "romana":
            MainWindow.setWindowTitle(_translate("MainWindow", "Aplicatie Mecatronica"))
        elif self.limba_sel == "engleza":
            MainWindow.setWindowTitle(_translate("MainWindow", "Mechatronics application"))
        elif self.limba_sel == "germana":
            MainWindow.setWindowTitle(_translate("MainWindow", "Mechatronik App"))
        self.label.setText(_translate("MainWindow", "Frequency Cage [Hz]"))
        self.label_3.setText(_translate("MainWindow", "Frequency Ball Defect [Hz]"))
        self.label_4.setText(_translate("MainWindow", "Ball Diameter [mm]"))
        self.label_5.setText(_translate("MainWindow", "Pitch Diameter [mm]"))
        self.label_2.setText(_translate("MainWindow", "Bearing series"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuOpen.setTitle(_translate("MainWindow", "Options"))
        self.menuLanguage.setTitle(_translate("MainWindow", "Language"))
        self.menuExit.setTitle(_translate("MainWindow", "Exit"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionEdit.setText(_translate("MainWindow", "Edit"))
        self.actionRecord.setText(_translate("MainWindow", "Play record"))
        self.actionInregistrare.setText(_translate("MainWindow", "Record"))
        self.actionStop_inregistrare_2.setText(_translate("MainWindow", "Stop recording"))
        self.actionOpen_file.setText(_translate("MainWindow", "Open file..."))
        self.actionShow_graphic.setText(_translate("MainWindow", "Show graphic"))
        self.actionClose_application.setText(_translate("MainWindow", "Close application"))
        self.actionRomanian.setText(_translate("MainWindow", "Romanian"))
        self.actionEnglish.setText(_translate("MainWindow", "English"))
        self.actionLoad_full_graphic.setText(_translate("MainWindow", "Load full graphic"))
        self.actionGerman.setText(_translate("MainWindow", "German"))
        self.actionCompare.setText(_translate("MainWindow", "Compare"))
        
    def iesire(self):
        self.rec.graf.close()
        self.rec.close()
        MainWindow.close()
    
    def full_graphic(self):
        if self.fileName != "":
            self.rec.fft_full(self.fileName)
        else: print("pula")
        
    def fxn1(self):
        self.rec.graf.open_graphic()
        if self.limba_sel == "romana":
            self.stats("Graficul este deschis")
        elif self.limba_sel == "engleza":
            self.stats("Graphic is open")
        elif self.limba_sel == "germana":
            self.stats("Grafik ist offen")
        
        
    def openFileNameDialog(self):    
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getOpenFileName(None,"QFileDialog.getOpenFileName()", "","Sounds (*.wav *.mp4 *.m4a)", options=options)
        if self.fileName:
            print(self.fileName)
            if self.limba_sel == "romana":
                self.stats("Fisier deschis: " + self.fileName)
            elif self.limba_sel == "engleza":
                self.stats("File open: " + self.fileName)
            elif self.limba_sel == "germana":
                self.stats("Datei öffnen" + self.fileName)            
            
    def romani(self):
        self.menuLanguage.setTitle("Limba")
        self.menuFile.setTitle("Fisier")
        self.menuExit.setTitle("Iesire")
        self.menuOpen.setTitle("Optiuni")
        self.limba_sel = "romana"
        self.actionClose_application.setText("Iesire")
        self.actionInregistrare.setText("Inregistrare")
        self.actionStop_inregistrare_2.setText("Stop Inregistrare")
        self.actionRecord.setText("Redare")
        self.actionEnglish.setText("Engleza")
        self.actionGerman.setText("Germana")
        self.actionOpen_file.setText("Deschide fisier...")
        self.actionShow_graphic.setText("Arata grafic")
        self.label_2.setText("Serie rulment")
        self.label.setText("Frecventa Coliviei [Hz]")
        self.label_3.setText( "Frecventa Bilei Defecte [Hz]")
        self.label_4.setText("Diametrul Bilei [mm]")
        self.label_5.setText("Diametrul Interior [mm]")
        self.actionLoad_full_graphic.setText("Incarca graficul complet")
        self.actionCompare.setText("Compara")
        MainWindow.setWindowTitle("Aplicatie Mecatronica")
        print('Limba este acum Romana.')
        self.stats('Limba este acum Romana.')
        
    def engli(self):
        self.menuLanguage.setTitle("Language")
        self.menuFile.setTitle("File")
        self.menuExit.setTitle("Exit")
        self.menuOpen.setTitle("Options")
        self.limba_sel = "engleza"
        self.actionClose_application.setText("Close application")
        self.actionInregistrare.setText("Record")
        self.actionStop_inregistrare_2.setText("Stop recording")
        self.actionRecord.setText("Play")
        self.actionEnglish.setText("English")
        self.actionGerman.setText("German")
        self.actionOpen_file.setText("Open file...")
        self.actionShow_graphic.setText("Show graphic")
        self.label_2.setText("Bearing series")
        self.label.setText("Frequency Cage [Hz]")
        self.label_3.setText( "Frequency Ball Defect [Hz]")
        self.label_4.setText("Ball Diameter [mm]")
        self.label_5.setText("Pitch Diameter [mm]")
        self.actionLoad_full_graphic.setText("Load full graphic")
        self.actionCompare.setText("Compare")
        MainWindow.setWindowTitle("Mechatronics application")
        print('Language is now English.')
        self.stats('Language is now English.')
        
        
    def germ(self):
        self.menuLanguage.setTitle("Sprache")
        self.menuFile.setTitle("Sprache")
        self.menuFile.setTitle("Datei")
        self.menuExit.setTitle("Ausfahrt")
        self.menuOpen.setTitle("Optionen")
        self.limba_sel = "germana"
        self.actionClose_application.setText("Schließen")
        self.actionInregistrare.setText("Aufzeichnung")
        self.actionStop_inregistrare_2.setText("Aufzeichnung stoppen")
        self.actionRecord.setText("Abspielen")
        self.actionEnglish.setText("Englisch")
        self.actionGerman.setText("Deutsche")
        self.actionOpen_file.setText("Datei öffnen...")
        self.actionShow_graphic.setText("Grafik anzeigen")
        self.label_2.setText("Lagerreihe")
        self.label.setText("Frequenzkäfig [Hz]")
        self.label_3.setText( "Frequenz Ball Defekt [Hz]")
        self.label_4.setText("Kugel durchmesser [mm]")
        self.label_5.setText("Tonhöhe durchmesserr [mm]")
        self.actionLoad_full_graphic.setText("Laden volle Grafik")
        self.actionCompare.setText("Vergleichen")
        MainWindow.setWindowTitle("Mechatronik App")
        print('Sprache ist jetzt Deutsch.')
        self.stats('Sprache ist jetzt Deutsch.')
        
    def calculare_frecv(self):
        import math
        if str(self.comboBox.currentText()) == "KOYO 6207 RSANB GA2":
            ni = 1900
            dm = 35
            Da = 8
            alpha = 0
            f_c = 1 / 60 * ni / 2 * (1 - (Da * math.cos(alpha)) / dm)
            f_b = 1 / 60 * ni / 2 * (dm / Da - (Da * math.cos(alpha) * math.cos(alpha)) / dm)
            self.textBrowser.setText(str(round(f_c,2)))
            self.textBrowser_2.setText(str(round(f_b,2)))
            self.textBrowser_3.setText(str(dm))
            self.textBrowser_4.setText(str(Da))
            return f_c, f_b
        else:
            self.textBrowser.setText("0")
            self.textBrowser_2.setText("0")
            self.textBrowser_3.setText("0")
            self.textBrowser_4.setText("0")
    

    def inreg(self):
        if self.limba_sel == "romana":
            self.stats("Inregistrare")
        elif self.limba_sel == "engleza":
            self.stats("Recording")
        elif self.limba_sel == "germana":
            self.stats("Aufzeichnung")
        self.rec.start_recording()
        
    def inreg_stop(self):
        self.rec.stop_recording()
        if self.rec.statusRedare == True:
            if self.limba_sel == "romana":
                self.stats("Redare terminata")
            elif self.limba_sel == "engleza":
                self.stats("Stop playing")
            elif self.limba_sel == "germana":
                self.stats("Hör auf zu spielen")
            print("Redare terminata")
        elif self.rec.statusRedare == False:
            if self.limba_sel == "romana":
                self.stats("Inregistrare terminata")
            elif self.limba_sel == "engleza":
                self.stats("Stop recording")
            elif self.limba_sel == "germana":
                self.stats("Höre auf, aufzunehmen")
            print("Inregistrare terminata")
        
    def redare(self):
        if self.fileName != "":
            if self.limba_sel == "romana":
                self.stats("Redare")
            elif self.limba_sel == "engleza":
                self.stats("Playing")
            elif self.limba_sel == "germana":
                self.stats("Spielen")
            self.rec._play(self.fileName)
            print("redare")
            if self.limba_sel == "romana":
                self.stats("Redare terminata")
            elif self.limba_sel == "engleza":
                self.stats("Playing over")
            elif self.limba_sel == "germana":
                self.stats("Überspielen")
        else:
            if self.limba_sel == "romana":
                self.stats("Alegeti un fisier")
            elif self.limba_sel == "engleza":
                self.stats("Choose file:")
            elif self.limba_sel == "germana":
                self.stats("Datei wählen:")
        
    def stats(self,msg):
       self.statusbar.showMessage(msg)
       

import resource

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

