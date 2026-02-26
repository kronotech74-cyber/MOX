#!/usr/bin/env python3
"""
MOX Browser - Aplicación de escritorio basada en PyQt6 + QWebEngineView
Autor: Generado automáticamente desde mox.html
"""

import sys
import os
import re
from urllib.parse import quote_plus, urlparse

from PyQt6.QtCore import (
    Qt, QUrl, QSize, pyqtSlot
)
from PyQt6.QtGui import (
    QIcon, QKeySequence, QShortcut, QColor, QPalette, QFont
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTabWidget, QTabBar, QStatusBar,
    QLabel, QSizePolicy, QFrame, QToolBar, QProgressBar
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage

# ─── Ruta base: donde está este script (o el .exe si usas PyInstaller) ───────
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HOME_HTML = os.path.join(BASE_DIR, 'mox.html')


# ─── Helpers ─────────────────────────────────────────────────────────────────
def smart_url(text: str) -> str:
    """
    Convierte texto en URL:
    - URL válida  → se normaliza con https://
    - Búsqueda   → https://www.google.com/search?q=...
    """
    text = text.strip()
    if not text:
        return ''

    # Si ya tiene esquema (http/https/ftp/file)
    if re.match(r'^[a-zA-Z][a-zA-Z0-9+\-.]*://', text):
        return text

    # Parece dominio (contiene punto y sin espacios, o localhost)
    domain_like = re.match(
        r'^([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}(/.*)?$', text
    ) or text.lower() in ('localhost',)

    if domain_like:
        return 'https://' + text

    # Búsqueda en Google
    return f'https://www.google.com/search?q={quote_plus(text)}'


# ─── WebView personalizado ────────────────────────────────────────────────────
class MoxWebView(QWebEngineView):
    """Vista web individual; redefine createWindow para abrir nuevas pestañas."""

    def __init__(self, browser_window, parent=None):
        super().__init__(parent)
        self._browser = browser_window
        self.loadStarted.connect(self._on_load_started)
        self.loadProgress.connect(self._on_load_progress)
        self.loadFinished.connect(self._on_load_finished)
        self.titleChanged.connect(self._on_title_changed)
        self.urlChanged.connect(self._on_url_changed)

    # Abrir links que piden nueva ventana en nueva pestaña
    def createWindow(self, _type):
        tab = self._browser.add_tab()
        return tab.web_view

    # ── Señales internas ──────────────────────────────────────────────────────
    def _on_load_started(self):
        if self._is_active():
            self._browser.progress_bar.setVisible(True)
            self._browser.progress_bar.setValue(0)

    def _on_load_progress(self, p):
        if self._is_active():
            self._browser.progress_bar.setValue(p)

    def _on_load_finished(self, _ok):
        if self._is_active():
            self._browser.progress_bar.setVisible(False)
            self._browser.update_nav_buttons()

    def _on_title_changed(self, title):
        idx = self._my_tab_index()
        if idx >= 0:
            short = (title[:22] + '…') if len(title) > 24 else title
            self._browser.tabs.setTabText(idx, short or 'Nueva pestaña')
            if self._is_active():
                self._browser.setWindowTitle(f'{title} — MOX')

    def _on_url_changed(self, qurl):
        if self._is_active():
            url_str = qurl.toString()
            if url_str.startswith('file://'):
                self._browser.url_bar.setText('')
                self._browser.url_bar.setPlaceholderText('🏠  Página de inicio MOX')
            else:
                self._browser.url_bar.setText(url_str)

    # ── Utilidades ────────────────────────────────────────────────────────────
    def _is_active(self):
        return self._browser.current_web_view() is self

    def _my_tab_index(self):
        for i in range(self._browser.tabs.count()):
            w = self._browser.tabs.widget(i)
            if hasattr(w, 'web_view') and w.web_view is self:
                return i
        return -1


# ─── Contenedor de pestaña ────────────────────────────────────────────────────
class TabContainer(QWidget):
    def __init__(self, browser_window):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.web_view = MoxWebView(browser_window)
        layout.addWidget(self.web_view)


# ─── Ventana principal ────────────────────────────────────────────────────────
class MoxBrowser(QMainWindow):

    DARK_STYLE = """
        QMainWindow, QWidget {
            background-color: #0c0c0c;
            color: #f2f2f2;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
        }
        QTabWidget::pane {
            border: none;
            background: #0c0c0c;
        }
        QTabBar::tab {
            background: #1a1a1a;
            color: #999;
            border: 1px solid #2a2a2a;
            border-bottom: none;
            border-radius: 8px 8px 0 0;
            padding: 7px 16px;
            min-width: 130px;
            max-width: 190px;
            margin-right: 2px;
            font-size: 12px;
        }
        QTabBar::tab:selected {
            background: #0c0c0c;
            color: #f2f2f2;
            border-bottom-color: #0c0c0c;
        }
        QTabBar::tab:hover:!selected {
            background: #222;
            color: #f2f2f2;
        }
        QTabBar::close-button {
            subcontrol-position: right;
        }
        QToolBar {
            background: #141414;
            border-bottom: 1px solid #2a2a2a;
            spacing: 6px;
            padding: 6px 10px;
        }
        QLineEdit {
            background: #1a1a1a;
            color: #f2f2f2;
            border: 1.5px solid #333;
            border-radius: 20px;
            padding: 6px 16px;
            font-size: 14px;
            selection-background-color: #e53935;
        }
        QLineEdit:focus {
            border-color: #e53935;
        }
        QPushButton {
            background: transparent;
            color: #999;
            border: none;
            border-radius: 16px;
            padding: 6px 10px;
            font-size: 14px;
        }
        QPushButton:hover {
            background: rgba(229,57,53,0.13);
            color: #e53935;
        }
        QPushButton:disabled {
            opacity: 0.3;
            color: #555;
        }
        QPushButton#go-btn {
            background: #e53935;
            color: white;
            font-weight: 600;
            padding: 6px 18px;
            min-width: 60px;
        }
        QPushButton#go-btn:hover {
            background: #ff5252;
            color: white;
        }
        QProgressBar {
            background: #1a1a1a;
            border: none;
            height: 3px;
            max-height: 3px;
        }
        QProgressBar::chunk {
            background: #e53935;
        }
        QStatusBar {
            background: #141414;
            color: #555;
            font-size: 11px;
            border-top: 1px solid #2a2a2a;
        }
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle('MOX Browser')
        self.resize(1280, 820)
        self.setMinimumSize(800, 500)
        self.setStyleSheet(self.DARK_STYLE)
        self._build_ui()
        self._build_shortcuts()
        # Abrir pestaña de inicio
        self.add_tab(home=True)

    # ── Construcción UI ───────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Barra de navegación ──────────────────────────────────────────────
        toolbar = QToolBar('Navegación')
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(18, 18))
        self.addToolBar(toolbar)

        # Botones atrás / adelante / recargar / inicio
        self.btn_back = QPushButton('◀')
        self.btn_back.setToolTip('Atrás  (Alt+←)')
        self.btn_back.setFixedSize(34, 34)
        self.btn_back.clicked.connect(self.go_back)

        self.btn_fwd = QPushButton('▶')
        self.btn_fwd.setToolTip('Adelante  (Alt+→)')
        self.btn_fwd.setFixedSize(34, 34)
        self.btn_fwd.clicked.connect(self.go_forward)

        self.btn_reload = QPushButton('↻')
        self.btn_reload.setToolTip('Recargar  (F5)')
        self.btn_reload.setFixedSize(34, 34)
        self.btn_reload.clicked.connect(self.reload_page)

        self.btn_home = QPushButton('🏠')
        self.btn_home.setToolTip('Inicio  (Ctrl+H)')
        self.btn_home.setFixedSize(34, 34)
        self.btn_home.clicked.connect(self.go_home)

        # Barra de URL / búsqueda
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText('🔍  Busca en Google o escribe una URL…')
        self.url_bar.setClearButtonEnabled(True)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        # Botón Ir
        self.btn_go = QPushButton('Ir')
        self.btn_go.setObjectName('go-btn')
        self.btn_go.setFixedHeight(34)
        self.btn_go.setToolTip('Navegar  (Enter)')
        self.btn_go.clicked.connect(self.navigate_to_url)

        # Nueva pestaña (en barra)
        self.btn_new_tab = QPushButton('＋')
        self.btn_new_tab.setToolTip('Nueva pestaña  (Ctrl+T)')
        self.btn_new_tab.setFixedSize(34, 34)
        self.btn_new_tab.clicked.connect(lambda: self.add_tab(home=True))

        for w in (self.btn_back, self.btn_fwd, self.btn_reload, self.btn_home,
                  self.url_bar, self.btn_go, self.btn_new_tab):
            toolbar.addWidget(w)

        # ── Barra de progreso ────────────────────────────────────────────────
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # ── Pestañas ─────────────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        main_layout.addWidget(self.tabs)

        # ── Barra de estado ──────────────────────────────────────────────────
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    # ── Atajos de teclado ─────────────────────────────────────────────────────
    def _build_shortcuts(self):
        shortcuts = [
            (Qt.Key.Key_F5,                        self.reload_page),
            ('Ctrl+R',                             self.reload_page),
            ('Ctrl+T',                             lambda: self.add_tab(home=True)),
            ('Ctrl+W',                             self._close_current_tab),
            ('Ctrl+H',                             self.go_home),
            ('Ctrl+L',                             self._focus_url_bar),
            ('Alt+Left',                           self.go_back),
            ('Alt+Right',                          self.go_forward),
            ('Ctrl+Tab',                           self._next_tab),
            ('Ctrl+Shift+Tab',                     self._prev_tab),
        ]
        for key, slot in shortcuts:
            sc = QShortcut(QKeySequence(key), self)
            sc.activated.connect(slot)

    # ── Gestión de pestañas ───────────────────────────────────────────────────
    def add_tab(self, url: str = '', home: bool = False) -> TabContainer:
        container = TabContainer(self)
        idx = self.tabs.addTab(container, 'Nueva pestaña')
        self.tabs.setCurrentIndex(idx)

        wv = container.web_view
        # Conectar señal de estado
        wv.page().linkHovered.connect(
            lambda href: self.status_bar.showMessage(href, 2000)
        )

        if home or not url:
            self._load_home(wv)
        else:
            wv.load(QUrl(smart_url(url)))

        return container

    def _load_home(self, wv: MoxWebView = None):
        if wv is None:
            wv = self.current_web_view()
        if wv is None:
            return
        if os.path.exists(HOME_HTML):
            wv.load(QUrl.fromLocalFile(HOME_HTML))
        else:
            wv.setHtml(self._fallback_home_html())

    def _fallback_home_html(self) -> str:
        return """<!DOCTYPE html><html><head><meta charset="UTF-8">
        <style>
          body{background:#0c0c0c;color:#f2f2f2;font-family:'Segoe UI',sans-serif;
               display:flex;align-items:center;justify-content:center;height:100vh;
               flex-direction:column;gap:16px;}
          h1{color:#e53935;font-size:4rem;letter-spacing:-3px;margin:0;}
          p{color:#999;font-size:.9rem;}
        </style></head><body>
        <h1>MOX</h1>
        <p>Archivo mox.html no encontrado en el directorio de la aplicación.</p>
        </body></html>"""

    def close_tab(self, idx: int):
        if self.tabs.count() <= 1:
            self.add_tab(home=True)
        self.tabs.removeTab(idx)

    def _close_current_tab(self):
        self.close_tab(self.tabs.currentIndex())

    def _on_tab_changed(self, idx: int):
        wv = self.current_web_view()
        if wv is None:
            return
        url = wv.url().toString()
        if url.startswith('file://') or not url:
            self.url_bar.setText('')
            self.url_bar.setPlaceholderText('🏠  Página de inicio MOX')
        else:
            self.url_bar.setText(url)
        title = wv.title() or 'MOX Browser'
        self.setWindowTitle(f'{title} — MOX')
        self.update_nav_buttons()

    # ── Navegación ────────────────────────────────────────────────────────────
    @pyqtSlot()
    def navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text:
            return
        url = smart_url(text)
        wv = self.current_web_view()
        if wv:
            wv.load(QUrl(url))

    @pyqtSlot()
    def go_back(self):
        wv = self.current_web_view()
        if wv and wv.history().canGoBack():
            wv.back()

    @pyqtSlot()
    def go_forward(self):
        wv = self.current_web_view()
        if wv and wv.history().canGoForward():
            wv.forward()

    @pyqtSlot()
    def reload_page(self):
        wv = self.current_web_view()
        if wv:
            wv.reload()

    @pyqtSlot()
    def go_home(self):
        self._load_home()

    def update_nav_buttons(self):
        wv = self.current_web_view()
        if wv:
            self.btn_back.setEnabled(wv.history().canGoBack())
            self.btn_fwd.setEnabled(wv.history().canGoForward())

    # ── Tabs helpers ──────────────────────────────────────────────────────────
    def current_web_view(self) -> MoxWebView | None:
        w = self.tabs.currentWidget()
        if isinstance(w, TabContainer):
            return w.web_view
        return None

    def _focus_url_bar(self):
        self.url_bar.setFocus()
        self.url_bar.selectAll()

    def _next_tab(self):
        n = self.tabs.count()
        self.tabs.setCurrentIndex((self.tabs.currentIndex() + 1) % n)

    def _prev_tab(self):
        n = self.tabs.count()
        self.tabs.setCurrentIndex((self.tabs.currentIndex() - 1) % n)


# ─── Entry point ──────────────────────────────────────────────────────────────
def main():
    # Necesario para QWebEngine en algunos sistemas
    os.environ.setdefault('QTWEBENGINE_CHROMIUM_FLAGS', '--no-sandbox')

    app = QApplication(sys.argv)
    app.setApplicationName('MOX Browser')
    app.setApplicationVersion('1.0.0')

    # Fuente por defecto
    font = QFont('Segoe UI', 10)
    app.setFont(font)

    window = MoxBrowser()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()