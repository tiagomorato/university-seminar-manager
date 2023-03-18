import psycopg2
import re
from flask import Flask, render_template, request, session, redirect, url_for, flash, Markup
from db_functions import *

app = Flask(__name__)
app.secret_key = "12345"
app.debug = True


def get_login_id():
    try:
        id = session["login"]
    except:
        # Die -1 dient dazu, dass erkannt wird, dass niemand momentan eingeloggt ist.
        # Falls ein anderer Wert in session["login"] steht,
        # wird angenommen, dass es die ID vom eingeloggten Nutzer ist
        session["login"] = -1
    return session["login"]


@app.route('/index')
@app.route('/')
def index():
    get_login_id()
    return render_template("index.html")


@app.route('/einloggen', methods=['GET', 'POST'])
def einloggen():
    return render_template("einloggen.html")


@app.route('/einloggen_verarbeiten', methods=["POST", "GET"])
def einloggen_verarbeiten():
    if request.method == "POST":
        data = request.form
        email = data.get('email_login')
        pw = data.get('password_login')
        try:
            user_values = db_get_student_by_mail(email)
            if len(user_values) > 1:
                if pw == user_values[4]:
                    session["login"] = user_values[0]
                    session["vorname"] = user_values[1]
                    session["nachname"] = user_values[2]
                    session["email"] = user_values[3]
                    session["password"] = user_values[4]
                    session["matrikelnummer"] = user_values[5]
                    session["abschluss"] = db_get_abschluss_name_by_id(user_values[6])[0][0]
                    session["abschluss_id"] = user_values[6]
                    session["studiengang"] = db_get_studiengang_name_by_id(user_values[7])[0][0]
                    session["studiengang_id"] = user_values[7]
                    session["seminar"] = db_get_seminar_name_by_id(user_values[8])[0][0]
                    session["seminar_id"] = user_values[8]
                    try:
                        session["seminarthema"] = db_get_seminarthema_name_by_student_email(session["email"])
                        session["seminarthema_id"] = db_get_seminarthema_id_by_name(session["seminarthema"])
                    except:
                        session["seminarthema"], session["seminarthema_id"] = None, None
                    session["is_dozent"] = False
                    flash('Logged in successfully!', 'success')
                    return redirect(url_for('profil'))
                else:
                    flash('Log in was not successful!', 'error')
                    return render_template("einloggen.html")
            else:
                user_values = db_get_dozent_by_mail(email)
                if pw == user_values[4]:
                    session["login"] = user_values[0]
                    session["vorname"] = user_values[1]
                    session["nachname"] = user_values[2]
                    session["email"] = user_values[3]
                    session["password"] = user_values[4]
                    session["is_dozent"] = True
                    flash('Logged in successfully!', 'success')
                    return render_template("profil.html")
                else:
                    flash('Log in was not successful!', 'error')
                    return render_template("einloggen.html")
        except Exception as e:
            print(e)
            flash('Log in was not successful!', 'error')
            return render_template("einloggen.html")


@app.route('/logout', methods=["POST", "GET"])
def logout():
    session["login"] = -1
    session.pop('vorname', None)
    session.pop('nachname', None)
    session.pop('email', None)
    session.pop('password', None)
    session.pop('matrikelnummer', None)
    session.pop('abschluss', None)
    session.pop('studiengang', None)
    session.pop('seminar', None)
    flash('You logged out successfully!', 'success')
    return render_template("einloggen.html")


@app.route('/registrierung', methods=["POST", "GET"])
def registrierung():
    return render_template("registrierung.html")


