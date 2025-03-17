# json_formatter.py
import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTextEdit,
                             QPushButton, QHBoxLayout, QVBoxLayout, QLabel,
                             QDialog, QSizeGrip, QStatusBar)
from PyQt5.QtGui import (QFont, QIcon, QPalette, QColor, QMouseEvent,
                        QFontDatabase, QTextCursor)
from PyQt5.QtCore import (Qt, QSize, QPoint, QRect, QEvent)

class CustomDialog(QDialog):
    def __init__(self, parent=None, title='提示', message=''):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.initUI(title, message)

    def initUI(self, title, message):
        # 主容器
        container = QWidget(self)
        container.setMinimumSize(300, 150)
        container.setStyleSheet("""
            QWidget {
                background: #ffffff;
                border-radius: 6px;
                border: 1px solid #d0d7de;
            }
        """)

        # 布局
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("""
            QLabel {
                color: #24292f;
                font: bold 16px 'Microsoft YaHei';
                qproperty-alignment: AlignCenter;
            }
        """)
        
        # 内容
        lbl_message = QLabel(message)
        lbl_message.setStyleSheet("""
            QLabel {
                color: #57606a;
                font: 14px 'Microsoft YaHei';
                qproperty-alignment: AlignCenter;
            }
        """)
        lbl_message.setWordWrap(True)
        
        # 确认按钮
        btn_confirm = QPushButton("确定")
        btn_confirm.setCursor(Qt.PointingHandCursor)
        btn_confirm.setStyleSheet("""
            QPushButton {
                background: #218bff;
                color: white;
                border: 1px solid #d0d7de;
                border-radius: 6px;
                padding: 8px 25px;
                font: 14px 'Microsoft YaHei';
            }
            QPushButton:hover {
                background: #1a73e8;
            }
        """)
        btn_confirm.clicked.connect(self.accept)
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_message)
        layout.addWidget(btn_confirm, alignment=Qt.AlignCenter)
        
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(container)

