import re


class UserInput:
    def __init__(self):
        self.user_responses = {
        "pipeline_choice": None,
        "dest_proj": None,
        "dest_task": None,
        "sof": None,
    }

    def show(self):
        print(self.user_responses)

    def is_valid_gl(self, text):
        if bool(re.fullmatch(r"[A-Za-z]{2}\d{4}", text)):
            return True
        if bool(re.fullmatch(r"[A-Za-z]{1}\d{5}", text)):
            return True

    def is_valid_project(self, text):
        if bool(re.fullmatch(r"[A-Za-z]{3}\d{5}", text)):
            return True
        if bool(re.fullmatch(r"[A-Za-z]{1}\d{1}[A-Za-z]{1}\d{5}", text)):
            return True

    def is_valid_task(self, text):
        if bool(re.fullmatch(r"[A-Za-z]{2}\d{2}\.[A-Za-z0-9]{2}", text)):
            return True
        if bool(re.fullmatch(r"[A-Za-z]{1}\d{3}.[A-Za-z0-9]{2}", text)):
            return True

    def get_pipeline(self):
        pipeline_choice = input(
            "\n\n"
            "   Choose the type of process you need to run: \n"
            "\n"
            "   1. Project to Project journal\n"
            "   2. Project to GL journal\n"
            "   3. Expenditure type changes\n\n"
            "   Enter your selection and press enter: ",
        )

        while pipeline_choice not in ["1", "2", "3"]:
            pipeline_choice = input(
                "\n\n"
            "   Choose a valid process to run:  \n"
            "\n"
            "   1. Project to Project journal\n"
            "   2. Project to GL journal\n"
            "   3. Expenditure type changes\n\n"
            "   Enter your selection and press enter: ",
            )
        self.user_responses["pipeline_choice"] = pipeline_choice

    def pipeline_specific_choices(self):
        if self.user_responses["pipeline_choice"] == "1":
            # print(f"chose: {self.pipeline}")
            self.user_responses["dest_proj"] = input("\n   Enter an 8 digit destination project and press enter: ").strip().upper()
            while self.is_valid_project(self.user_responses["dest_proj"]) is not True:
                self.user_responses["dest_proj"] = input("   Enter a valid 8 digit destination project and press enter: ").strip().upper()
            self.user_responses["dest_task"] = input('   Enter a task number (e.g. "XXXX.XX") and press enter: ').strip().upper()
            while self.is_valid_task(self.user_responses["dest_task"]) is not True:
                self.user_responses["dest_task"] = input('   Enter a valid task number (e.g. "XXXX.XX") and press enter: ').strip().upper()


        elif self.user_responses["pipeline_choice"] == "2":
            # print(f"chose: {self.pipeline}")
            self.user_responses["dest_proj"] = input("\n   Enter a 6 digit destination GL (6 character) and press enter: ").strip().upper()
            while self.is_valid_gl(self.user_responses["dest_proj"]) is not True:
                self.user_responses["dest_proj"] = input("   Enter a valid 6 character destination GL and press enter: ").strip().upper()
            self.user_responses["sof"] = input("   Enter Source of funds if required (5 characters). Press enter to accept default 00000: ").strip().upper()
            if self.user_responses["sof"] == "":
                self.user_responses["sof"] = "00000"
            while len(self.user_responses["sof"]) != 5:
                self.user_responses["sof"] = input("   Enter valid source of funds (5 characters). Press enter to accept default 00000: ").strip().upper()
                if not self.user_responses["sof"]:
                    self.user_responses["sof"] = "00000"

        elif self.user_responses["pipeline_choice"] == "3":
            pass


        print("\n\n    Beginning process...")
        # self.show()
