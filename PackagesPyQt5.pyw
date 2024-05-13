import sys
import os
import json
import zipfile
from PyQt5.QtWidgets import (
    QApplication, 
    QTreeWidget, 
    QTreeWidgetItem, 
    QMainWindow, 
    QVBoxLayout, 
    QWidget, 
    QPushButton, 
    QFileDialog, 
    QLabel,
    QTableWidget,
    QTableWidgetItem
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class PackageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Styling for the tree widget
        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabels(["Package File"])
        self.tree.itemExpanded.connect(self.loadPackages)
        self.tree.setStyleSheet("""
            QTreeWidget::item {
                border-bottom: 1px solid #d3d3d3;
                border-top: 1px solid #d3d3d3;
            }
            QTreeView {
                show-decoration-selected: 0;
                alternate-background-color: #e8e8e8;
            }
            QTreeWidget::item:hover {
                background-color: #f5f5f5;
            }
            QTreeView::item:selected {
                border: none;
                background-color: #3a99d9;
                color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border-style: none;
                border-bottom: 1px solid #d3d3d3;
                border-right: 1px solid #d3d3d3;
            }
            QTableWidget {
                gridline-color: #d3d3d3;
            }
        """)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)

        self.welcomeLabel = QLabel("Welcome! Please load a ZIP file containing A360 package files.")
        self.welcomeLabel.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(self.welcomeLabel)
        layout.addSpacing(20)

        layout.addWidget(self.tree)
        self.tree.hide()

        self.loadButton = QPushButton("Load ZIP File")
        self.loadButton.setFont(QFont("Arial", 10, QFont.Bold))
        self.loadButton.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border-radius: 5px;
                padding: 10px;
                border: 2px solid #0056b3;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #00449e;
            }
        """)
        self.loadButton.clicked.connect(self.loadZipFile)
        layout.addWidget(self.loadButton)
        layout.addSpacing(20)

        self.errorLabel = QLabel()
        self.errorLabel.setStyleSheet("color: red;")
        layout.addWidget(self.errorLabel)

        self.setGeometry(300, 300, 600, 450)
        self.setWindowTitle('Package Viewer')

    def loadZipFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a ZIP file", "", "ZIP Files (*.zip)")
        if file_path:
            self.processZipFile(file_path)
            self.tree.show()
            self.welcomeLabel.hide()

    def processZipFile(self, file_path):
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                valid_file_found = False
                for file_info in zip_ref.infolist():
                    if not file_info.is_dir():
                        file_name, file_extension = os.path.splitext(file_info.filename)
                        if not file_extension:
                            valid_file_found = True
                            break

                if not valid_file_found:
                    self.errorLabel.setText("Error: No suitable files without an extension.")
                    return

                self.tree.clear()
                file_names = [file_info.filename for file_info in zip_ref.infolist() if not file_info.is_dir() and not os.path.splitext(file_info.filename)[1]]
                file_names.sort()

                for file_name in file_names:
                    try:
                        with zip_ref.open(file_name) as file:
                            data = json.load(file)
                        packages = self.extract_packages_and_versions(data)

                        file_item = QTreeWidgetItem(self.tree)
                        file_item.setText(0, os.path.basename(file_name))
                        dummy = QTreeWidgetItem(file_item)
                        dummy.setText(0, "Loading...")

                        file_item.setData(0, Qt.UserRole, packages)
                    except json.JSONDecodeError:
                        continue

                self.tree.resizeColumnToContents(0)

        except UnicodeDecodeError as e:
            self.errorLabel.setText("Error: Incompatible ZIP file format.")

    def loadPackages(self, item):
        while item.childCount() > 0:
            item.removeChild(item.child(0))

        child_item = QTreeWidgetItem(item)
        child_item.setText(0, "")

        package_table = QTableWidget()
        package_table.setColumnCount(2)
        package_table.setHorizontalHeaderLabels(["Package", "Version"])
        packages = item.data(0, Qt.UserRole)
        if packages:
            package_table.setRowCount(len(packages))
            for i, (pkg_name, version) in enumerate(packages.items()):
                package_table.setItem(i, 0, QTableWidgetItem(pkg_name))
                package_table.setItem(i, 1, QTableWidgetItem(version))
            package_table.resizeColumnsToContents()

        package_table.setEditTriggers(QTableWidget.NoEditTriggers)
        package_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        package_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        total_height = package_table.horizontalHeader().height() + 4
        for i in range(package_table.rowCount()):
            total_height += package_table.rowHeight(i)
        package_table.setMinimumHeight(total_height)

        self.tree.setItemWidget(child_item, 0, package_table)

    def extract_packages_and_versions(self, json_data):
        if 'packages' in json_data:
            packages_section = json_data['packages']
            return {package['name']: package['version'] for package in packages_section}
        else:
            return {}

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PackageViewer()
    ex.show()
    sys.exit(app.exec_())