@app.route('/registrierung_verarbeiten', methods=["POST", "GET"])
def registrierung_verarbeiten():
    if request.method == "POST":
        data = request.form
        vorname = data.get('vorname')
        nachname = data.get('nachname')
        email = data.get('email')
        password = data.get('password')
        matrikelnummer = data.get('matrikelnummer')
        abschluss_id = data.get('abschluss')
        studiengang_id = data.get('studiengang')
        seminar_id = data.get('seminar')

        # check vorname
        if not re.match(r"^[A-Z][a-z]*([- ]?[a-z]+)*$", vorname):
            flash('Wähle einen anderen Vornamen aus. '
                  'Er muss mit einem Großbuchstaben beginnen, gefolgt von beliebig vielen Kleinbuchstaben. '
                  'Optional sind Bindestriche und Leerzeichen', 'error')
            return render_template("registrierung.html")
        # check nachname
        if not re.match(r"^[A-Z][a-z]*([- ]?[a-z]+)*$", nachname):
            flash('Wähle einen anderen Nachnamen aus. '
                  'Er muss mit einem Großbuchstaben beginnen, gefolgt von beliebig vielen Kleinbuchstaben. '
                  'Optional sind Bindestriche und Leerzeichen', 'error')
            return render_template("registrierung.html")
        # check email
        if not re.match(r"^[a-zA-Z0-9.+-]{1,63}@[a-zA-Z0-9.-]{1,254}$", email):
            flash('Wähle eine andere E-Mail aus. '
                  'Erlaubte Zeichen sind Kleinbuchstaben, Punkte, Plus und Minus. '
                  'Vor dem @ kann es bis zu 63 Zeichen und ingesamt bis 254 Zeichen geben', 'error')
            return render_template("registrierung.html")
        # check password
        if not re.match(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$%^&+=]).+$", password):
            flash('Wähle ein anderes Passwort aus. '
                  'Es muss mindests ein Groß- und Kleinbuchstabe und ein Sonderzeichen beinhalten', 'error')
            return render_template("registrierung.html")
        # check matrikelnummer
        if not re.match(r"^\d{6,8}$", matrikelnummer):
            flash('Wähle eine andere Matrikelnummer aus. '
                  'Sie muss zwischen 6 und 8 Zahlen lang sein', 'error')
            return render_template("registrierung.html")

        try:
            db_add_user([vorname, nachname, email, password, matrikelnummer, abschluss_id, studiengang_id, seminar_id])
            flash(Markup('New user created successfuly. Click <a href="einloggen">here</a> to log in.'), 'success')
            return render_template("registrierung.html")
        except Exception as e:
            print(e)
            flash('Something went wrong, try again.', 'error')
            return render_template("registrierung.html")


@app.route('/profil', methods=['GET'])
def profil():
    """

    :return:
    """
    ave_bewertung = 3
    anzahl_bewertung = 0
    try:
        all_bewertungen = db_get_bewertung(session["matrikelnummer"])
        if all_bewertungen is not None:
            ave_bewertung = calc_bewertung(all_bewertungen)[0]
            anzahl_bewertung = calc_bewertung(all_bewertungen)[1]
    except Exception as e:
        print(e)

    return render_template("profil.html", ave_bewertung=ave_bewertung, anzahl_bewertung=anzahl_bewertung)


def calc_bewertung(bewertungen):
    """
    Gibt den Durchschnitt der Bewerung und die Anzahl aller Bewertungen wieder
    :param bewertungen: list
    :return: bewertung
    """
    average = 0
    anzahl = 0
    liste_durchschnitt = []

    for vortrag in bewertungen:
        wertung = 0
        for zahl in vortrag:
            wertung = wertung + zahl
        anzahl = anzahl + 1
        liste_durchschnitt.append(wertung / 9)

    for wertung in liste_durchschnitt:
        average = average + wertung
    return round(average / len(bewertungen)), anzahl


@app.route('/profil_bearbeiten', methods=['GET', 'POST'])
def profil_bearbeiten():
    if not session["is_dozent"]:
        user_data = db_get_student_by_mail(session["email"])
        abschluss_id = user_data[6]
        studiengang_id = user_data[7]
        seminar_id = user_data[8]
        return render_template("profil_bearbeiten.html",
                               abschluss_id=abschluss_id, studiengang_id=studiengang_id, seminar_id=seminar_id)
    else:
        return render_template("profil_bearbeiten.html")


@app.route('/profil_bearbeiten_verarbeiten', methods=['GET', 'POST'])
def profil_bearbeiten_verarbeiten():
    if request.method == "POST":
        data = request.form
        vorname = data.get('new_vorname')
        nachname = data.get('new_nachname')
        email = data.get('new_email')
        password = data.get('new_password')
        current_password = data.get('current_password')

        # check if the given 'current password' is correct
        if current_password != session["password"]:
            flash('Falsches aktuelles Passwort', 'error')
            return redirect(url_for('profil'))

        # if user is student
        if not session["is_dozent"]:
            matrikelnummer = data.get('new_matrikelnummer')
            abschluss = data.get('new_abschluss')
            studiengang = data.get('new_studiengang')
            seminar = data.get('new_seminar')
            try:
                # update user
                db_edit_student([vorname, nachname, email, password, matrikelnummer,
                                 abschluss, studiengang, seminar, str(session["login"])])
                flash('Profile updated successfully. Log in again.', 'success')
                return redirect(url_for('logout'))
            except Exception as e:
                print(e)
                flash('Something went wrong, try again.', 'error')
                return redirect(url_for('profil'))

        # if user is dozent
        else:
            try:
                db_edit_dozent([vorname, nachname, email, password, str(session["login"])])
                flash('Profile updated successfully. Log in again.', 'success')
                return redirect(url_for('logout'))
            except Exception as e:
                print(e)
                flash('Something went wrong, try again.', 'error')
                return render_template("profil.html")


