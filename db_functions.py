import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def do_sql_parameterized(sql, parameters):
    # Benötigte Variablen um die Datenbankverbindung aufzubauen
    host = os.environ.get('DB_HOST')
    database = os.environ.get('DB_NAME')
    user = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASSWORD')

    # Aufbauen der Verbindung
    conn = psycopg2.connect(host=host, database=database, user=user, password=password)
    cur = conn.cursor()

    # Ausführen des SQL Befehls
    if parameters:
        cur.execute(sql, parameters)
        conn.commit()
    else:
        cur.execute(sql)
        conn.commit()

    # Versuchen eine Rückgabe zu holen, falls keine vorhanden: None
    try:
        output = cur.fetchall()
    except:
        output = None

    # Verbindung schließen
    cur.close()
    conn.close()

    # Rückgabe von SQL Resultaten
    return output


def db_add_user(data):
    sql = "INSERT INTO public.student (vorname, nachname, email, password, matrikelnummer, " \
          "abschluss_id, studiengang_id, seminar_id) " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    return do_sql_parameterized(sql, data)


def db_edit_student(data):
    sql = "UPDATE public.student " \
          "SET vorname = %s, nachname = %s, email = %s, password = %s, matrikelnummer = %s, " \
          "abschluss_id = %s, studiengang_id = %s, seminar_id = %s " \
          "WHERE public.student.id = %s"
    return do_sql_parameterized(sql, data)


def db_add_seminar_thema(data: list):
    sql = "INSERT INTO public.seminar_thema (name, oberbegriff, beschreibung, semester, " \
          "status, filename, dozent_id, student_email, filedata) " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    return do_sql_parameterized(sql, data)


def db_edit_seminar_thema(data: list):
    sql = "UPDATE public.seminar_thema " \
          "SET name = %s, oberbegriff = %s, beschreibung = %s, semester = %s, status = %s, " \
          "filename = %s, dozent_id = %s, student_email = %s, filedata = %s " \
          "WHERE seminar_thema.id = %s"
    return do_sql_parameterized(sql, data)


def db_get_student_by_mail(email):
    sql = "SELECT * FROM public.student WHERE public.student.email = %s"
    value = do_sql_parameterized(sql, (email,))
    if len(value) == 0:
        return []
    else:
        return value[0]


def db_get_dozent_by_mail(email):
    sql = "SELECT * FROM public.dozent WHERE public.dozent.email = %s"
    value = do_sql_parameterized(sql, (email,))
    if len(value) == 0:
        return []
    else:
        return value[0]


def db_get_all_dozenten():
    """ Alle Dozenten aus der Datenbank in eine Liste schreiben

    :return: List
                [ ( (Name und Nachname), (Dozent_ID) )   , # dozent 1
                  ( (Name und Nachname), (Dozent_ID) )   , # dozent 2
                  ( (Name und Nachname), (Dozent_ID) )  ]  # dozent 3

    """
    sql = "SELECT * FROM public.dozent;"
    value = do_sql_parameterized(sql)
    if len(value) == 0:
        print("Keine Dozenten gefunden")
    else:
        values = []
        value = value
        for dozent in value:
            name_dozent = dozent[1]  # Vorname
            name_dozent += " " + dozent[2]  # Nachname
            email = dozent[0]  # Email
            values.append([name_dozent, email])
        return values


def db_edit_dozent(data):
    sql = "UPDATE public.dozent " \
          "SET vorname = %s, nachname = %s, email = %s, password = %s " \
          "WHERE public.dozent.id = %s"
    return do_sql_parameterized(sql, data)


def db_edit_seminar_thema_belegen(data):
    sql = "UPDATE public.seminar_thema " \
          "SET status = %s, student_email = %s " \
          "WHERE seminar_thema.id = %s"
    return do_sql_parameterized(sql, data)


def db_get_student_matrikel_by_seminar(sem_id):
    """ Funktion gibt den Studenten des Seminars zurück

    :param sem_id: int
            Seminar ID
    :return: output of do_sql()
    """
    sql = "SELECT matrikelnummer " \
          "FROM public.student " \
          "WHERE public.student.seminar_id = %s"
    return do_sql_parameterized(sql, (sem_id,))


