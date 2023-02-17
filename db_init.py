import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

host = os.environ.get('DB_HOST')
database = os.environ.get('DB_NAME')
user = os.environ.get('DB_USER')
password = os.environ.get('DB_PASSWORD')

conn = psycopg2.connect(host=host, database=database, user=user, password=password)
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS seminar CASCADE')
cur.execute('CREATE TABLE seminar ('
            'id SERIAL,'
            '"name" VARCHAR(100),'
            'abkuerzung VARCHAR(10),'
            'PRIMARY KEY(id));')

cur.execute('DROP TABLE IF EXISTS studiengang CASCADE')
cur.execute('CREATE TABLE studiengang ('
            'id SERIAL,'
            '"name" VARCHAR(100),'
            'abkuerzung VARCHAR(10),'
            'PRIMARY KEY(id));')

cur.execute('DROP TABLE IF EXISTS abschluss CASCADE')
cur.execute('CREATE TABLE abschluss ('
            'id SERIAL,'
            '"name" VARCHAR(100),'
            'abkuerzung VARCHAR(10),'
            'PRIMARY KEY(id));')

cur.execute('DROP TABLE IF EXISTS student CASCADE')
cur.execute('CREATE TABLE student ('
            'id SERIAL,'
            'vorname VARCHAR(100),'
            'nachname VARCHAR(100),'
            'email VARCHAR(254) NOT NULL UNIQUE,'
            '"password" VARCHAR(72) NOT NULL,'
            'matrikelnummer INT NOT NULL UNIQUE,'
            'abschluss_id INT,'
            'studiengang_id INT,'
            'seminar_id INT,'
            'PRIMARY KEY (id),'
            'FOREIGN KEY (abschluss_id) REFERENCES abschluss(id),'
            'FOREIGN KEY (studiengang_id) REFERENCES studiengang(id),'
            'FOREIGN KEY (seminar_id) REFERENCES seminar(id));')

cur.execute('DROP TABLE IF EXISTS dozent CASCADE')
cur.execute('CREATE TABLE dozent ('
            'id SERIAL,'
            'vorname VARCHAR(100),'
            'nachname VARCHAR(100),'
            'email VARCHAR(254) NOT NULL UNIQUE ,'
            '"password" VARCHAR(72) NOT NULL,'
            'PRIMARY KEY(id));')

cur.execute('DROP TABLE IF EXISTS seminar_thema CASCADE')
cur.execute('CREATE TABLE seminar_thema ('
            'id SERIAL,'
            '"name" VARCHAR(255) NOT NULL,'
            'oberbegriff VARCHAR(255) NOT NULL,'
            'beschreibung TEXT NOT NULL,'
            'semester VARCHAR(20),'
            'status VARCHAR(20),'
            'filename VARCHAR(255),'
            'dozent_id INT,'
            'student_email VARCHAR(254) UNIQUE,'
            'filedata bytea,'
            'PRIMARY KEY (id),'
            'FOREIGN KEY (dozent_id) REFERENCES dozent(id),'
            'FOREIGN KEY (student_email) REFERENCES student(email));')

cur.execute('DROP TABLE IF EXISTS vortrag_bewertung CASCADE')
cur.execute('CREATE TABLE vortrag_bewertung ('
            'id SERIAL,'
            'foliengestaltung INT,'
            'sprach_praesentation INT,'
            'praesentationsstil INT,'
            'zeit_gestaltung INT,'
            'verstaendnis INT,'
            'inhaltlich_Aufbereitung INT,'
            'verknuepfung_Vortraege INT,'
            'diskussionsfuehrung_eigener INT,'
            'beteiligung_diskussion INT,'
            'kommentar VARCHAR(255),'
            'student INT,'
            'seminar_id INT,'
            'FOREIGN KEY (seminar_id) REFERENCES seminar_thema(id),'
            'FOREIGN KEY (student) REFERENCES student(matrikelnummer));')

cur.execute('DROP TABLE IF EXISTS ausarbeitung_bewertung CASCADE')
cur.execute('CREATE TABLE ausarbeitung_bewertung ('
            'id SERIAL,'
            'umfang INT,'
            'referenz INT,'
            'sprachlich INT,'
            'inhaltlich INT,'
            'schwierigkeit INT,'
            'kommentar VARCHAR(255),'
            'student_id INT,'
            'seminar_id INT,'
            'FOREIGN KEY (seminar_id) REFERENCES seminar_thema(id),'
            'FOREIGN KEY (student_id) REFERENCES student(id));')

