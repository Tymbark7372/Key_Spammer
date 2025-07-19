import sys
import threading
import time
import random
from pynput.keyboard import Controller, Key
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class KeySpammer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('KeySpammer')
        self.setFixedSize(500, 320)
        self.keyboard = Controller()
        self.spamming = False
        self.thread = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel('KeySpammer')
        title.setFont(QFont('Segoe UI', 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        credit = QLabel('Made by Tymbark7372')
        credit.setFont(QFont('Segoe UI', 10, QFont.Weight.Normal))
        credit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credit.setObjectName('creditLabel')
        layout.addWidget(credit)

        key_layout = QHBoxLayout()
        key_label = QLabel('Key:')
        key_label.setFont(QFont('Segoe UI', 12))
        self.key_combo = QComboBox()
        self.key_combo.setFont(QFont('Segoe UI', 12))
        # --- CHANGE THE KEYS TO SPAM HERE ---
        for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            self.key_combo.addItem(c)
        for d in '0123456789':
            self.key_combo.addItem(d)
        for i in range(1, 13):
            self.key_combo.addItem(f'F{i}')
        special_keys = [
            'Shift', 'Ctrl', 'Alt', 'Space', 'Enter', 'Tab', 'Esc', 'Backspace', 'Delete', 'Insert',
            'CapsLock', 'Cmd', 'Win', 'Menu', 'Home', 'End', 'PageUp', 'PageDown',
            'Left', 'Right', 'Up', 'Down'
        ]
        for k in special_keys:
            self.key_combo.addItem(k)
        self.key_combo.setCurrentText('Shift')
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.key_combo)
        layout.addLayout(key_layout)

        mode_layout = QHBoxLayout()
        mode_label = QLabel('Mode:')
        mode_label.setFont(QFont('Segoe UI', 12))
        self.mode_combo = QComboBox()
        self.mode_combo.setFont(QFont('Segoe UI', 12))
        self.mode_combo.addItems(['Fixed', 'Randomized'])
        self.mode_combo.currentIndexChanged.connect(self.update_mode_ui)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        speed_layout = QHBoxLayout()
        speed_label = QLabel('Speed (ms):')
        speed_label.setFont(QFont('Segoe UI', 12))
        self.speed_input = QLineEdit()
        self.speed_input.setFont(QFont('Segoe UI', 12))
        self.speed_input.setText('100')
        self.speed_input.setFixedWidth(80)
        self.speed_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.speed_input.setPlaceholderText('ms')
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_input)
        layout.addLayout(speed_layout)

        rand_layout = QHBoxLayout()
        self.min_label = QLabel('Min (ms):')
        self.min_label.setFont(QFont('Segoe UI', 12))
        self.min_input = QLineEdit()
        self.min_input.setFont(QFont('Segoe UI', 12))
        self.min_input.setText('10')
        self.min_input.setFixedWidth(80)
        self.min_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.min_input.setPlaceholderText('10')
        self.max_label = QLabel('Max (ms):')
        self.max_label.setFont(QFont('Segoe UI', 12))
        self.max_input = QLineEdit()
        self.max_input.setFont(QFont('Segoe UI', 12))
        self.max_input.setText('1000')
        self.max_input.setFixedWidth(80)
        self.max_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.max_input.setPlaceholderText('1000')
        rand_layout.addWidget(self.min_label)
        rand_layout.addWidget(self.min_input)
        rand_layout.addWidget(self.max_label)
        rand_layout.addWidget(self.max_input)
        layout.addLayout(rand_layout)
        self.min_input.hide()
        self.max_input.hide()
        self.min_label.hide()
        self.max_label.hide()
        self.rand_widgets = [self.min_input, self.max_input, self.min_label, self.max_label]

        hotkey_layout = QHBoxLayout()
        hotkey_label = QLabel('Toggle Hotkey:')
        hotkey_label.setFont(QFont('Segoe UI', 12))
        self.hotkey_combo = QComboBox()
        self.hotkey_combo.setFont(QFont('Segoe UI', 12))
        # --- CHANGE THE TOGGLE HOTKEYS HERE ---
        for i in range(1, 13):
            self.hotkey_combo.addItem(f'F{i}')
        self.hotkey_combo.setCurrentText('F8')
        hotkey_layout.addWidget(hotkey_label)
        hotkey_layout.addWidget(self.hotkey_combo)
        layout.addLayout(hotkey_layout)

        self.toggle_btn = QPushButton('Start Spamming')
        self.toggle_btn.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))
        self.toggle_btn.clicked.connect(self.toggle_spam)
        layout.addWidget(self.toggle_btn)

        self.setLayout(layout)
        self.apply_qss_theme()
        self.listener_thread = threading.Thread(target=self.listen_hotkey, daemon=True)
        self.listener_thread.start()

    def apply_qss_theme(self):
        self.setStyleSheet('''
            QWidget { background-color: #181020; color: #ba68c8; }
            QLabel { color: #ba68c8; }
            QLabel#creditLabel { color: rgba(186, 104, 200, 120); }
            QComboBox, QLineEdit, QPushButton { background-color: #2c2038; color: #ba68c8; border-radius: 8px; border: 1px solid #7b1fa2; }
            QPushButton { padding: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #7b1fa2; color: #fff; }
            QComboBox QAbstractItemView { background-color: #2c2038; color: #ba68c8; selection-background-color: #7b1fa2; selection-color: #fff; }
            QLineEdit:focus { border: 1.5px solid #ba68c8; background: #241028; color: #fff; }
        ''')

    def update_mode_ui(self):
        mode = self.mode_combo.currentText()
        if mode == 'Fixed':
            self.speed_input.show()
            for w in self.rand_widgets:
                w.hide()
        else:
            self.speed_input.hide()
            for w in self.rand_widgets:
                w.show()

    def get_selected_key(self):
        key = self.key_combo.currentText().strip()
        special_keys = {
            'Shift': Key.shift,
            'Ctrl': Key.ctrl,
            'Alt': Key.alt,
            'Space': Key.space,
            'Enter': Key.enter,
            'Tab': Key.tab,
            'Esc': Key.esc,
            'Escape': Key.esc,
            'Backspace': Key.backspace,
            'Delete': Key.delete,
            'Insert': Key.insert,
            'CapsLock': Key.caps_lock,
            'Caps_Lock': Key.caps_lock,
            'Cmd': Key.cmd,
            'Win': Key.cmd,
            'Windows': Key.cmd,
            'Menu': Key.menu,
            'Home': Key.home,
            'End': Key.end,
            'PageUp': Key.page_up,
            'PageDown': Key.page_down,
            'Left': Key.left,
            'Right': Key.right,
            'Up': Key.up,
            'Down': Key.down,
        }
        if key.startswith('F') and key[1:].isdigit():
            fnum = int(key[1:])
            if 1 <= fnum <= 12:
                return getattr(Key, f'f{fnum}')
        if key in special_keys:
            return special_keys[key]
        elif len(key) == 1 and key.isalpha():
            return key.lower()
        elif len(key) == 1 and key.isdigit():
            return key
        else:
            return key

    def get_speed(self):
        mode = self.mode_combo.currentText()
        if mode == 'Fixed':
            try:
                value = int(self.speed_input.text())
                if value < 1:
                    return 1
                return value
            except ValueError:
                return 100
        else:
            try:
                min_val = int(self.min_input.text())
                max_val = int(self.max_input.text())
                if min_val < 1:
                    min_val = 1
                if max_val < min_val:
                    max_val = min_val
                return random.randint(min_val, max_val)
            except ValueError:
                return 100

    def get_hotkey(self):
        return self.hotkey_combo.currentText().strip()

    def spam_key(self):
        key = self.get_selected_key()
        while self.spamming:
            self.keyboard.press(key)
            self.keyboard.release(key)
            time.sleep(self.get_speed() / 1000.0)

    def toggle_spam(self):
        if not self.spamming:
            self.spamming = True
            self.toggle_btn.setText('Stop Spamming')
            self.thread = threading.Thread(target=self.spam_key, daemon=True)
            self.thread.start()
        else:
            self.spamming = False
            self.toggle_btn.setText('Start Spamming')

    def listen_hotkey(self):
        from pynput import keyboard
        def on_press(key):
            try:
                pressed = None
                if hasattr(key, 'char') and key.char:
                    pressed = key.char.upper()
                elif hasattr(key, 'name') and key.name:
                    if key.name.upper().startswith('F') and key.name[1:].isdigit():
                        pressed = key.name.upper()
                    else:
                        pressed = key.name.capitalize()
                else:
                    pressed = str(key).replace('Key.', '').capitalize()
                if pressed == self.get_hotkey():
                    self.toggle_spam()
            except Exception:
                pass
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

    def closeEvent(self, event):
        self.spamming = False
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = KeySpammer()
    window.show()
    sys.exit(app.exec()) 