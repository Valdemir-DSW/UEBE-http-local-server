import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction, QFileDialog, QMessageBox, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QWidget, QLabel
from PyQt5.QtGui import QFont
import qdarkstyle
import os
from PyQt5.QtGui import QIcon
from threading import Timer
import shutil
from datetime import datetime
import argparse
class IDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.folder_path = None  # Adicionando o atributo folder_path
        self.backup_folder = None  # Adicionando o atributo backup_folder
        self.backup_timer = None  # Adicionando o atributo backup_timer
        self.folder_stack = []  # Adicionando o histórico de pastas visitadas
        self.backup_info_label = QLabel("Pasta de Backup: Nenhuma pasta configurada", self)  # Adicionando o atributo backup_info_label
        self.load_settings()  # Carrega as configurações ao iniciar a aplicação
        self.initUI()
        try:
            settings_file = "settingasa.ini"
            if os.path.isfile(settings_file):
                with open(settings_file, "r") as file:
                    lines = file.readlines()
                    if len(lines) >= 1:
                        self.folder_path = lines[0].strip()
                        self.update_folder_view()
                        print("oi")
                        
                        
        except:
            pass
    def initUI(self):
        self.setWindowTitle("UEBE - Web IDE")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.text_area = QTextEdit(self)
        self.text_area.setFont(QFont("Consolas", 11))

        self.file_list = QListWidget(self)
        self.file_list.itemClicked.connect(self.load_file)

        self.execute_button = QPushButton("Executar", self)
        self.execute_button.clicked.connect(self.execute_file)
        self.execute_button.setVisible(False)

        self.save_button = QPushButton("Salvar", self)
        self.save_button.clicked.connect(self.save_file)
        self.save_button.setVisible(False)

        self.backup_info_label.setWordWrap(True)  # Configuração do word wrap para o QLabel

        self.backup_button = QPushButton("Ver Pasta de Backup", self)
        self.backup_button.clicked.connect(self.show_backup_folder)

        self.back_button = QPushButton("Voltar", self)  # Botão para voltar à pasta anterior
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setVisible(False)  # Inicialmente invisível até que haja histórico

        layout = QHBoxLayout()
        layout.addWidget(self.file_list)
        layout.addWidget(self.text_area)
        layout.addWidget(self.execute_button)
        layout.addWidget(self.save_button)

        self.central_layout = QVBoxLayout(self.central_widget)
        self.central_layout.addLayout(layout)
        self.central_layout.addWidget(self.backup_info_label)  # Adicionando o QLabel ao layout
        self.central_layout.addWidget(self.backup_button)
        self.central_layout.addWidget(self.back_button)  # Adicionando o botão "Voltar"

        self.statusBar().showMessage("Status: Pronto")

        self.createMenuBar()
        

    def createMenuBar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Arquivo")

        open_folder_action = QAction("Abrir Pasta", self)
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)

        configure_backup_action = QAction("Configurar Pasta de Backup", self)
        configure_backup_action.triggered.connect(self.configure_backup)
        file_menu.addAction(configure_backup_action)

        self.backup_toggle_action = QAction("Ativar Backup Automático", self)
        self.backup_toggle_action.setCheckable(True)
        self.backup_toggle_action.triggered.connect(self.toggle_backup)
        file_menu.addAction(self.backup_toggle_action)

        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.save_and_close)  # Salva as configurações e fecha ao sair
        file_menu.addAction(exit_action)

    def load_settings(self):
        # Carrega as configurações da pasta de backup de um arquivo, se existir
        settings_file = "settings.ini"
        if os.path.isfile(settings_file):
            with open(settings_file, "r") as file:
                lines = file.readlines()
                if len(lines) >= 2:
                    self.folder_path = lines[0].strip()
                    self.backup_folder = lines[1].strip()
                    if self.backup_folder:
                        self.backup_info_label.setText(f"Pasta de Backup: {self.backup_folder}")

    def save_settings(self):
        # Salva as configurações da pasta de backup em um arquivo
        settings_file = "settings.ini"
        with open(settings_file, "w") as file:
            if self.folder_path:
                file.write(f"{self.folder_path}\n")
            if self.backup_folder:
                file.write(f"{self.backup_folder}\n")

    def open_folder(self):
        selected_folder = QFileDialog.getExistingDirectory(self, "Abrir Pasta", "")
        if selected_folder:
            self.folder_path = selected_folder
            self.folder_stack.append(selected_folder)  # Adiciona a pasta ao histórico
            self.update_folder_view()

    def update_folder_view(self):
        if self.folder_path:
            self.file_list.clear()
            for file_name in os.listdir(self.folder_path):
                if os.path.isfile(os.path.join(self.folder_path, file_name)):
                    self.file_list.addItem(file_name)
            self.back_button.setVisible(len(self.folder_stack) > 1)  # Mostra o botão "Voltar" se houver histórico

    def go_back(self):
        if len(self.folder_stack) > 1:
            self.folder_stack.pop()  # Remove a pasta atual do histórico
            self.folder_path = self.folder_stack[-1]  # Retorna à pasta anterior
            self.update_folder_view()

    def load_file(self, item):
        file_name = item.text()
        if file_name and self.folder_path:
            file_path = os.path.join(self.folder_path, file_name)
            if os.path.isfile(file_path):
                if file_name.lower().endswith((".txt", ".py", ".html", ".js", ".php", ".fuzil", ".json", ".ino", ".rubi", ".css", ".java", ".c", ".cpp", ".cs", ".rb", ".swift", ".xml", ".md", ".sql", ".sh", ".yml", ".toml", ".ini", ".bat", ".go", ".pl", ".lua", ".kt", ".rs")):

                    with open(file_path, "r") as file:
                        content = file.read()
                        self.text_area.setPlainText(content)
                    self.execute_button.setVisible(True)
                    self.save_button.setVisible(True)
                else:
                    self.text_area.clear()
                    self.text_area.setPlainText("Desculpe, não podemos exibir este arquivo.")

    def execute_file(self):
        file_name = self.file_list.currentItem().text()
        if file_name and self.folder_path:
            file_path = os.path.join(self.folder_path, file_name)
            if os.path.isfile(file_path):
                try:
                    os.startfile(file_path)
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Erro ao abrir o arquivo: {str(e)}")
            else:
                QMessageBox.warning(self, "Aviso", "O arquivo selecionado não existe.")

    def save_file(self):
        file_name = self.file_list.currentItem().text()
        if file_name and self.folder_path:
            file_path = os.path.join(self.folder_path, file_name)
            content = self.text_area.toPlainText()
            try:
                with open(file_path, "w") as file:
                    file.write(content)
                QMessageBox.information(self, "Sucesso", f"Arquivo {file_name} salvo com sucesso!")
            except Exception as e:
                QMessageBox.critical(self
, "Erro", f"Erro ao salvar o arquivo: {str(e)}")

    def configure_backup(self):
        self.backup_folder = QFileDialog.getExistingDirectory(self, "Configurar Pasta de Backup", "")
        if self.backup_folder:
            self.backup_toggle_action.setEnabled(True)  # Habilita o backup automático se a pasta de backup estiver configurada
            self.backup_info_label.setText(f"Pasta de Backup: {self.backup_folder}")
            self.save_settings()  # Salva a configuração da pasta de backup

    def toggle_backup(self, checked):
        if checked and self.backup_folder:
            self.backup_timer = Timer(300, self.backup_all_files)  # 300 segundos = 5 minutos
            self.backup_timer.start()
        else:
            if self.backup_timer:
                self.backup_timer.cancel()

    def backup_all_files(self):
        if self.folder_path and self.backup_folder:
            if not os.path.exists(self.backup_folder):
                os.makedirs(self.backup_folder)  # Cria a pasta de backup se não existir

            for file_name in os.listdir(self.folder_path):
                if os.path.isfile(os.path.join(self.folder_path, file_name)):
                    file_path = os.path.join(self.folder_path, file_name)
                    backup_file_name = f"{os.path.splitext(file_name)[0]}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}{os.path.splitext(file_name)[1]}"
                    backup_file_path = os.path.join(self.backup_folder, backup_file_name)
                    try:
                        shutil.copy(file_path, backup_file_path)
                    except Exception as e:
                        QMessageBox.critical(self, "Erro", f"Erro ao fazer backup do arquivo: {str(e)}")
            self.backup_timer = Timer(300, self.backup_all_files)
            self.backup_timer.start()


    def show_backup_folder(self):
        if self.backup_folder:
            QMessageBox.information(self, "Pasta de Backup", f"A pasta de backup configurada é: {self.backup_folder}")
        else:
            QMessageBox.warning(self, "Aviso", "Nenhuma pasta de backup está configurada.")

    def save_and_close(self):
        self.save_settings()  # Salva as configurações antes de fechar
        self.close()
    
    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Script description.')
        parser.add_argument('directory', type=str, help='Path to the directory.')
        args = parser.parse_args()
        return args
if __name__ == "__main__":
    
    
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.abspath("icona.ico")))
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    ide = IDE()
    ide.show()
    sys.exit(app.exec_())
