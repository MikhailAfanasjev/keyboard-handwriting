from matplotlib import pyplot
import utils

def read_sqlite_table():  # вывод данных из бд
    global cursor, sqlite_connection
    try:
        sqlite_connection = sqlite3.connect('db/DB.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sqlite_select_query = """SELECT * from user"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        print("Всего строк:  ", len(records))
        print("Вывод каждой строки")
        for row in records:
            print("password:", row[0])
            print("vector:", row[1])

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")

    read_sqlite_table()
    # return row
    # main_frame.tableWidget.setText(row)


def connect_interface_handlers(main_frame, gp_dialog):
    def set_password(*args, **kwargs):
        utils.password = main_frame.SetPasswordInput.text()
        utils.key_list = None
        complexity = utils.check_password_complexity(utils.password)
        main_frame.ComplexityPasswordLabel.setText(str(complexity))

    old_press_event = main_frame.TestPasswordInput.keyPressEvent
    old_release_event = main_frame.TestPasswordInput.keyReleaseEvent
    utils.key_list = None
    utils.vectors = []
    utils.reg_counter = 0

    main_frame.labelRegCounter.setText("0 / 10")
    main_frame.PasswordStatusLabel.setText("")

    def press_key_test_password(event, *args, **kwargs):
        if utils.key_list is None:
            utils.key_list = utils.KeyList()
        utils.key_list.press(event.key())
        return old_press_event(event)

    def release_key_test_password(event, *args, **kwargs):
        utils.key_list.release(event.key())
        return old_release_event(event)

    def analyse(*args, **kwargs):
        if utils.password != main_frame.TestPasswordInput.text():
            main_frame.PasswordStatusLabel.setText("Несовпадение пароль")
            return
        key_list = utils.key_list
        utils.key_list = None
        series = key_list.serialize()

        apt = key_list.average_pressing_time
        main_frame.PasswordStatusLabel.setText(
            f"Пересечения 1K-2K-1K-2K: {key_list.intersections_1212}\n"
            f"Пересечения 1K-2K-2K-1K: {key_list.intersections_1221}\n"
            f"Среднее время удержания клавиши: {apt.microseconds / 10**6 + apt.seconds}c"
        )
        main_frame.PasswordStatusLabel.adjustSize()

        main_frame.TestPasswordInput.setText("")

        for key in series:
            time = (key["start"], key["end"])
            char_num = (key["key"], key["key"])
            pyplot.plot(time, char_num, color="#1f77b4")
        pyplot.show()

    def show_gp_dialog(*args, **kwargs):
        gp_dialog.show()

    main_frame.SetPasswordInput.editingFinished.connect(set_password)
    main_frame.TestPassword.clicked.connect(analyse)
    main_frame.pushButtonGenerate.clicked.connect(show_gp_dialog)
    main_frame.TestPasswordInput.keyPressEvent = press_key_test_password
    main_frame.TestPasswordInput.keyReleaseEvent = release_key_test_password

    def generate_password(*args, **kwargs): # генерация пароля
        password = utils.generate_password(
            gp_dialog.spinBoxLen.value(),
            gp_dialog.checkBoxUpper.isChecked(),
            gp_dialog.checkBoxLower.isChecked(),
            gp_dialog.checkBoxDigits.isChecked(),
            gp_dialog.checkBoxSpec.isChecked(),
        )
        main_frame.SetPasswordInput.setText(password)
        set_password(*args, **kwargs)
        gp_dialog.close()

    gp_dialog.pushButtonGenerate.clicked.connect(generate_password)

    def registrate(*args, **kwargs):
        if utils.password != main_frame.TestPasswordInput.text():
            main_frame.PasswordStatusLabel.setText("Несовпадение паролей")
            return
        key_list = utils.key_list
        utils.key_list = None
        main_frame.TestPasswordInput.setText("")

        vector = key_list.time_vector
        utils.vectors.append(vector)
        utils.reg_counter += 1

        if utils.reg_counter < 20:
            main_frame.labelRegCounter.setText(f"{utils.reg_counter} / 20")
        else:
            utils.register_password()
            utils.reg_counter = 0
            utils.vectors = list()
            main_frame.labelRegCounter.setText("0 / 20")

    def authenticate(*args, **kwargs):
        password = main_frame.TestPasswordInput.text()

        vector = utils.key_list.time_vector
        utils.key_list = None
        main_frame.TestPasswordInput.setText("")

        res = utils.check_password(password, vector)

        main_frame.PasswordStatusLabel.setText(f"{res[0]}/{res[1]} {'Получилось' if res[2] else 'Не получилось'}")

    main_frame.pushButtonRegiter.clicked.connect(registrate)
    main_frame.pushButtonAuthenificate.clicked.connect(authenticate)

    old_event = main_frame.horizontalSliderSensetivity.sliderChange

    def change_sensitivity(*args, **kwargs):
        utils.password_check_sensitivity = main_frame.horizontalSliderSensetivity.value() / 100
        #return old_event(*args, **kwargs)

    main_frame.horizontalSliderSensetivity.valueChanged.connect(change_sensitivity)
