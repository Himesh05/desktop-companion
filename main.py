import sys
import random

from PyQt6.QtWidgets import QApplication, QLabel, QMenu
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QPixmap

import pyautogui
import math

import pygetwindow as gw


class Companion(QLabel):
    def __init__(self):
        super().__init__()

        # Load slime image
        pixmap = QPixmap("assets/slime.png")

        pixmap = pixmap.scaled(
            150,
            150,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.setPixmap(pixmap)

        # Window settings
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Dragging
        self.drag_pos = None

        # Animation state
        self.is_bouncing = False

        # Behavior timer
        self.behavior_timer = QTimer()
        self.behavior_timer.timeout.connect(self.choose_behavior)

        # First random action in 5–15 sec
        self.behavior_timer.start(random.randint(5000, 15000))

        # Cursor awareness timer
        self.cursor_timer = QTimer()
        self.cursor_timer.timeout.connect(self.check_cursor)
        self.cursor_timer.start(200)

        self.cursor_near = False

        # Speech bubble
        self.speech = QLabel("", None)

        self.speech.setStyleSheet("""
            background-color: white;
            border: 2px solid black;
            border-radius: 10px;
            padding: 5px;
        """)

        self.speech.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )

        self.speech.hide()

        self.current_app = ""

        self.app_timer = QTimer()
        self.app_timer.timeout.connect(self.check_active_window)
        self.app_timer.start(2000)

        self.following_cursor = False

        self.follow_timer = QTimer()
        self.follow_timer.timeout.connect(self.follow_cursor)
        self.follow_timer.start(30)

    # ==========================
    # Mouse Events
    # ==========================

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

        elif event.button() == Qt.MouseButton.RightButton:

            menu = QMenu()

            exit_action = QAction("Exit", self)
            exit_action.triggered.connect(QApplication.quit)

            menu.addAction(exit_action)

            menu.exec(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):

        if self.drag_pos:

            delta = event.globalPosition().toPoint() - self.drag_pos

            self.move(self.pos() + delta)

            self.drag_pos = event.globalPosition().toPoint()

    # ==========================
    # Behavior System
    # ==========================

    def choose_behavior(self):

        action = random.choice(["idle", "bounce"])

        print(f"Mochi decided to: {action}")
        if action == "bounce":

            self.start_bounce()

            self.speak(
                random.choice(
                    [
                        "Feeling energetic.",
                        "Just stretching.",
                        "A little jump.",
                        "Nothing to see here.",
                    ]
                )
            )

        # Schedule next decision
        self.behavior_timer.start(random.randint(5000, 15000))

    # ==========================
    # Bounce Animation
    # ==========================

    def start_bounce(self):

        if self.is_bouncing:
            return

        self.is_bouncing = True

        self.original_y = self.y()
        self.bounce_count = 0

        self.bounce_timer = QTimer()
        self.bounce_timer.timeout.connect(self.bounce)
        self.bounce_timer.start(20)

    def bounce(self):

        x = self.x()
        y = self.y()

        if self.bounce_count < 20:

            self.move(x, y - 3)

        elif self.bounce_count < 40:

            self.move(x, y + 3)

        else:

            self.move(x, self.original_y)

            self.bounce_timer.stop()

            self.is_bouncing = False

            return

        self.bounce_count += 1

    def check_cursor(self):

        mouse_x, mouse_y = pyautogui.position()

        slime_x = self.x() + self.width() // 2
        slime_y = self.y() + self.height() // 2

        distance = math.sqrt((mouse_x - slime_x) ** 2 + (mouse_y - slime_y) ** 2)

        if distance < 150:

            if not self.cursor_near:

                self.cursor_near = True

                messages = [
                    "Hello.",
                    "Oh, it's you.",
                    "Nice to see you.",
                    "I'm watching.",
                ]

                self.speak(random.choice(messages))

                self.following_cursor = True

        else:

            self.cursor_near = False
            self.following_cursor = False

    def speak(self, message):

        self.speech.setText(message)

        self.speech.adjustSize()

        bubble_x = self.x()
        bubble_y = self.y() - 50

        self.speech.move(bubble_x, bubble_y)

        self.speech.show()

        QTimer.singleShot(3000, self.speech.hide)

    def check_active_window(self):

        try:

            active_window = gw.getActiveWindow()

            if not active_window:
                return

            title = active_window.title

            if title != self.current_app:

                self.current_app = title

                print("Current Window:", title)

                self.react_to_window(title)

        except:
            pass

    def react_to_window(self, title):

        title = title.lower()

        if "youtube" in title:

            self.speak(
                random.choice(
                    ["What are we watching?", "Movie time?", "This looks interesting."]
                )
            )

        elif "spotify" in title:

            self.speak(
                random.choice(["Music again?", "Nice choice.", "I like this one."])
            )

        elif "chrome" in title:

            self.speak(
                random.choice(["Browsing?", "Looking for something?", "Another tab?"])
            )

        elif "code" in title:

            self.speak(
                random.choice(
                    ["Building something?", "Working hard?", "Lots of code today."]
                )
            )

    def follow_cursor(self):

        if not self.following_cursor:
            return

        mouse_x, mouse_y = pyautogui.position()

        slime_x = self.x() + self.width() // 2
        slime_y = self.y() + self.height() // 2

        dx = mouse_x - slime_x
        dy = mouse_y - slime_y

        distance = math.sqrt(dx * dx + dy * dy)

        print("Distance:", distance)

        if distance < 80:
            self.following_cursor = False
            return

        speed = 4

        move_x = dx / distance * speed
        move_y = dy / distance * speed

        self.move(
            int(self.x() + move_x),
            int(self.y() + move_y)
        )

# ==========================
# Main
# ==========================

app = QApplication(sys.argv)

companion = Companion()

companion.move(500, 300)

companion.show()

sys.exit(app.exec())