class JSONFormatter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.mouse_pressed = False
        self.resize_direction = 0
        self.setMouseTracking(True)

    def initUI(self):
        # 窗口设置
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("JSON格式工具")
        self.setMinimumSize(800, 600)
        
        # 设置GitHub风格主题
        self.set_github_theme()
        
        # 主容器
        main_widget = QWidget()
        main_widget.setObjectName("mainWidget")
        main_widget.setStyleSheet("""
            QWidget#mainWidget {
                background: #ffffff;
                border: 1px solid #d0d7de;
            }
        """)
        self.setCentralWidget(main_widget)
        
        # 自定义标题栏
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(32)
        self.title_bar.setStyleSheet("background: #f6f8fa;")
        
        # 标题栏布局
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(12, 0, 12, 0)
        
        # 标题
        self.title_label = QLabel("JSON格式工具")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #24292f;
                font: bold 14px 'Microsoft YaHei';
            }
        """)
        
        # 窗口按钮
        self.btn_min = self.create_title_button("－")
        self.btn_close = self.create_title_button("×")
        
        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_close.clicked.connect(self.close)
        
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.btn_min)
        title_layout.addWidget(self.btn_close)
        
        # 主布局
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.title_bar)
        
        # 功能区域
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(12)
        
        # 按钮布局
        btn_layout = QHBoxLayout()
        self.btn_format = self.create_main_button("格式化", "#218bff")
        self.btn_compress = self.create_main_button("压缩", "#2da44e")
        self.btn_validate = self.create_main_button("验证", "#bf8700")
        self.btn_escape = self.create_main_button("转义", "#cf222e")
        self.btn_undo = self.create_main_button("撤销", "#6e7781")
        
        btn_layout.addWidget(self.btn_format)
        btn_layout.addWidget(self.btn_compress)
        btn_layout.addWidget(self.btn_validate)
        btn_layout.addWidget(self.btn_escape)
        btn_layout.addWidget(self.btn_undo)
        btn_layout.addStretch()
        
        # 文本编辑框
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("在此粘贴JSON内容...")
        self.text_edit.setAcceptRichText(False)  # 禁用富文本
        self.text_edit.setUndoRedoEnabled(True)  # 启用撤销重做
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background: #ffffff;
                border: 1px solid #d0d7de;
                border-radius: 6px;
                padding: 12px;
                color: #24292f;
                font: 14px 'Consolas';
                selection-background-color: #218bff;
                selection-color: white;
            }
        """)
        
        content_layout.addLayout(btn_layout)
        content_layout.addWidget(self.text_edit, 1)
        
        main_layout.addWidget(content_widget, 1)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background: #f6f8fa;
                border-top: 1px solid #d0d7de;
                color: #57606a;
                font: 12px 'Microsoft YaHei';
            }
        """)
        self.setStatusBar(self.status_bar)
        
        # 连接信号
        self.btn_format.clicked.connect(self.format_json)
        self.btn_compress.clicked.connect(self.compress_json)
        self.btn_validate.clicked.connect(self.validate_json)
        self.btn_escape.clicked.connect(self.escape_json)
        self.btn_undo.clicked.connect(self.text_edit.undo)

    def create_title_button(self, text):
        btn = QPushButton(text)
        btn.setFixedSize(28, 24)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #57606a;
                font: bold 18px 'Microsoft YaHei';
                border-radius: 4px;
            }
            QPushButton:hover {
                background: rgba(27,31,36,0.1);
            }
        """)
        return btn

    def create_main_button(self, text, color):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: white;
                border: 1px solid rgba(27,31,36,0.15);
                border-radius: 6px;
                padding: 6px 12px;
                font: 14px 'Microsoft YaHei';
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: {self.darken_color(color)};
                border-color: rgba(27,31,36,0.3);
            }}
        """)
        return btn

    def set_github_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.WindowText, QColor(36, 41, 47))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(36, 41, 47))
        self.setPalette(palette)

    def darken_color(self, hex_color, factor=0.9):
        color = QColor(hex_color)
        darker_color = color.darker(int(100 * (2 - factor)))
        return darker_color.name()  # 返回颜色字符串

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = True
            self.start_pos = event.globalPos()
            self.start_geometry = self.geometry()

    def mouseMoveEvent(self, event: QMouseEvent):
        # 窗口缩放处理
        if not self.mouse_pressed:
            pos = self.mapFromGlobal(event.globalPos())
            margin = 8
            rect = self.rect()
            self.resize_direction = 0
            
            # 转换为整数进行位运算
            if pos.x() <= margin:
                self.resize_direction |= int(Qt.LeftEdge)
            if pos.x() >= rect.width() - margin:
                self.resize_direction |= int(Qt.RightEdge)
            if pos.y() <= margin:
                self.resize_direction |= int(Qt.TopEdge)
            if pos.y() >= rect.height() - margin:
                self.resize_direction |= int(Qt.BottomEdge)
            
            # 使用整数进行判断
            if self.resize_direction & (int(Qt.LeftEdge) | int(Qt.TopEdge)) or \
               self.resize_direction & (int(Qt.RightEdge) | int(Qt.BottomEdge)):
                self.setCursor(Qt.SizeFDiagCursor)
            elif self.resize_direction & (int(Qt.RightEdge) | int(Qt.TopEdge)) or \
                 self.resize_direction & (int(Qt.LeftEdge) | int(Qt.BottomEdge)):
                self.setCursor(Qt.SizeBDiagCursor)
            elif self.resize_direction & (int(Qt.LeftEdge) | int(Qt.RightEdge)):
                self.setCursor(Qt.SizeHorCursor)
            elif self.resize_direction & (int(Qt.TopEdge) | int(Qt.BottomEdge)):
                self.setCursor(Qt.SizeVerCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
            return


        if self.resize_direction != 0:  # 缩放窗口
            delta = event.globalPos() - self.start_pos
            geo = self.start_geometry

            if self.resize_direction & Qt.LeftEdge:
                geo.setLeft(geo.left() + delta.x())
            if self.resize_direction & Qt.TopEdge:
                geo.setTop(geo.top() + delta.y())
            if self.resize_direction & Qt.RightEdge:
                geo.setRight(geo.right() + delta.x())
            if self.resize_direction & Qt.BottomEdge:
                geo.setBottom(geo.bottom() + delta.y())

            self.setGeometry(geo.normalized())
        else:  # 移动窗口
            delta = event.globalPos() - self.start_pos
            self.move(self.pos() + delta)
            self.start_pos = event.globalPos()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.mouse_pressed = False
        self.resize_direction = 0
        self.setCursor(Qt.ArrowCursor)

    def show_message(self, title, message):
        dialog = CustomDialog(self, title, message)
        dialog.exec_()

    def format_json(self):
        try:
            data = json.loads(self.text_edit.toPlainText())
            formatted = json.dumps(data, indent=4, ensure_ascii=False)
            self.text_edit.setPlainText(formatted)
            self.status_bar.showMessage("格式化成功", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"格式化失败：{str(e)}", 5000)

    def compress_json(self):
        try:
            data = json.loads(self.text_edit.toPlainText())
            compressed = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
            self.text_edit.setPlainText(compressed)
            self.status_bar.showMessage("压缩成功", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"压缩失败：{str(e)}", 5000)

    def validate_json(self):
        try:
            json.loads(self.text_edit.toPlainText())
            self.status_bar.showMessage("✅ JSON验证通过", 5000)
        except Exception as e:
            self.status_bar.showMessage(f"❌ JSON验证失败：{str(e)}", 5000)

    def escape_json(self):
        try:
            text = self.text_edit.toPlainText()
            escaped = text.replace('\\', '\\\\').replace('"', '\\"')
            self.text_edit.setPlainText(escaped)
            self.status_bar.showMessage("转义完成", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"转义失败：{str(e)}", 5000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei", 10))
    window = JSONFormatter()
    window.show()
    sys.exit(app.exec_())