@app.route('/profil_alle_studierende', methods=['GET'])
def profil_alle_studierende():
    profile = db_get_profil_alle_studierende()
    profile = [list(i) for i in profile]
    for profil in profile:
        student_id = profil[0]
        wertung = db_get_ausarbeitung_bewertung(student_id)
        if wertung == -1:
            profil.append("Noch keine Bewertung abgegeben")
        else:
            profil.append(wertung)
        note = db_get_benotung_student(student_id)
        if note == -1:
            profil.append("Noch keine Note abgegeben")
        else:
            profil.append(note)
    return render_template("profil_alle_studierende.html", profile=profile)


@app.template_global()
def db_get_dozent_by_id(dozent_id):
    if not dozent_id:
        return "Kein Dozent"
    else:
        return db_get_dozent_full_name_by_id(dozent_id)[0][0]


@app.route('/seminarthemen', methods=['GET', 'POST'])
def seminarthemen():
    headings = ["ID", "Titel", "Oberbegriff", "Beschreibung", "Semester",
                "Status", "PDF", "Dozent", "Student", "Action"]
    themen = db_get_seminarthemen_seite()
    return render_template("seminarthemen.html", headings=headings, themen=themen)


@app.route('/seminarthemen_ansicht/<int:record_id>')
def seminarthemen_ansicht(record_id):
    ansicht_daten = db_get_seminarthemen_ansicht(record_id)
    return render_template('seminarthemen_ansicht.html', ansicht_daten=ansicht_daten)


@app.route('/seminarthemen_ansicht_bearbeiten/<int:record_id>', methods=['GET', 'POST'])
def seminarthemen_ansicht_bearbeiten(record_id):
    ansicht_daten = db_get_seminarthema_by_id(record_id)
    dozenten = db_get_all_dozenten()
    return render_template("seminarthemen_ansicht_bearbeiten.html", ansicht_daten=ansicht_daten, dozenten=dozenten)


@app.route('/seminarthemen_ansicht_bearbeiten_verarbeiten', methods=['GET', 'POST'])
def seminarthemen_ansicht_bearbeiten_verarbeiten():
    data = request.form
    id = data.get('id')
    new_titel = data.get('new_titel')
    new_oberbegriff = data.get('new_oberbegriff')
    new_beschreibung = data.get('new_beschreibung')
    new_semester = data.get('new_semester')
    status = data.get('status')
    new_dozent = data.get('new_dozent')
    new_student = data.get('new_student')

    if request.files['new_file']:
        new_file = request.files['new_file']  # byte
        new_filename = new_file.filename
        new_filedata = psycopg2.Binary(new_file.read())
    else:
        current_file = db_get_current_file(id)
        new_filename = current_file[0][0]
        new_filedata = current_file[0][1]

    if not new_student or new_student == 'None':
        new_student = None
        status = 'frei'

    if new_student and status == 'frei':
        status = 'vergeben'

    try:
        data = [new_titel, new_oberbegriff, new_beschreibung, new_semester,
                status, new_filename, new_dozent, new_student, new_filedata, id]
        db_edit_seminar_thema(data)
        flash('Seminar updated successfully. Log in again', 'success')
        return redirect(url_for('logout'))
    except Exception as e:
        print(e)
        flash('Something went wrong, try again.', 'error')
        return redirect(url_for('seminarthemen'))


@app.route('/seminarthemen_ansicht_belegen/<int:record_id>', methods=['GET', 'POST'])
def seminarthemen_ansicht_belegen(record_id):
    try:
        if db_check_if_student_belegt(session["email"]):
            flash('Student ist bereits in einem laufendem Seminar.', 'error')
        else:
            db_edit_seminar_thema_belegen(["vergeben", session["email"], record_id])
            flash('Seminar erfolgreich belegt. Log in again.', 'success')
            return redirect(url_for('logout'))
    except Exception as e:
        print(e)
        flash('Something went wrong, try again.', 'error')
        return redirect(url_for('seminarthemen'))
    return redirect(url_for('seminarthemen'))


@app.route('/seminarthemen_definieren', methods=['GET', 'POST'])
def seminarthemen_definieren():
    dozenten = db_get_all_dozenten()
    user_id = session["login"]
    predefined_dozenten = []
    for dozent in dozenten:
        if dozent[1] == user_id:
            predefined_dozenten.insert(0, dozent)
        else:
            predefined_dozenten.append(dozent)
    return render_template("seminarthemen_definieren.html", dozenten=predefined_dozenten)