cur.execute('DROP TABLE IF EXISTS student_noten CASCADE')
cur.execute('CREATE TABLE student_noten ('
            'id SERIAL,'
            'note INT,'
            'kommentar VARCHAR(255),'
            'student_id INT,'
            'seminar_id INT,'
            'FOREIGN KEY (seminar_id) REFERENCES seminar_thema(id),'
            'FOREIGN KEY (student_id) REFERENCES student(id));')
conn.commit()

#  Testdaten hinzufügen
cur.execute('TRUNCATE TABLE seminar CASCADE')
seminar_values = [
    ("Intelligente Informationssysteme", "IIS"),
    ("Wissensbasierte Systeme", "WBS")
]
cur.executemany('INSERT INTO seminar("name", abkuerzung)'
                'VALUES (%s, %s)', seminar_values)

cur.execute('TRUNCATE TABLE studiengang CASCADE')
studiengang_values = [
    ("Wirtschaftsinformatik", "WINF"),
    ("Informationsmanagement und Informationstechnologie", "IMIT"),
    ("Angewandte Informatik", "AI"),
    ("Internationales Informationsmanagement", "IIM"),
    ("Interkulturelle Kommunikation und Übersetzen", "IKÜ")
]
cur.executemany('INSERT INTO studiengang("name", abkuerzung)'
                'VALUES (%s, %s)', studiengang_values)

cur.execute('TRUNCATE TABLE abschluss CASCADE')
abschluss_values = [
    ("Bachelor of Arts", "B.A."),
    ("Master of Arts", "M.A."),
    ("Bachelor of Science", "B.Sc."),
    ("Master of Science", "M.Sc.")
]
cur.executemany('INSERT INTO abschluss("name", abkuerzung)'
                'VALUES (%s, %s)', abschluss_values)

cur.execute('TRUNCATE TABLE dozent CASCADE')
dozent_values = [
    ("Prof. Dr. John", "Schmidt", "schmidt@uni.com", "Passwort!123"),
    ("Dr. Gregory", "House", "house@uni.com", "Passwort!123")
]
cur.executemany('INSERT INTO dozent(vorname, nachname, email, "password")'
                'VALUES (%s, %s, %s, %s)', dozent_values)

cur.execute('TRUNCATE TABLE student CASCADE')
student_values = [
    ("Jesse", "Spencer", "spencer@uni.com", "Passwort!123", 111111, 1, 4, 1),
    ("Jennifer", "Morrison", "morrison@uni.com", "Passwort!123", 222222, 2, 3, 3)]

cur.executemany('INSERT INTO student(vorname, nachname, email, "password", matrikelnummer, seminar_id, '
                'studiengang_id, abschluss_id)'
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', student_values)

cur.execute('TRUNCATE TABLE seminar_thema CASCADE')
seminar_thema_values = [
    ("Erstes Thema", "Erster Oberbegriff", "Das erste Beispielthema", "WiSe 22/23", "vergeben", 1,
     "spencer@uni.com"),
    ("Zweites Thema", "Zweiter Oberbegriff", "Das zweite Beispielthema", "WiSe 22/23", "vergeben", 2,
     "morrison@uni.com")
]
cur.executemany(
    'INSERT INTO seminar_thema("name", oberbegriff, beschreibung, semester, status, dozent_id, student_email)'
    'VALUES (%s, %s, %s, %s, %s, %s, %s)', seminar_thema_values)

cur.execute('TRUNCATE TABLE vortrag_bewertung CASCADE')
bewertung_values = [
    (2, 3, 4, 3, 3, 5, 3, 2, 4, "Das war eine sehr gute Praesentation", 222222, 2),
    (1, 5, 4, 4, 2, 1, 2, 3, 5, "Das schlecht", 222222, 2),
    (5, 4, 1, 1, 4, 2, 4, 2, 3, "Du hast viele Bilder benutzt", 222222, 2),
    (2, 3, 4, 3, 3, 5, 3, 4, 5, "Das war eine sehr gute Praesentation", 111111, 1),
    (1, 5, 4, 4, 2, 1, 2, 4, 2, "Das schlecht", 111111, 1),
    (5, 4, 1, 1, 4, 2, 4, 5, 1, "Du hast viele Bilder benutzt", 111111, 1)
]
cur.executemany('INSERT INTO vortrag_bewertung(foliengestaltung, sprach_praesentation, praesentationsstil, '
                'zeit_gestaltung, verstaendnis, inhaltlich_Aufbereitung, '
                'verknuepfung_Vortraege, diskussionsfuehrung_eigener, '
                'beteiligung_diskussion, kommentar, student, seminar_id)'
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', bewertung_values)

conn.commit()
cur.close()
conn.close()
