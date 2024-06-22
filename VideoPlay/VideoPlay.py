import os
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSlider, QListWidget, QVBoxLayout, QWidget, QPushButton


class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music Player")
        self.setWindowIcon(QIcon("icon.png"))
        self.resize(800, 600)

        self.current_song = None
        self.playing = False

        self.song_list_view = QListWidget()
        self.song_list_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.current_song_label = QLabel()
        self.current_song_label.setAlignment(Qt.AlignCenter)
        self.current_song_label.setPixmap(QPixmap("default.jpg"))

        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setEnabled(False)

        self.play_button = QPushButton()
        self.play_button.setIcon(QIcon("play.png"))
        self.play_button.clicked.connect(self.play_or_pause)

        layout = QVBoxLayout()
        layout.addWidget(self.song_list_view)
        layout.addWidget(self.current_song_label)
        layout.addWidget(self.progress_slider)
        layout.addWidget(self.play_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.player = QMediaPlayer()
        self.player.stateChanged.connect(self.update_playback_state)

        self.load_song_list()

    def load_song_list(self):
        song_list = os.listdir("video")
        self.song_list_view.clear()
        self.song_list_view.addItems(song_list)
        self.song_list_view.itemDoubleClicked.connect(self.play_song)

    def play_song(self, item):
        song_name = item.text()
        if self.current_song:
            self.player.stop()
            self.current_song = None
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile("video/{}".format(song_name))))
        self.current_song = song_name
        self.player.play()
        self.playing = True
        self.current_song_label.setPixmap(QPixmap("video/{}.jpg".format(song_name.split(".")[0])))
        self.setWindowTitle("Music Player - {}".format(song_name.split(".")[0]))
        self.play_button.setIcon(QIcon("pause.png"))  # 更新播放按钮的图标为暂停图标

    def stop_song(self):
        self.player.stop()
        self.current_song = None
        self.playing = False
        self.current_song_label.setPixmap(QPixmap("default.jpg"))
        self.setWindowTitle("Music Player")
        self.play_button.setIcon(QIcon("play.png"))  # 更新播放按钮的图标为播放图标

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            if self.current_song:
                if self.playing:
                    self.player.pause()
                    self.playing = False
                    self.play_button.setIcon(QIcon("play.png"))  # 更新播放按钮的图标为播放图标
                else:
                    self.player.play()
                    self.playing = True
                    self.play_button.setIcon(QIcon("pause.png"))  # 更新播放按钮的图标为暂停图标

    def play_or_pause(self):
        if self.current_song:
            if self.playing:
                self.player.pause()
                self.playing = False
                self.play_button.setIcon(QIcon("play.png"))  # 更新播放按钮的图标为播放图标
            else:
                self.player.play()
                self.playing = True
                self.play_button.setIcon(QIcon("pause.png"))  # 更新播放按钮的图标为暂停图标

    def update_playback_state(self, state):
        if state == QMediaPlayer.PlayingState:
            self.playing = True
            self.setWindowTitle("Music Player - Playing")
        elif state == QMediaPlayer.PausedState:
            self.playing = False
            self.setWindowTitle("Music Player - Paused")
        elif state == QMediaPlayer.StoppedState:
            self.playing = False
            self.setWindowTitle("Music Player")

    def closeEvent(self, event):
        self.player.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication([])
    player = MusicPlayer()
    player.show()
    app.exec()