@app.route('/seminarthemen_definieren_verarbeiten', methods=['POST'])
def seminarthemen_definieren_verarbeiten():
    if request.method == "POST":
        data = request.form
        titel = data.get('titel')  # string
        oberbegriff = data.get('oberbegriff')  # string
        beschreibung = data.get('beschreibung')  # string
        semester = data.get('semester')  # string
        status = data.get('status')  # string
        dozent = data.get('dozent')  # email
        student = data.get('zugewiesener_student')  # string

        # check if file was uploaded
        if request.files['file']:
            file = request.files['file']  # byte
            filename = file.filename
            filedata = psycopg2.Binary(file.read())
        else:
            filename = None
            filedata = None

        if not student:
            student = None

        try:
            data = [titel, oberbegriff, beschreibung, semester, status, filename, dozent, student, filedata]
            db_add_seminar_thema(data)
            flash('New seminar theme created successfuly.', 'success')
            return redirect(url_for('seminarthemen'))
        except Exception as e:
            flash('Something went wrong, try again.', 'error')
            print(e)
            return redirect(url_for('seminarthemen_definieren'))


@app.route('/profil_studierende/<int:record_id>', methods=['GET', 'POST'])
def profil_studierende(record_id):
    # get student email using seminar_thema.id
    student_email = db_get_student_email_by_seminarthema_id(record_id)[0][0]
    # get student data using student.email
    student_data = db_get_profil_einzelne_studierende(student_email)[0]
    return render_template("profil_studierende.html", student=student_data)


@app.route('/vortrag_bewerten/<int:record_id>', methods=['GET', 'POST'])
def vortrag_bewerten(record_id):
    """
       Vortrag bewerten
       :param   record_id = int
       :return: bewerten-vortrag
       """
    return render_template("bewerten_vortrag.html", rec_id=record_id)


@app.route('/vortrag_bewerten_verabeiten/<int:record_id>', methods=['GET', 'POST'])
def vortrag_bewerten_verabeiten(record_id):
    """

       :param record_id
                Seminar ID des zu bewertenden Seminars
       :return:
       """
    if request.method == "POST":
        data = [str(request.form.get('folien'))]
        data.append(str(request.form.get('sprachlich')))
        data.append(str(request.form.get('praesentation')))
        data.append(str(request.form.get('zeitlich')))
        data.append(str(request.form.get('verstaendnis')))
        data.append(str(request.form.get('inhaltlich')))
        data.append(str(request.form.get('verknuepfung')))
        data.append(str(request.form.get('diskussion')))
        data.append(str(request.form.get('beteiligung')))
        data.append(str(request.form.get('kommentar')))
        data.append((db_get_student_matrikel_by_seminar(record_id)[0][0]))
        data.append(record_id)
        db_add_bewertung(data)
        return redirect(url_for('seminarthemen'))


@app.route('/student_bewerten/', methods=['GET'])
def student_benoten():
    """
       Vortrag bewerten
       :param   record_id = int
       :return: bewerten-student
       """
    record_id = request.args.get("record_id", type=int)
    return render_template("student_bewerten.html", record_id=record_id)


@app.route('/student_bewerten_verarbeiten/<record_id>', methods=['GET', 'POST'])
def student_benoten_verarbeiten(record_id):
    """

       :param record_id
                Seminar ID des zu bewertenden Seminars
       :return: url_for("seminarthemen)
       """
    if request.method == 'POST':
        note = request.form.get("note")
        kommentar = request.form.get("kommentar")
        data = [note, kommentar]
        student_id = db_get_student_id_by_seminar_id(record_id)
        data.append(str(student_id[0][0]))
        data.append(str(record_id))
        db_add_benotung_student(record_id, data)
        db_close_seminar(record_id)
    return redirect(url_for("seminarthemen"))


@app.route('/ausarbeitung_bewerten', methods=['GET'])
def ausarbeitung_bewerten():
    """

    :return:
    """
    record_id = request.args.get("record_id", type=int)
    return render_template("bewerten_ausarbeitung.html", record_id=record_id)


@app.route('/ausarbeitung_bewerten_verarbeiten/<seminar_id>', methods=['POST'])
def ausarbeitung_bewerten_verarbeiten(seminar_id):
    """ Verarbeiten der Bewertung der Ausarbeitung

    :return: url_for("seminarthemen)
    """
    if request.method == 'POST':
        umfang = request.form.get("umfang")
        referenz = request.form.get("referenz")
        sprachlich = request.form.get("sprachlich")
        inhaltlich = request.form.get("inhaltlich")
        schwierigkeit = request.form.get("schwierigkeit")
        kommentar = request.form.get("kommentar")
        data = [umfang, referenz, sprachlich, inhaltlich, schwierigkeit, kommentar]
        student_id = db_get_student_id_by_seminar_id(seminar_id)
        data.append(str(student_id[0][0]))
        data.append(seminar_id)
        db_add_ausarbeitung_bewertung(data)
        flash(Markup(
            'Bewertung erfolgreich abgegeben!'
        ))
    return redirect(url_for("seminarthemen"))


if __name__ == '__main__':
    app.run()
