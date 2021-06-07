import pyodbc
from PyQt5.QtWidgets import QApplication, QComboBox, QDialog, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit
from functools import partial


class DatabaseConnection:
    def __init__(self):
        self.server = '127.0.0.1,1433'
        self.database = 'prace_dyplomowe'
        self.username = 'sa'
        self.password = 'yourStrong(!)Password'
        self.cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
                                   self.server+';DATABASE='+self.database+';UID='+self.username+';PWD='+self.password)
        self.cursor = self.cnxn.cursor()

    def close(self):
        # Close the cursor and delete it
        self.cursor.close()
        del self.cursor

        # Close the database connection
        self.cnxn.close()


class MainApp:
    def __init__(self, cursor):
        self.cursor = cursor

    def add_student_to_db(self):
        try:
            self.cursor.execute(
                '''INSERT INTO dbo.Student VALUES ({0}, '{1}', '{2}', 2);'''.format(self.leIdxName.text(), self.leName.text(), self.leSurname.text()))
            self.cursor.commit()
        except Exception as e:
            print("Nie mozna dodac do bazy danych" + e)

    def say_hello(self):
        d = QDialog()
        hBoxLayout = QHBoxLayout()
        d.setWindowTitle("Wprowadz studenta")
        d.setLayout(hBoxLayout)
        self.leName = QLineEdit()
        self.leSurname = QLineEdit()
        self.leIdxName = QLineEdit()
        btnAddStudent = QPushButton("Dodaj")
        self.leName.setPlaceholderText("Imie studenta")
        self.leSurname.setPlaceholderText("Nazwisko studenta")
        self.leIdxName.setPlaceholderText("Numer indeksu studenta")
        hBoxLayout.addWidget(self.leName)
        hBoxLayout.addWidget(self.leSurname)
        hBoxLayout.addWidget(self.leIdxName)
        hBoxLayout.addWidget(btnAddStudent)
        btnAddStudent.clicked.connect(self.add_student_to_db)
        d.exec_()

    def get_query_by_idx(self):
        current_idx = self.cmbSelection.currentIndex()
        if current_idx == 0:
            return "SELECT Imie, Nazwisko, NR_INDEKSU FROM dbo.Student ORDER BY Nazwisko asc;"
        if current_idx == 1:
           return '''SELECT pd.TematPracy, pd.NR_INDEKSU AS 'Student', LOWER(tp.Typ) AS 'Typ pracownika', pn.Imie, LOWER(pn.Nazwisko) AS 'Nazwisko' FROM dbo.PracaDyplomowa as pd
                    INNER JOIN dbo.TypPracownika AS tp ON pd.TypPracownika = tp.ID
                    INNER JOIN dbo.PracownikNaukowy AS pn ON tp.ID_PRACOWNIKA = pn.ID
                    WHERE 
                        tp.Typ = 'recenzent'
                        AND
                        pn.Nazwisko = '{0}';'''.format(self.leSelection.text())
        if current_idx == 2:
            return '''SELECT s.Imie, UPPER(s.Nazwisko) AS 'Nazwisko', s.NR_INDEKSU, pd.TematPracy FROM dbo.PracaDyplomowa as pd
                        INNER JOIN dbo.Student AS s ON pd.NR_INDEKSU = s.NR_INDEKSU
                        WHERE 
                        s.Nazwisko = '{0}';'''.format(self.leSelection.text())

        if current_idx == 3:
            return '''SELECT S.Imie, S.Nazwisko, S.NR_INDEKSU, R.Stopien, LOWER(R.Kierunek) AS 'Kierunek', pd.TematPracy, O.Termin FROM dbo.Obrona as O
                        INNER JOIN dbo.Student as S ON S.NR_INDEKSU = O.Student
                        INNER JOIN dbo.RodzajStudiow as R ON S.Rodzaj_studiow = R.ID
                        INNER JOIN dbo.PracaDyplomowa as pd ON O.Praca = pd.ID 
                        WHERE
                            R.Kierunek = '{0}'
                            OR 
                            YEAR(O.Termin) = 2012;'''.format(self.leSelection.text())
        if current_idx == 4:
            return '''SELECT LOWER(pd.TematPracy), S.Imie, S.Nazwisko FROM dbo.PracaDyplomowa as pd
                        INNER JOIN dbo.Student as S ON pd.NR_INDEKSu = S.NR_INDEKSU
                        WHERE TematPracy LIKE '%{0}%';'''.format(self.leSelection.text())

        return ''

    def show_filtered(self):
        self.cursor.execute(self.get_query_by_idx())
        self.show_all(self.table)

    def clear_all(self):
        self.table.clear()

    def show_all(self, table):
        self.clear_all()
        # iterate the cursor
        row = self.cursor.fetchone()
        if row is None:
            return

        print(len(row))
        table.setColumnCount(len(row))
        table.setRowCount(len(row) + 1)
        i = 0
        while row:
            # Print the row
            for j in range(len(row)):
                item = QTableWidgetItem(str(row[j]))
                table.setItem(i, j, item)

            row = self.cursor.fetchone()
            i += 1

    def run(self):
        app = QApplication([])
        window = QWidget()

        layout = QVBoxLayout()
        btnHello = QPushButton('Dodaj studenta')
        layout.addWidget(btnHello)
        btnHello.clicked.connect(self.say_hello)
        hLayout = QHBoxLayout()

        self.cmbSelection = QComboBox()
        self.cmbSelection.addItems(
            ['Wyswietl studentow', 'Wyswietl prace zwiazane z tematyka', 'Wyswietl prace danego studenta', 'Wyswietl wszystkie obronione prace na danym kierunku', 'Wyswietl wszyskie prace ktore zawieraja slowo'])
        hLayout.addWidget(self.cmbSelection)
        self.leSelection = QLineEdit()
        hLayout.addWidget(self.leSelection)
        btnFilter = QPushButton('Szukaj')
        btnFilter.clicked.connect(self.show_filtered)
        hLayout.addWidget(btnFilter)
        layout.addLayout(hLayout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(
            ["Imie", "Nazwisko", "Nr indeksu"])
        layout.addWidget(self.table)

        window.setLayout(layout)
        window.show()

        self.cursor.execute(self.get_query_by_idx())

        ##### 2 ##############
        # SELECT st.Nazwa, pn.Imie, pn.Nazwisko FROM dbo.PracownikNaukowy as pn
        # INNER JOIN dbo.Stopien AS st ON st.ID = pn.ID
        # WHERE StopienID IS NOT NULL
        # ORDER BY st.Nazwa ASC;
        ######################

        ##### 3 ##############
        # SELECT * FROM dbo.PracaDyplomowa
        # ORDER BY TematPracy;
        ######################

        ##### 4 ##############
        # SELECT S.Imie, S.Nazwisko, S.NR_INDEKSU, R.Stopien, LOWER(R.Kierunek) AS 'Kierunek', pd.TematPracy, O.Termin FROM dbo.Obrona as O
        # INNER JOIN dbo.Student as S ON S.NR_INDEKSU = O.Student
        # INNER JOIN dbo.RodzajStudiow as R ON S.Rodzaj_studiow = R.ID
        # INNER JOIN dbo.PracaDyplomowa as pd ON O.Praca = pd.ID
        # ORDER BY O.Termin;
        ######################

        self.show_all(self.table)

        # self.cursor.
        app.exec()


if __name__ == "__main__":
    dbConnection = DatabaseConnection()
    app = MainApp(dbConnection.cursor)
    app.run()
    dbConnection.close()
