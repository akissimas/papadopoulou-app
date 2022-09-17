import random
import sys
from time import sleep
from MyRequest import MyRequest
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QLineEdit, QPushButton, QLabel, \
    QHBoxLayout, QGridLayout, QStyleFactory, QPlainTextEdit, QMessageBox, QGroupBox

BUTTON_SIZE_X = 640
BUTTON_SIZE_Y = 480
LINE_EDIT_WIDTH = 120


# Step 1: Create a worker class
class Worker(QObject):
    update_progress = pyqtSignal(str)
    worker_complete = pyqtSignal(int)
    error_message = pyqtSignal(str)

    def __init__(self, my_request, reps, pause_btn_reps, pause_after_reps):
        super(Worker, self).__init__()
        self.my_request = my_request
        self.reps = reps
        self.pause_btn_reps = pause_btn_reps
        self.pause_after_reps = pause_after_reps
        self.flag = False

    def run(self):
        counter = 0
        while not self.flag:
            for i in range(self.reps):
                if self.flag:
                    break

                # send request
                error = self.my_request.send_request()

                # print error message if exception occurrence
                if error == 0:
                    self.error_message.emit('Invalid URL')
                    self.worker_complete.emit(counter)
                    return
                elif error == 1:
                    self.error_message.emit('missing/invalid Schema')
                    self.worker_complete.emit(counter)
                    return
                elif error == 2:
                    self.error_message.emit('connection/HTTP error')
                    self.worker_complete.emit(counter)
                    return

                self.update_progress.emit(self.my_request.get_result(counter + 1))

                counter += 1

                # in the last rep don't use sleep
                if i == self.reps - 1:
                    break
                sleep(random.uniform(self.pause_btn_reps, self.pause_btn_reps + 3))

            if self.flag:
                break
            sleep(random.uniform(self.pause_after_reps, self.pause_after_reps + 3))


        # if you press the stop button before loop ends
        if self.flag:
            # reset flag
            self.flag = False
            # how many requests were made
            self.worker_complete.emit(counter)
            return

        # how many requests were made
        self.worker_complete.emit(counter + 1)

    def stop(self):
        self.flag = True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stop_flag = False
        self.worker = None
        self.file_worker = None
        self.thread = None
        self.thread2 = None
        self.total_requests = 0

        self.data_from_file = self.read_from_file()


        # url
        self.url_label = QLabel("url:")
        self.url_field = QLineEdit(self.data_from_file[0])

        # answer
        self.answer_label = QLabel("answer:")
        self.answer_field = QLineEdit(self.data_from_file[1])

        # name
        self.name_label = QLabel("name:")
        self.name_field = QLineEdit(self.data_from_file[2])

        # surname
        self.surname_label = QLabel("surname:")
        self.surname_field = QLineEdit(self.data_from_file[3])

        # phone
        self.phone_label = QLabel("phone:")
        self.phone_field = QLineEdit(self.data_from_file[4])

        # email
        self.email_label = QLabel("email:")
        self.email_field = QLineEdit(self.data_from_file[5])

        # number of repetitions
        self.num_of_reps_label = QLabel("repetitions:")
        self.num_of_reps_field = QLineEdit()
        if self.data_from_file[6] == '':
            self.num_of_reps_field.setText(str(0))
        else:
            self.num_of_reps_field.setText(self.data_from_file[6])

        # pause between repetitions
        self.pause_of_reps_label = QLabel("pause time between reps:")
        self.pause_of_reps_field = QLineEdit(self.data_from_file[7])
        if self.data_from_file[7] == '':
            self.pause_of_reps_field.setText(str(0))
        else:
            self.pause_of_reps_field.setText(self.data_from_file[7])

        # pause after repetitions
        self.pause_after_reps_label = QLabel("pause after reps:")
        self.pause_after_reps_field = QLineEdit(self.data_from_file[8])
        if self.data_from_file[8] == '':
            self.pause_after_reps_field.setText(str(0))
        else:
            self.pause_after_reps_field.setText(self.data_from_file[8])

        # total requests
        if self.data_from_file[9]:
            self.total_requests += int(self.data_from_file[9])

        # logs area
        self.logs = QPlainTextEdit()

        # buttons
        self.start_btn = QPushButton("start")
        self.stop_btn = QPushButton("stop")
        self.stop_btn.setEnabled(False)
        self.clear_btn = QPushButton("clear")
        self.save_btn = QPushButton("save preset")

        # set gui
        self.setup_ui()

        # events
        # start button
        self.start_btn.clicked.connect(self.submit_data)

        # clear button
        self.clear_btn.clicked.connect(self.clear_logs)

        # stop button
        self.stop_btn.clicked.connect(self.stop_button_pressed)

        # save button
        self.save_btn.clicked.connect(self.save_to_file)

    # enter pressed
    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Return, Qt.Key_Enter] and self.start_btn.isEnabled():
            self.submit_data()

    def setup_ui(self):
        self.setWindowTitle("Papadopoulou app")
        self.setWindowIcon(QIcon('images/logo.png'))
        self.setGeometry(400, 400, 500, 300)
        self.setFixedSize(680, 480)

        # url
        url_layout = self.create_field(self.url_label, self.url_field, 250, QHBoxLayout())

        # write your answer
        answer_layout = self.create_field(self.answer_label, self.answer_field, LINE_EDIT_WIDTH, QHBoxLayout())

        # name
        name_layout = self.create_field(self.name_label, self.name_field, LINE_EDIT_WIDTH, QHBoxLayout())

        # surname
        surname_layout = self.create_field(self.surname_label, self.surname_field, LINE_EDIT_WIDTH, QHBoxLayout())

        # phone
        phone_layout = self.create_field(self.phone_label, self.phone_field, LINE_EDIT_WIDTH, QHBoxLayout())

        # email
        email_layout = self.create_field(self.email_label, self.email_field, LINE_EDIT_WIDTH, QHBoxLayout())

        # number of repetitions
        num_of_reps_layout = self.create_field(self.num_of_reps_label, self.num_of_reps_field, 30,
                                               QHBoxLayout())

        # pause between repetitions
        pause_of_reps_layout = self.create_field(self.pause_of_reps_label, self.pause_of_reps_field, 30,
                                                 QHBoxLayout())

        # pause after repetitions
        pause_after_reps_layout = self.create_field(self.pause_after_reps_label, self.pause_after_reps_field, 30,
                                                    QHBoxLayout())

        # logs area
        self.logs.setReadOnly(True)
        self.logs.setStyleSheet("margin: 5px 0px 5px 0px")

        # buttons
        self.save_btn.setGeometry(0, 0, 640, 480)
        self.save_btn.setMaximumSize(84, 90)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addWidget(self.stop_btn)
        buttons_layout.addWidget(self.clear_btn)

        # set layout
        layout = QGridLayout()

        # set top groupBox
        top_groupbox = QGroupBox()
        layout.addWidget(top_groupbox)

        top_layout = QGridLayout()
        top_groupbox.setLayout(top_layout)

        # url
        top_layout.addLayout(url_layout, 0, 1, alignment=Qt.AlignHCenter)

        # answer
        top_layout.addLayout(answer_layout, 1, 1, alignment=Qt.AlignHCenter)

        # elements
        top_layout.addLayout(name_layout, 2, 0, alignment=Qt.AlignHCenter)
        top_layout.addLayout(surname_layout, 2, 2)
        top_layout.addLayout(phone_layout, 3, 0, alignment=Qt.AlignHCenter)
        top_layout.addLayout(email_layout, 3, 2)
        top_layout.addLayout(num_of_reps_layout, 4, 0)
        top_layout.addLayout(pause_of_reps_layout, 4, 1)
        top_layout.addLayout(pause_after_reps_layout, 4, 2)

        # set bottom groupBox
        bottom_groupbox = QGroupBox()
        layout.addWidget(bottom_groupbox)

        bottom_layout = QGridLayout()
        bottom_groupbox.setLayout(bottom_layout)

        # logs
        bottom_layout.addWidget(self.logs, 0, 0, 1, 3)
        # buttons
        bottom_layout.addWidget(self.save_btn, 1, 0)
        bottom_layout.addLayout(buttons_layout, 1, 2)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    @staticmethod
    def create_field(label, field, size, Qlayout):
        field.setFixedWidth(size)

        layout = Qlayout
        layout.addWidget(label, alignment=Qt.AlignRight)
        layout.addWidget(field, alignment=Qt.AlignLeft)

        return layout

    def submit_data(self):
        data, values_of_reps = self.get_fields_text()

        # check if the user has given valid data
        if self.data_validation_check(data, values_of_reps):
            return

        #  enable stop button
        self.stop_btn.setEnabled(True)

        url = data[0]

        payload = dict(firstname=data[2], lastname=data[3], pmsg=data[1], phone=data[4], email=data[5])

        my_request = MyRequest(url, payload)

        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker(my_request, int(values_of_reps[0]), int(values_of_reps[1]), int(values_of_reps[2]))
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.worker_complete.connect(self.thread.quit)
        self.worker.worker_complete.connect(self.worker.deleteLater)
        self.worker.worker_complete.connect(self.evt_worker_finished)
        self.worker.update_progress.connect(self.evt_update_progress)
        self.worker.error_message.connect(self.evt_error_message)

        # Step 6: Start the thread
        self.thread.start()

        # Final resets
        self.start_btn.setEnabled(False)  # disable start button
        self.thread.finished.connect(
            lambda: self.start_btn.setEnabled(True)
        )

    def evt_update_progress(self, response):
        self.logs.appendPlainText(response + '\n')

    def evt_worker_finished(self, requests):
        #  disable stop button
        self.stop_btn.setEnabled(False)
        self.total_requests += requests
        self.logs.appendPlainText(f"requests: {requests}\ntotal requests: {self.total_requests}\n\n")

    def evt_error_message(self, err_msg):
        QMessageBox.information(self, 'Error', err_msg, QMessageBox.Ok)
        #  enable start button
        self.start_btn.setEnabled(True)
        #  disable stop button
        self.stop_btn.setEnabled(False)

    def get_fields_text(self):
        data = [self.url_field.text(), self.answer_field.text(), self.name_field.text(),
                self.surname_field.text(), self.phone_field.text(),
                self.email_field.text()]

        values_of_reps = [self.num_of_reps_field.text(), self.pause_of_reps_field.text(), self.pause_after_reps_field.text()]

        return data, values_of_reps

    def data_validation_check(self, data, values_of_reps):
        # if personal info fields are empty
        for index in data:
            if index == '' or index.isspace():
                QMessageBox.information(self, 'Missing data', 'Fill in all blank fields', QMessageBox.Ok)
                return True

        for index in values_of_reps:
            if not index.isnumeric():
                QMessageBox.information(self, 'Missing data',
                                        f'Fields ({self.num_of_reps_label.text()}), ({self.pause_of_reps_label.text()}) and ({self.pause_after_reps_label.text()}) must be only numbers and greater than 0',
                                        QMessageBox.Ok)
                return True

        # if last fields have values of 0
        if int(values_of_reps[0]) == 0 or int(values_of_reps[1]) == 0 or int(values_of_reps[2]) == 0:
            QMessageBox.information(self, 'Missing data',
                                    f'Fields ({self.num_of_reps_label.text()}), ({self.pause_of_reps_label.text()}) and ({self.pause_after_reps_label.text()}) must be only numbers and greater than 0',
                                    QMessageBox.Ok)
            return True

    def stop_button_pressed(self):
        try:
            self.worker.stop()
        except AttributeError:
            pass

    def clear_logs(self):
        self.logs.clear()

    def save_to_file(self):
        data, values_of_reps = self.get_fields_text()

        with open('auto_field_completion.txt', 'w') as writer:
            for i in (data, values_of_reps):
                print(*i, sep='\n', file=writer)

            writer.write(str(self.total_requests))

        QMessageBox.information(self, 'Save', "Preset saved", QMessageBox.Ok)

    @staticmethod
    def read_from_file():
        try:
            with open('auto_field_completion.txt', 'r') as reader:
                data_from_file = [line.rstrip() for line in reader]
                return data_from_file
        except FileNotFoundError:
            return [''] * 9 + ['0']

    def closeEvent(self, event=None):
        self.stop_button_pressed()

        choice = QMessageBox.question(self, 'Save',
                                      "Do you want to save your preset?",
                                      QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.save_to_file()
            sys.exit()
        else:
            pass


if __name__ == "__main__":
    # create window
    app = QApplication([])

    app.setStyle(QStyleFactory.create('fusion'))

    window = MainWindow()
    window.show()  # launch window

    sys.exit(app.exec_())
