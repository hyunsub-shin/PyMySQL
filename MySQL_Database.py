# https://www.youtube.com/watch?v=lHa11Ub_JCY

import sys
import os
import pymysql
import pandas as pd

from datetime import datetime
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QTableWidgetItem, QFileDialog
# from PyQt5.QtCore import Qt
# from PyQt5 import QtGui

# from Database_viewer import Ui_MainWindow
import resource_rc

'''
pyuic5.exe .\Database_viewer.ui -o .\Database_viewer.py
pyrcc5.exe .\resource.qrc -o .\resource_rc.py
'''

'''
Make exe file cmd
 - pyinstaller -w -F MySQL_Database.py
modify control_add_graph.spec file
 - add ui file
    # -*- mode: python ; coding: utf-8 -*-
    files = [('Database_viewer.ui','.'),('cloud-sql3-14659761.png','.')] <===== add
    
 - change datas=[]
    a = Analysis(['MySQL_Database.py'],
                pathex=[],
                binaries=[],
    change ===> datas=files,
    
 - Add icon file
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        icon='cloud-sql3-14659761.png', <===== add icon
        
one more Make exe file cmd
 - pyinstaller -w -F MySQL_Database.spec
'''
####################################################
app = QtWidgets.QApplication([])
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ui_file = os.path.join(BASE_DIR, 'Database_viewer.ui')

# 운영체제 확인 및 경로 설정
if os.name == 'nt':  # Windows
    ui_file = ui_file.replace('/', '\\')
else:  # Linux/Unix
    ui_file = ui_file.replace('\\', '/')

ui = uic.loadUi(ui_file)
ui.setWindowTitle("Database partList Editor")
####################################################

table = ui.tableWidget
db_table_name = "partList"

