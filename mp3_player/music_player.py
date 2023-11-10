from PyQt5.QtWidgets import (QWidget, QDesktopWidget,
    QMessageBox, QHBoxLayout, QVBoxLayout, QSlider, QListWidget,
    QPushButton, QLabel, QComboBox, QApplication, QFileDialog, QLineEdit)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import sys, os, time, random

class MP3Player(QWidget):
    def __init__(self):
        super().__init__()

        
        self.startTimeLabel = QLabel('00:00')
        self.endTimeLabel = QLabel('00:00')
        self.slider = QSlider(Qt.Horizontal, self)
        self.playBtn = QPushButton(self)
        self.playBtn.clicked.connect(self.playMusic)
        self.prevBtn = QPushButton(self)
        self.prevBtn.clicked.connect(self.prevMusic)
        self.nextBtn = QPushButton(self)
        self.nextBtn.clicked.connect(self.nextMusic)
        self.openBtn = QPushButton(self)
        self.openBtn.clicked.connect(self.openMusicFolder)
        self.musicList = QListWidget()
        self.musicList.itemDoubleClicked.connect(self.doubleClicked)
        # self.modeCom = QComboBox()
        # self.modeCom.addItem(' Play in order ')
        # self.modeCom.addItem(' Loop ')
        # self.modeCom.addItem(' Shuffle Play ')
        self.playModeBtn = QPushButton()
        self.playModeBtn.clicked.connect(self.playModeSet)
        self.playMode = 0
        self.authorLabel = QLabel(' ')
        self.textLable = QLabel(' ')
        self.versionLabel = QLabel(' ')
        self.searchBar = QLineEdit()
        self.searchBar.returnPressed.connect(self.musicSearch)
        self.searchBar.setStyleSheet('font-size: 16px; height: 24px; color: white;')
        self.playBtn.setStyleSheet("color: white;"
                                   "background-color: #2c2f33;"
                                   "selection-color: white;"
                                   #"border-color: #2c2f33;"
                                   #"border-width: 2px;"
                                   #"border-style: outset;"
                                   "border-image: url(mp3_player/play.png);")
        self.playBtn.setFixedSize(64, 64)
        self.prevBtn.setStyleSheet("color: white;"
                                   "background-color: #2c2f33;"
                                   "selection-color: white;"
                                   "border-color: #23272a;"
                                   "border-width: 2px;"
                                   "border-style: outset;"
                                   "border-image: url(mp3_player/prev.png);")
        self.prevBtn.setFixedSize(64, 64)
        self.nextBtn.setStyleSheet("color: white;"
                                   "background-color: #2c2f33;"
                                   "selection-color: white;"
                                   "border-color: #23272a;"
                                   "border-width: 2px;"
                                   "border-style: outset;"
                                   "border-image: url(mp3_player/next.png);")
        self.nextBtn.setFixedSize(64, 64)
        self.openBtn.setStyleSheet("color: white;"
                                   "background-color: #2c2f33;"
                                   "selection-color: white;"
                                   "border-color: #23272a;"
                                   "border-width: 2px;"
                                   "border-style: outset;"
                                   "border-image: url(mp3_player/folder.png);")
        self.openBtn.setFixedSize(32, 32)
        self.playModeBtn.setStyleSheet("color: white;"
        #                            "background-color: #2c2f33;"
        #                            "selection-color: white;"
        #                            "border-color: #23272a;"
        #                            "border-width: 2px;"
                                    "border-image: url(mp3_player/sequence.png);")
        self.playModeBtn.setFixedSize(32, 32)
        self.musicList.setStyleSheet("color: white;"
                                   "background-color: #2c2f33;"
                                   "selection-color: white;"
                                   "border-color: #23272a;"
                                   "border-width: 2px;"
                                   "border-style: outset;")
    
        self.hBoxSlider = QHBoxLayout()
        self.hBoxSlider.addWidget(self.startTimeLabel)
        self.hBoxSlider.addWidget(self.slider)
        self.hBoxSlider.addWidget(self.endTimeLabel)
    
        self.hBoxButton = QHBoxLayout()
        self.hBoxButton.addWidget(self.playModeBtn)
        self.hBoxButton.addWidget(self.prevBtn)
        self.hBoxButton.addWidget(self.playBtn)
        self.hBoxButton.addWidget(self.nextBtn)
        self.hBoxButton.addWidget(self.openBtn)
    
        self.vBoxControl = QVBoxLayout()
        self.vBoxControl.addLayout(self.hBoxSlider)
        self.vBoxControl.addLayout(self.hBoxButton)
            
        self.hBoxAbout = QHBoxLayout()
        self.hBoxAbout.addWidget(self.authorLabel)
        self.hBoxAbout.addStretch(1)
        self.hBoxAbout.addWidget(self.textLable)
        self.hBoxAbout.addStretch(1)
        self.hBoxAbout.addWidget(self.versionLabel)
        
    
        self.vboxMain = QVBoxLayout()
        self.vboxMain.addWidget(self.searchBar)
        self.vboxMain.addWidget(self.musicList)
        self.vboxMain.addLayout(self.vBoxControl)
        self.vboxMain.addLayout(self.hBoxAbout)
        
        self.player = QMediaPlayer()
        self.is_switching = False
        
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.playByMode)
        
        self.song_formats = ['mp3', 'm4a', 'flac', 'wav', 'ogg']
        self.songs_list = []
        self.cur_playing_song = ''
        self.is_pause = True
        self.setAcceptDrops(True)
        
        self.setLayout(self.vboxMain)

        self.initUI()

    def initUI(self):
        self.resize(600, 400)
        self.center()
        self.setWindowTitle('MP3 player')   
        self.setWindowIcon(QIcon('mp3_player/music.png'))
        self.show()
        self.setStyleSheet("background-color: #2c2f33")
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def openMusicFolder(self):
        self.cur_path = QFileDialog.getExistingDirectory(self, " Select the music folder ", './')
        if self.cur_path:
            self.showMusicList()
            self.cur_playing_song = ''
            self.startTimeLabel.setText('00:00')
            self.endTimeLabel.setText('00:00')
            self.slider.setSliderPosition(0)
            self.slider.sliderMoved[int].connect(lambda: self.player.setPosition(self.slider.value()))
            self.is_pause = True
            #self.playBtn.setText(' Play ')
    
    def showMusicList(self):
        self.musicList.clear()
        for song in os.listdir(self.cur_path):
            if song.split('.')[-1] in self.song_formats:
                self.songs_list.append([song, os.path.join(self.cur_path, song).replace('\\', '/')])
                self.musicList.addItem(song)
        self.musicList.setCurrentRow(0)
        if self.songs_list:
                self.cur_playing_song = self.songs_list[self.musicList.currentRow()][-1]
    
    def Tips(self, message):
        QMessageBox.about(self, " Tips ", message)
        
    def setCurPlaying(self):
        self.cur_playing_song = self.songs_list[self.musicList.currentRow()][-1]
        self.player.setMedia(QMediaContent(QUrl(self.cur_playing_song)))
    
    def playMusic(self):
        if self.musicList.count() == 0:
                self.Tips(' There is no music file to play in the current path ')
                return
        if not self.player.isAudioAvailable():
                self.setCurPlaying()
        if self.is_pause or self.is_switching:
                self.player.play()
                self.is_pause = False
                self.playBtn.setStyleSheet('border-image: url(mp3_player/pause.png);')
        elif (not self.is_pause) and (not self.is_switching):
                self.player.pause()
                self.is_pause = True
                self.playBtn.setStyleSheet('border-image: url(mp3_player/play.png);')
    
    def prevMusic(self):
        self.slider.setValue(0)
        if self.musicList.count() == 0:
            self.Tips(' There is no music file to play in the current path ')
            return
        pre_row = self.musicList.currentRow()-1 if self.musicList.currentRow() != 0 else self.musicList.count() - 1
        self.musicList.setCurrentRow(pre_row)
        self.is_switching = True
        self.setCurPlaying()
        self.playMusic()
        self.is_switching = False
    
    def nextMusic(self):
        self.slider.setValue(0)
        if self.musicList.count() == 0:
            self.Tips(' There is no music file to play in the current path ')
            return
        next_row = self.musicList.currentRow()+1 if self.musicList.currentRow() != self.musicList.count()-1 else 0
        self.musicList.setCurrentRow(next_row)
        self.is_switching = True
        self.setCurPlaying()
        self.playMusic()
        self.is_switching = False
    
    def doubleClicked(self):
        self.slider.setValue(0)
        self.is_switching = True
        self.setCurPlaying()
        self.playMusic()
        self.is_switching = False

    def playByMode(self):
        if (not self.is_pause) and (not self.is_switching):
            self.slider.setMinimum(0)
            self.slider.setMaximum(self.player.duration())
            self.slider.setValue(self.slider.value() + 1000)
        self.startTimeLabel.setText(time.strftime('%M:%S', time.localtime(self.player.position()/1000)))
        self.endTimeLabel.setText(time.strftime('%M:%S', time.localtime(self.player.duration()/1000)))
        
        if (self.playMode == 0) and (not self.is_pause) and (not self.is_switching):
            if self.musicList.count() == 0:
                return
            if self.player.position() == self.player.duration():
                self.nextMusic()
        
        elif (self.playMode == 1) and (not self.is_pause) and (not self.is_switching):
            if self.musicList.count() == 0:
                return
            if self.player.position() == self.player.duration():
                self.is_switching = True
                self.setCurPlaying()
                self.slider.setValue(0)
                self.playMusic()
                self.is_switching = False
        
        elif (self.playMode == 2) and (not self.is_pause) and (not self.is_switching):
            if self.musicList.count() == 0:
                return
            if self.player.position() == self.player.duration():
                self.is_switching = True
                self.musicList.setCurrentRow(random.randint(0, self.musicList.count()-1))
                self.setCurPlaying()
                self.slider.setValue(0)
                self.playMusic()
                self.is_switching = False
                
    def musicSearch(self):
        if self.searchBar.text() == "":
            self.musicList.clear()
            self.songs_list.clear()
            self.showMusicList()
        elif self.searchBar.text() != "":
            temp_list = []
            self.musicList.clear()
            for count in range(len(self.songs_list)):
                if (self.searchBar.text()).lower() in (self.songs_list[count][0]).lower():
                    self.musicList.addItem(self.songs_list[count][0])
                    temp_list.append(self.songs_list[count])
            self.songs_list.clear()
            self.songs_list = temp_list
    
    def playModeSet(self):
        if self.playMode == 0:
            self.playMode = 1
            self.playModeBtn.setStyleSheet("border-image: url(mp3_player/loop.png)")
        elif self.playMode == 1:
            self.playMode = 2
            self.playModeBtn.setStyleSheet("border-image: url(mp3_player/shuffle.png)")
        elif self.playMode == 2:
            self.playMode = 0
            self.playModeBtn.setStyleSheet("border-image:url(mp3_player/sequence.png)")

app = QApplication(sys.argv)
ex = MP3Player()
sys.exit(app.exec_())