def db_add_bewertung(data):
    """ Funktion fügt eine Bewertung in die Datenbank hinzu

    :param sem_id: int
            Seminar ID
    :param data:
            Array mit den Bewertungsdaten
    :return: output of do_sql()

    """
    sql = "INSERT INTO public.vortrag_bewertung (foliengestaltung, sprach_praesentation, praesentationsstil, " \
          "zeit_gestaltung, verstaendnis, inhaltlich_Aufbereitung, verknuepfung_Vortraege, " \
          "diskussionsfuehrung_eigener, beteiligung_diskussion, kommentar, student, seminar_id)" \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    return do_sql_parameterized(sql, data)


def db_get_bewertung(student_id):
    """ Fragt alle Bewertungen eines Studenten, anhand der Studenten ID

    :param student_id: int
            Seminar ID
    :return: output of do_sql()
    """
    sql = "SELECT foliengestaltung, sprach_praesentation, praesentationsstil, zeit_gestaltung, " \
          "verstaendnis, inhaltlich_Aufbereitung, verknuepfung_Vortraege, diskussionsfuehrung_eigener, " \
          "beteiligung_diskussion " \
          "FROM public.vortrag_bewertung " \
          "WHERE public.vortrag_bewertung.student = %s"
    return do_sql_parameterized(sql, (student_id,))


def db_add_benotung_student(sem_id, data):
    """ Funktion fügt eine Bewertung in die Datenbank hinzu

    :param sem_id: int
            Seminar ID
    :param data:
            Array mit den Bewertungsdaten
    :return: output of do_sql()

    """
    sql = "INSERT INTO public.student_noten (note, kommentar, student_id, seminar_id) " \
          "VALUES  (%s, %s, %s, %s)"
    return do_sql_parameterized(sql, data)


def db_get_benotung_student(student_id):
    """ Funktion fügt eine Benotung in die Datenbank hinzu

    :param sem_id: int
            Seminar ID
    :param data:
            Array mit den Bewertungsdaten
    :return: output of do_sql()

    """
    sql = "SELECT note " \
          "FROM public.student_noten " \
          "WHERE public.student_noten.student_id = %s"
    benotung = do_sql_parameterized(sql, (student_id,))
    benotung = list(benotung)
    if len(benotung) > 0:
        benotung = list(benotung[0])
        return benotung[0]
    else:
        return -1


def db_get_seminarthema_by_id(seminar_id):
    sql = "SELECT * FROM seminar_thema WHERE id = %s"
    thema = do_sql_parameterized(sql, (seminar_id,))
    thema = [list(i) for i in thema]
    return thema


def db_get_seminarthema_name_by_student_email(session_email):
    sql = "SELECT name FROM seminar_thema WHERE student_email = %s"
    return do_sql_parameterized(sql, (session_email,))[0][0]


def db_get_seminarthema_id_by_name(session_seminarthema):
    sql = "SELECT id FROM seminar_thema WHERE name = %s"
    return do_sql_parameterized(sql, (session_seminarthema,))[0][0]


def db_add_ausarbeitung_bewertung(data_bewertung):
    """

    :param data_bewertung: List (Datenliste der Bewertungen für eine Ausarbeitung)
    :return: Boolean (True bei Erfolg)
    """
    sql = "INSERT INTO public.ausarbeitung_bewertung (umfang, referenz, sprachlich, inhaltlich, " \
          "schwierigkeit, kommentar,  student_id, seminar_id) " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    return do_sql_parameterized(sql, data_bewertung)


def db_get_student_id_by_seminar_id(sem_id):
    """ Erhalte Student id mit der Seminar ID

    :param sem_id: INT (Seminar ID des Studenten)
    :return: Int (Studen_id)
    """
    sql = "SELECT id FROM public.student WHERE public.student.seminar_id = %s"
    return do_sql_parameterized(sql, (sem_id,))


def db_get_student_email_by_seminarthema_id(seminarthema_id):
    sql = "SELECT student_email FROM seminar_thema WHERE id = %s"
    return do_sql_parameterized(sql, (seminarthema_id,))


def db_get_ausarbeitung_bewertung(student_id):
    """

    :param student_id: int (Studenten ID dessen Bewertungen geuscht werden soll)
    :return: List (Liste mit allen Bewertungen für Ausarbeitungen)
    """
    sql = "SELECT * FROM ausarbeitung_bewertung WHERE student_id = %s"
    bewertung = do_sql_parameterized(sql, (student_id,))
    if len(bewertung) > 0:
        bewertung = list(bewertung[0])[:5]
        average = 0
        for wertung in bewertung:
            average = average + wertung
        average = round(average / len(bewertung))
        return average
    else:
        return -1