class DatabaseManager:
    def __init__(self):
        self.mydb = None
        self.mycursor = None
        self.selected_id = None
        self.selected_col = None
        
        ui.lineEdit_host.setPlaceholderText('host 입력')
        ui.lineEdit_port.setPlaceholderText('port 입력')
        ui.lineEdit_user.setPlaceholderText('user 입력')
        ui.lineEdit_db.setPlaceholderText('database 입력')
        ui.lineEdit_pw.setPlaceholderText('password 입력')
        ui.lineEdit_item.setPlaceholderText('item 입력')
        ui.lineEdit_partName.setPlaceholderText('partName 입력')
        ui.lineEdit_package.setPlaceholderText('package 입력')
        ui.lineEdit_qty.setPlaceholderText('qty 입력')
        ui.lineEdit_vendor.setPlaceholderText('vendor 입력')
        ui.lineEdit_search.setPlaceholderText('find')
        
        ui.lineEdit_port.setText("3306")

    def connect(self):
        try:
            self.mydb = pymysql.connect(
                host=ui.lineEdit_host.text(),
                port=int(ui.lineEdit_port.text()),
                user=ui.lineEdit_user.text(),
                password=ui.lineEdit_pw.text(),
                database=ui.lineEdit_db.text(),
                charset='utf8'
            )
            self.mycursor = self.mydb.cursor()
            self.get_data()
            QMessageBox.information(None, "success", "MySQL database connect!", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.information(None, "Error", f"MySQL database Not connect!:\n{str(e)}", QMessageBox.Ok)

    def get_data(self):
        try:
            self.mycursor.execute(f"SELECT * FROM {db_table_name}")
            self.display_table(self.mycursor.fetchall())
        except Exception:
            QMessageBox.information(None, "Error", "No data got from database", QMessageBox.Ok)

    @staticmethod
    def display_table(db_data):
        table.setRowCount(len(db_data))
        for row, row_data in enumerate(db_data):
            for col, value in enumerate(row_data):
                # qty 컬럼(인덱스 4)인 경우 천단위 구분자 추가
                if col == 4 and str(value).isdigit():
                    formatted_value = "{:,}".format(int(value))
                    table.setItem(row, col, QTableWidgetItem(formatted_value))
                else:
                    table.setItem(row, col, QTableWidgetItem(str(value)))

    def export_data(self):
        try:
            now = datetime.now().strftime("%Y-%m-%d")
            file_name = f"Export_DB_{now}.xlsx"
            
            file, _ = QFileDialog.getSaveFileName(
                None, "Excel 파일 저장", file_name, "Excel Files (*.xlsx)"
            )
            
            if not file:
                return
                
            table_data = [
                [table.item(row, col).text() if table.item(row, col) else ''
                for col in range(table.columnCount())]
                for row in range(table.rowCount())
            ]
            
            df = pd.DataFrame(table_data, columns=["id", "item", "PartName", "package", "qty", "vendor"])
            df.to_excel(file, index=False)
            QMessageBox.information(None, "Success", "Data exported successfully!", QMessageBox.Ok)
            
        except Exception as e:
            QMessageBox.information(None, "Error", f"Export failed: {str(e)}", QMessageBox.Ok)

    def import_data(self):
        reply = QMessageBox.question(None, "Confirm Import", 
                                   "This will replace all existing data. Continue?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                file, _ = QFileDialog.getOpenFileName(
                    None, "Import Excel", "", "Excel Files (*.xlsx)"
                )
                
                if not file:
                    return
                    
                df = pd.read_excel(file)
                # qty 컬럼의 쉼표 제거 및 숫자 변환
                if 'qty' in df.columns:
                    df['qty'] = df['qty'].astype(str).str.replace(',', '').astype(float).astype(int)
                
                df = df.replace({pd.NA: '', '': ''})  # 빈 값을 ''으로 통일
                data = df.values.tolist()
                
                self.delete_all_data()
                
                sql = f"INSERT INTO {db_table_name} VALUES (%s, %s, %s, %s, %s, %s)"
                for row in data:
                    self.mycursor.execute(sql, tuple(row))
                    
                self.mydb.commit()
                self.get_data()
                QMessageBox.information(None, "Success", "Data imported successfully!", QMessageBox.Ok)
                
            except Exception as e:
                QMessageBox.information(None, "Error", f"Import failed: {str(e)}", QMessageBox.Ok)

    def delete_all_data(self):
        try:
            self.mycursor.execute(f"TRUNCATE TABLE {db_table_name}")
            self.mydb.commit()
        except Exception as e:
            raise Exception(f"Failed to clear table: {str(e)}")

    def reset_search(self):
        ui.lineEdit_search.setText("")
        for row in range(table.rowCount()):
            table.setRowHidden(row, False)

    def add_part(self):
        try:
            values = (
                ui.lineEdit_item.text(),
                ui.lineEdit_partName.text(),
                ui.lineEdit_package.text(),
                ui.lineEdit_qty.text(),
                ui.lineEdit_vendor.text()
            )
            sql = f"INSERT INTO {db_table_name} (item, partName, package, qty, vendor) VALUES (%s, %s, %s, %s, %s)"
            self.mycursor.execute(sql, values)
            self.mydb.commit()
            self.get_data()
            self.clear_inputs()
            QMessageBox.information(None, "OK", "Part Add Success!!", QMessageBox.Ok)
        except Exception:
            QMessageBox.information(None, "Error", "Part is Not add!!", QMessageBox.Ok)

    def edit_part(self):
        try:
            if not self.selected_id or not self.selected_col:
                QMessageBox.information(None, "Error", "Please select a cell to edit", QMessageBox.Ok)
                return

            col_names = ["id", "item", "partName", "package", "qty", "vendor"]
            col_name = col_names[self.selected_col]
            item = table.item(table.currentRow(), self.selected_col)
            
            if not item:
                return

            sql = f"UPDATE {db_table_name} SET {col_name} = %s WHERE id = %s"
            self.mycursor.execute(sql, (item.text(), self.selected_id))
            self.mydb.commit()
            
            self.get_data()
            self.clear_inputs()
            QMessageBox.information(None, "OK", f"{col_name} Update Success!!", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.information(None, "Error", f"Update failed: {str(e)}", QMessageBox.Ok)

    def delete_part(self):
        if not self.selected_id:
            QMessageBox.information(None, "Error", "Please select a part to delete", QMessageBox.Ok)
            return

        reply = QMessageBox.question(None, "Confirm Delete", 
                                   "Are you sure you want to delete this part?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                sql = f"DELETE FROM {db_table_name} WHERE id = %s"
                self.mycursor.execute(sql, (self.selected_id,))
                self.mydb.commit()
                self.get_data()
                self.clear_inputs()
                QMessageBox.information(None, "OK", "Part deleted successfully", QMessageBox.Ok)
            except Exception as e:
                QMessageBox.information(None, "Error", f"Delete failed: {str(e)}", QMessageBox.Ok)

    def select_cell(self):
        current_row = table.currentRow()
        self.selected_col = table.currentColumn()
        
        row_data = []
        for col in range(table.columnCount()):
            item = table.item(current_row, col)
            if item:
                row_data.append(item.text())

        if row_data:
            self.selected_id = row_data[0]
            self.update_input_fields(row_data)

    def update_input_fields(self, row_data):
        if len(row_data) >= 6:
            ui.lineEdit_item.setText(row_data[1])
            ui.lineEdit_partName.setText(row_data[2])
            ui.lineEdit_package.setText(row_data[3])
            ui.lineEdit_qty.setText(row_data[4])
            ui.lineEdit_vendor.setText(row_data[5])

    @staticmethod
    def clear_inputs():
        for field in ['item', 'partName', 'package', 'qty', 'vendor']:
            getattr(ui, f'lineEdit_{field}').setText("")

    def search_part(self):
        search_text = ui.lineEdit_search.text().lower()
        for row in range(table.rowCount()):
            hide_row = True
            for col in range(table.columnCount()):
                if search_text in table.item(row, col).text().lower():
                    hide_row = False
                    break
            table.setRowHidden(row, hide_row)

db = DatabaseManager()

# Connect all signals
ui.pushButton_connect.clicked.connect(db.connect)
ui.pushButton_getdata.clicked.connect(db.get_data)
ui.pushButton_exportdata.clicked.connect(db.export_data)
ui.pushButton_importdata.clicked.connect(db.import_data)
ui.pushButton_addpart.clicked.connect(db.add_part)
ui.pushButton_editpart.clicked.connect(db.edit_part)
ui.pushButton_deletepart.clicked.connect(db.delete_part)
ui.pushButton_search.clicked.connect(db.search_part)
ui.pushButton_reset.clicked.connect(db.reset_search)
table.cellClicked.connect(db.select_cell)

# 엔터키 입력 시 함수 호출
ui.lineEdit_pw.returnPressed.connect(db.connect)
ui.lineEdit_search.returnPressed.connect(db.search_part)

ui.show()

# CI 환경에서 실행 중인지 확인
if os.environ.get('CI'):
    # 3초 후 앱 종료
    QtCore.QTimer.singleShot(3000, app.quit)

sys.exit(app.exec_())
