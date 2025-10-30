# AppContext is holding COMMON objects in one place. 
# Think of it like a box / wrapper
# We create the class AppContenxt. We fill it with other
# classes. Then when we initiliase AppContext, all
# the other classes are initiliased also and are available
# through this class.

# Instantiate AppContext have access to Filemanager, DataManager etc etc

# Not the bootstrap method also. This is a great way or running any methods
# early on that may be required for set-up or data prep


from modules.filemanager import FileManager
from modules.datamanager import DataManager
# from modules.journalhelper import JournalHelpers
from modules.userinput import UserInput
from modules.totals import Totals



class AppContext:
    def __init__(self):
        self.fm = FileManager()
        self.dm = DataManager()
        # self.jh = JournalHelpers()
        self.ui = UserInput()
        self.tt = Totals()
        self._bootstrapped = False
        self.paths = []
        self.journal = None
        self.data = None
        self.headings = None
        self.start_time = None
        self.end_time = None

    def bootstrap(self):
        # if self._bootstrapped:
        #     return self
        base_path = self.fm.get_base_path()
        self.paths = self.fm.get_file_paths(base_path)
        self.fm.check_files_are_closed(self.paths)
        data_path = self.paths[1]
        workbook_ref = self.fm.open_with_openpyxl(data_path)
        self.data = self.dm.get_data_from_workbook(workbook_ref)
        self.headings = self.data[0]
        self.dm.check_for_disallowed(self.data)
        report_type = self.dm.determine_input_report_type(self.headings)

        self._bootstrapped = True
        return self