def db_close_seminar(seminar_id):
    """

    :param seminar_id:
    :return:
    """
    sql = "UPDATE public.seminar_thema " \
          "SET status='Abgeschlossen' " \
          "WHERE public.seminar_thema.id = %s"
    return do_sql_parameterized(sql, (seminar_id,))


def db_check_if_student_belegt(student_mail):
    """

    :param student_mail: String (Email Adresse des Studenten)
    :return: Boolean (True wenn ein Serminar belegt und offen, False wenn kein Seminar offen )
    """
    sql = "SELECT status FROM seminar_thema WHERE public.seminar_thema.student_email = %s"
    themen_student = do_sql_parameterized(sql, (student_mail,))
    if len(themen_student) > 0:
        themen_student = [list(i) for i in themen_student]
        for value in themen_student:
            if value[0] == "vergeben" or value[0] == "frei":
                return True
    return False


def db_get_profil_alle_studierende():
    return do_sql_parameterized("SELECT stud.id, "
                                        "stud.vorname, "
                                        "stud.nachname, "
                                        "stud.email, "
                                        "stud.matrikelnummer, "
                                        "a.name, "
                                        "std.name, "
                                        "s.name, "
                                        "st.name "
                                "FROM student stud "
                                        "INNER JOIN studiengang std on stud.studiengang_id = std.id "
                                        "INNER JOIN abschluss a on a.id = stud.abschluss_id "
                                        "INNER JOIN seminar s on stud.seminar_id = s.id "
                                        "LEFT OUTER JOIN seminar_thema st on stud.email = st.student_email "
                                "ORDER BY stud.id;")


def db_get_profil_einzelne_studierende(student_email):
    return do_sql_parameterized("SELECT stud.id, "
                                        "stud.vorname, "
                                        "stud.nachname, "
                                        "stud.email, "
                                        "stud.matrikelnummer, "
                                        "a.name, "
                                        "std.name, "
                                        "s.name, "
                                        "st.name "
                                "FROM student stud " 
                                        "INNER JOIN studiengang std on stud.studiengang_id = std.id "
                                        "INNER JOIN abschluss a on a.id = stud.abschluss_id "
                                        "INNER JOIN seminar s on stud.seminar_id = s.id "
                                        "LEFT OUTER JOIN seminar_thema st on stud.email = st.student_email "
                                "WHERE stud.email= %s "
                                "ORDER BY stud.id;", (student_email,))


def db_get_seminarthemen_seite():
    return do_sql_parameterized("SELECT seminar_thema.id, "
                                    "seminar_thema.name, "
                                    "oberbegriff, "
                                    "beschreibung, "
                                    "semester, "
                                    "status, filename, concat(d.vorname, ' ', d.nachname) AS dozent_name,  "
                                    "concat(s.vorname,' ', s.nachname) AS student_name "
                                "FROM seminar_thema "
                                        "JOIN dozent d on seminar_thema.dozent_id = d.id "
                                        "LEFT OUTER JOIN student s on s.email = seminar_thema.student_email "
                                "ORDER BY seminar_thema.id;")


def db_get_current_file(file_id):
    sql = "SELECT filename, filedata FROM seminar_thema WHERE id = %s"
    return do_sql_parameterized(sql, (file_id,))


def db_get_dozent_full_name_by_id(dozent_id):
    sql = "SELECT dozent.vorname, dozent.nachname FROM dozent WHERE id = %s"
    return do_sql_parameterized(sql, (dozent_id,))


def db_get_seminarthemen_ansicht(seminarthema_id):
    sql = "SELECT * FROM seminar_thema WHERE id = %s"
    return do_sql_parameterized(sql, (seminarthema_id,))


def db_get_abschluss_name_by_id(abschluss_id):
    sql = "SELECT name " \
          "FROM abschluss " \
          "WHERE id = %s"
    return do_sql_parameterized(sql, (abschluss_id,))


def db_get_studiengang_name_by_id(studiengang_id):
    sql = "SELECT name " \
          "FROM studiengang " \
          "WHERE id = %s"
    return do_sql_parameterized(sql, (studiengang_id,))


def db_get_seminar_name_by_id(seminar_id):
    sql = "SELECT name " \
          "FROM seminar " \
          "WHERE id = %s"
    return do_sql_parameterized(sql, (seminar_id,))
