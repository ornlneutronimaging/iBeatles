class CheckError(object):
    delay = 10000  # microseconds the message will be displayed in status bar

    def __init__(self, parent=None):
        self.parent = parent

        self.check_step1()

    def check_step1(self):
        self.check_file_errors()

    def check_file_errors(self):
        step = "step1"
        message = "Number of Data and OB files NOT compatible!"

        nbr_data_file = len(self.parent.list_files["sample"])

        if nbr_data_file == 0:
            return

        nbr_ob_file = len(self.parent.list_files["ob"])
        if nbr_ob_file == 0:
            return

        if not (nbr_data_file == nbr_ob_file):
            self.save_and_report_message(step=step, message=message, status=True)
            return

        self.save_and_report_message(step=step, message="", status=False)

    def save_and_report_message(self, **kwargs):
        self.save_report(**kwargs)
        self.report_message(step=kwargs["step"])

    def save_report(self, step="step1", message="", status=False):
        steps_error = self.parent.steps_error
        steps_error[step]["status"] = status
        steps_error[step]["message"] = message
        self.parent.steps_error = steps_error

    def report_message(self, step="step1"):
        steps_error = self.parent.steps_error
        if steps_error[step]["status"]:
            _message = steps_error[step]["message"]
            self.parent.ui.statusbar.showMessage(_message, self.delay)
