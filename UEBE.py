import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QHBoxLayout, QComboBox, QLineEdit, QMainWindow, QTextEdit, QProgressBar
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from http.server import SimpleHTTPRequestHandler, HTTPServer
import socket
import qdarkstyle
from PyQt5.QtGui import QIcon
import threading
from PyQt5.QtCore import QUrl, QDateTime,QTimer
import webbrowser
import subprocess
class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('.php'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            result = self.run_php(self.path[1:])
            self.wfile.write(result.encode())
        else:
            super().do_GET()

    def run_php(self, filename):
        port = self.server.server_port
        return self.execute_command(f'php {filename}')

    @staticmethod
    def execute_command(command):
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout

class ServerThread(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)
        self.server = server

    def run(self):
        self.server.serve_forever()

class ServerControl(QWidget):
    def __init__(self):
        super().__init__()
        self.server = None
        self.port = 8000  # Porta padrão
        self.root_directory = os.getcwd()  # Diretório raiz padrão
        self.index_file = 'index.html'  # Arquivo de indexação padrão
        self.timeout = 60  # Tempo limite do servidor em segundos
        self.initUI()
        self.browser_window = None 

    def initUI(self):
        self.setWindowTitle('UEBE - Configurações do Servidor')
        layout = QVBoxLayout()

        # Configuração da Porta
        port_label = QLabel('Porta Padrão:')
        self.port_combo = QComboBox()
        self.port_combo.addItems(['8000', '8080', '8888'])  # Opções de porta
        self.port_combo.setCurrentText(str(self.port))
        layout.addWidget(port_label)
        layout.addWidget(self.port_combo)

        # Configuração do Diretório Raiz
        root_dir_layout = QHBoxLayout()
        self.root_dir_label = QLabel('Diretório Raiz:')
        self.root_dir_edit = QLineEdit()
        self.root_dir_edit.setText(self.root_directory)
        root_dir_layout.addWidget(self.root_dir_label)
        root_dir_layout.addWidget(self.root_dir_edit)
        self.select_dir_button = QPushButton('Selecionar')
        self.select_dir_button.clicked.connect(self.select_root_directory)
        root_dir_layout.addWidget(self.select_dir_button)
        layout.addLayout(root_dir_layout)

        # Configuração do Arquivo de Indexação
        index_file_label = QLabel('Arquivo de Indexação:')
        self.index_file_edit = QLineEdit()
        self.index_file_edit.setText(self.index_file)
        layout.addWidget(index_file_label)
        layout.addWidget(self.index_file_edit)
        
        self.start_buttonide = QPushButton('Editar site na IDE')
        self.start_buttonide.clicked.connect(self.start_ide)
        self.start_buttonide.setEnabled(False)
        layout.addWidget(self.start_buttonide)

        self.start_button = QPushButton('Iniciar Servidor')
        self.start_button.clicked.connect(self.start_server)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Parar Servidor')
        self.stop_button.clicked.connect(self.stop_server)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        self.status_label = QLabel('Status: Servidor não iniciado')
        layout.addWidget(self.status_label)

        self.open_button = QPushButton('Abrir no Navegador')
        self.open_button.clicked.connect(self.open_browser)
        layout.addWidget(self.open_button)


        self.load_button = QPushButton('Carregar Configurações')
        self.load_button.clicked.connect(self.load_settings)
        layout.addWidget(self.load_button)

        self.save_button = QPushButton('Salvar Configurações')
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.command_line_edit = QLineEdit()
        layout.addWidget(self.command_line_edit)

        self.send_command_button = QPushButton('Enviar Comando')
        self.send_command_button.clicked.connect(self.send_command)
        layout.addWidget(self.send_command_button)


        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        self.open_buttona = QPushButton('Sobre o uso de outras linguagens')
        self.open_buttona.clicked.connect(self.open_browser2)
        layout.addWidget(self.open_buttona)

        self.setLayout(layout)
        self.show()

    def start_server(self):
        if not self.server:
            self.port = int(self.port_combo.currentText())
            self.root_directory = self.root_dir_edit.text()
            self.index_file = self.index_file_edit.text()

            os.chdir(self.root_directory)  # Mudar para o diretório raiz
            self.server = HTTPServer(('', self.port), MyHandler)
            self.server.timeout = self.timeout
            self.server_thread = ServerThread(self.server)
            self.server_thread.start()
            self.status_label.setText('Status: Servidor rodando em http://{}:{}'.format(socket.gethostname(), self.port))
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.log('Servidor iniciado.')
            settings_file = "settingasa.ini"
            with open(settings_file, "w") as file:
                if self.root_directory:
                    file.write(f"{self.root_directory}\n")
                    self.start_buttonide.setEnabled(True)

    def start_ide(self):

        os.startfile(os.path.abspath("ideE.exe"))

    
    def select_root_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Selecione o Diretório Raiz')
        if directory:
            self.root_directory = directory
            self.root_dir_edit.setText(self.root_directory)
    def stop_server(self):
        if self.server:
            self.server.shutdown()
            self.server_thread.join()
            self.server = None
            self.status_label.setText('Status: Servidor parado')
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.log('Servidor parado.')

    def open_browser(self):
        self.browser_window = QMainWindow()
        self.browser_window.setWindowTitle('UEBE - Mini Navegador')
        layout = QVBoxLayout()

        self.web_view = QWebEngineView()
        self.web_view.load(QUrl(f'http://127.0.0.1:{self.port}/{self.index_file}'))
        layout.addWidget(self.web_view)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.reload_button = QPushButton('Recarregar Página')
        self.reload_button.clicked.connect(self.reload_page)
        layout.addWidget(self.reload_button)
        
        self.reload_buttona = QPushButton('Abrir no navegador do computador')
        self.reload_buttona.clicked.connect(self.gitpage)
        layout.addWidget(self.reload_buttona)
        

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.browser_window.setCentralWidget(central_widget)
        self.web_view.loadProgress.connect(self.update_progress) 
        self.browser_window.show()

    def open_browser2(self):
        
        webbrowser.open(os.path.abspath("php.html")) 

    def gitpage(self):
        webbrowser.open(f'http://127.0.0.1:{self.port}/{self.index_file}')

    def send_command(self):
        command = self.command_line_edit.text()
        if command:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f'Comando enviado e executado com sucesso: {command}')
            else:
                self.log(f'Erro ao executar o comando: {result.stderr}')
            self.command_line_edit.clear()
        else:
            self.log('Nenhum comando inserido.')
    def update_progress(self, progress):
        self.progress_bar.setValue(progress) 
    def reload_page(self):
         self.web_view.reload()
         self.log('Página recarregada no Mini Navegador.')



    def log(self, message):
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        log_message = f"{current_time}: {message}"
        self.log_text.append(log_message)
        QApplication.processEvents()  # Atualiza a interface para exibir o log imediatamente

    def load_settings(self):
        documentos_dir = os.path.expanduser("~/Documents")
        file_path, _ = QFileDialog.getOpenFileName(self, 'Carregar Configurações', documentos_dir, 'Arquivo de configuração Fuzil (*.fuzil)')
        if file_path:
            with open(file_path, 'r') as file:
                settings = json.load(file)
                self.port = settings.get('port', self.port)
                self.root_directory = settings.get('root_directory', self.root_directory)
                self.index_file = settings.get('index_file', self.index_file)
                self.timeout = settings.get('timeout', self.timeout)
                self.update_ui()

    def save_settings(self):
        settings = {
            'port': self.port,
            'root_directory': self.root_directory,
            'index_file': self.index_file,
            'timeout': self.timeout
        }
        documentos_dir = os.path.expanduser("~/Documents/Salvada.Fuzil")
        file_path, _ = QFileDialog.getSaveFileName(self, 'Salvar Configurações', documentos_dir, 'Arquivo de configuração Fuzil (*.fuzil)')
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(settings, file)
            self.log('Configurações salvas.')

    def update_ui(self):
        self.port_combo.setCurrentText(str(self.port))
        self.root_dir_edit.setText(self.root_directory)
        self.index_file_edit.setText(self.index_file)
        self.log('Configurações carregadas.')

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.abspath("icona.ico")))
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = ServerControl()
    sys.exit(app.exec_())
