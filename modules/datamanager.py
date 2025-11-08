import getpass
from datetime import datetime

from modules.disallowed import disallowed
from modules.headers import data_identity, mappings
from modules.naturalaccounts import natural_accounts
from modules.unit_dict import unit_dict


class DataManager:
    def __init__(self):
        self.full_data = None
        self.headers = None
        self._loaded = False
        self.report_type = None
        self.uploader_ref = None

    # def load(self, workbook):
    #     rows = self.get_data_from_workbook(workbook)
    #     self.full_data = rows
    #     self.headers = rows[0] if rows else []
    #     self._loaded = True
    #     return self

    def get_data_from_workbook(self, workbook):
        """Gets all data rows from the given data workbook reference
        input: Data workbook ref
        output: full_data
        """
        # Essentially finds a BOUNDING BOX of where the data is. By finding
        # the first empty row and column we have a co-ord in conjunction
        # with cell A1 where the data is
        try:
            data_sheet = workbook.worksheets[0]

            max_row = 0
            max_col = 0
            # uses openpyxl .iter_rows() method
            for row in data_sheet.iter_rows():
                for cell in row:
                    if cell.value not in (None, ""):
                        max_row = max(max_row, cell.row)
                        max_col = max(max_col, cell.column)
            if max_row > 1000 + 1:
                raise ValueError(
        f"\n    [!] Error: Too many rows in data file ({max_row} rows).\n"
        f"    Please reduce the number of rows (inc headers) to 1001 or fewer.\n",
    )


            # openpyxl iterates cell by cell, NOT BY RANGE
            # so we have to populate our full_data list on that basis with a call
            # # to iter_rows
            self.full_data = [
                [cell.value for cell in row]
                for row in data_sheet.iter_rows(
                    min_row=1, min_col=1, max_row=max_row, max_col=max_col,
                )
            ]
        finally:
            workbook.close()
        return self.full_data

    # def _require_loaded(self):
    #     if not self._loaded:
    #         raise RuntimeError("Call dm.load_from_rows() first.")

    def check_for_disallowed(self, data):
        """Check for any disallowed expenditure types in the source data
        Gets the index of either of the expenditure columsn dependant on the source
        and scans that column for disallowed types against a dict. Will raise an
        excpetion and exit the program if it finds a disallowed type
        input: data
        output: none
        """
        disallowed_types = []
        exp_header_column = None
        headers = data[0]
        # print(headers)
        column_to_check = ["Expenditure Type", "Expnd Type"]
        for column in column_to_check:
            # print(column)
            if column in headers:
                exp_header_column = headers.index(column)
        # print(exp_header_column)

        if exp_header_column == None:
            raise IndexError("    [!] Could not find the expenditure column to check")
        for row in data[1:]:
            # print(row[exp_header_column])
            if row[exp_header_column] in disallowed:
                # print(row)
                disallowed_types.append(row[exp_header_column])

            if len(disallowed_types) > 0:
                disallowed_str = "\n        ".join(str(item) for item in disallowed_types)
                raise RuntimeError(
                    f"\n    [!] - Found cost types we shouldn't move in the input data:\n"
                    f"\n          {disallowed_str}\n",
                )

    def determine_input_report_type(self, headings):
        """Determines if the input data is from an Oracle dump or a
        Splash BI outpur by checking the headers

        input: headings list
        output: type of report as a string Oracle or Splash_BI
        """
        # print(headings)
        for key in data_identity:
            if key in headings:
                self.report_type = data_identity[key]
                return self.report_type

    def filter_data_to_journal_headings(self, full_data):
        """Method to create a list of data corresponding to the headings in the journal
        It matches the headings from the journal to the dataset using the dict
        However it also creates the filtered data with the headings FROM THE JOURNAL
        rather than the headings from the data - which is easier to look up from

        """
        #
        # Get the journal_headers as a list from the keys
        journal_headers = list(mappings[self.report_type].keys())
        column_indexes = [full_data[0].index(header) for header in mappings[self.report_type].values()]
        # print(column_indexes)
        # write the journal headers to the new list
        # not the * to UNPACK the rest of the list comprehension i.e. discard 1 level of nesting
        filtered_data = [
            journal_headers,
            *[
                [row[column_index] for column_index in column_indexes]
                for row in full_data[1:]
            ],# Loop over rows but skip original header row
        ]
        return filtered_data

    def clean_journal(self, journal):
        """Utility to clean out the journal or previous data
        Clears up to row 2015 on the web adi to pr
        
        """
        try:
            webadi = journal.sheets["WebADI"]
            webadi.range("B12:L2015").clear_contents()
            webadi.range("E7").merge_area.clear_contents()
            webadi.range("E8").merge_area.clear_contents()
            sheets_to_reset = ["Data", "Backups_"]
            for sheet_name in sheets_to_reset:
                if sheet_name in [s.name for s in journal.sheets]:
                    # print(f"found: {sheet_name}, deleting")
                    journal.sheets[sheet_name].delete()
                journal.sheets.add(
                    name=sheet_name, after=journal.sheets[-1],
                )
        except Exception as e:
            raise ValueError(
                f"\n[!] Error: {e}.\n    Issue in journal_clean function\n",
            )

    def datetimes_to_strings(self, filtered_data):
        """Openpyxl pulls in dates as datetimes but they need to be written as
        strings to the jounral. Re-format them and overwrites the source data
        as we don't need datetimes in the future - ok to lose them here.

        input: filtered data
        output: filtered data with string based dates
        """
        column_index = filtered_data[0].index("Expnd Item Date")
        for row in filtered_data[1:]:
            formatted_date = row[column_index].strftime("%d-%b-%Y")
            row[column_index] = formatted_date
            # print(filtered_data)
        return filtered_data

    def build_coding_string(self, unit):
        """Build the coding string. Hardcoded some values as they never change
        for this scenario
        input: unit
        output: formatted string
        """
        cost_centre = f"{unit}9970"
        account = "61110"
        activity = "00"
        source = "00000"
        organisation = "10"
        future = "000000"
        return f"{cost_centre}.{account}.{activity}.{source}.{organisation}.{future}"


    def build_coding_string_gl(self, ctx, natural_account):
        """Builds coding strings for the p to gl scenario. These strings reflect
        the natural account from each expenditure type and the sof value

        input: ctx
        output: formatted string
        """
        # print(f"AN: {natural_account}")
        cost_centre = f"{ctx.ui.user_responses['dest_proj']}"
        # print(cost_centre)
        account = natural_accounts[natural_account]
        activity = "00"
        source = ctx.ui.user_responses["sof"]
        organisation = "10"
        future = "000000"
        return f"{cost_centre}.{account}.{activity}.{source}.{organisation}.{future}"


    def get_project_and_task_columns_for_exp_change(self, filtered_data):
        """Gets the project and task numbers from the data - useful for the
        expenditure type change method as we can't use the user input
        project and task - must be the same as the source in this instance

        input: filtered_data
        output: tuple with the 2 pieces of data 
        """
        project_column = []
        task_column = []
        idx = filtered_data[0].index("Project Number")
        for row in filtered_data[1:]:
            project_column.append(row[idx])
        idx = filtered_data[0].index("Task Number")
        for row in filtered_data[1:]:
            task_column.append(row[idx])
        return (project_column, task_column)


    def build_credit_rows(self, date_formatted_filtered_data, ctx):
        """Builds up the rows of credit information. Looks overly
        complex but the alternative is to break it up further
        when the steps within are easy to understand, there's just
        a lot of them. 

        input: filtered_data, ctx
        output: mutated filtered_data
        """
        selectors = {"1": "build_coding_string",
                    "2": "build_coding_string_gl",
                    "3": "build_coding_string"}
        # print(f"User Responses: {ctx.ui.user_responses}")
        source_proj = date_formatted_filtered_data[1][0]
        # print(f"SP: {source_proj}")
        source_task = date_formatted_filtered_data[1][1]
        coding_string_type = selectors[ctx.ui.user_responses["pipeline_choice"]]
        unit = date_formatted_filtered_data[1][0]
        unit = unit[:2]

        # per column tweaks ##############################################
        column_index = date_formatted_filtered_data[0].index("Quantity")
        for row in date_formatted_filtered_data[1:]:
            row[column_index] = row[column_index] * - 1
        for i, row in enumerate(date_formatted_filtered_data):
            date_formatted_filtered_data[i] = row[:-1]
        # add new column for Category DFF
        date_formatted_filtered_data[0].append("Category DFF")

        # This section calls the correct coding string method dependant on the
        # pipeline choice. Since pipeline 2 won't have a debit section, we
        # take the opportunit to add in the comments here
        exp_type_column = date_formatted_filtered_data[0].index("Expnd Type")
        method = getattr(self, coding_string_type)
        pipeline_choice = ctx.ui.user_responses["pipeline_choice"]
        if pipeline_choice == "1":
            for row in date_formatted_filtered_data[1:]:
                row.append(method(unit))
            return date_formatted_filtered_data
        if pipeline_choice == "2":
            for row in date_formatted_filtered_data[1:]:
                row.append(method(ctx, row[exp_type_column]))
            column_index = date_formatted_filtered_data[0].index("Expnd Comment")
            for row in date_formatted_filtered_data[1:]:
                row[column_index] = f"From {source_proj}.{source_task} S/C: {row[column_index]}"
            return date_formatted_filtered_data
        if pipeline_choice == "3":
            for row in date_formatted_filtered_data[1:]:
                row.append(method(unit))
            return date_formatted_filtered_data


    def build_debit_rows(self, credit_rows, full_data, dest_project=None, dest_task=None, project_col=None, task_col=None, pipeline=None):
        """Builds the debit rows. It's a large fucntion but given the simplicity of the steps
        it felt easier to have them in one place
        
        """
        # print(f"CREDIT ROWS: {credit_rows}")
        # get the source form the data - not from user inputs
        source_proj = credit_rows[1][0]
        # print(f"SP: {source_proj}")
        source_task = credit_rows[1][1]
        # print(f"ST: {source_task}")

        if pipeline == "3":
            # print(f"project_col {project_col[1][:2]}")
            exp_unit = project_col[0][:2]
        # get the correct column dependant on the input type
        if self.report_type == "Splash_BI":
            trans_id_column = full_data[0].index("Trans ID")
        elif self.report_type == "Oracle":
            trans_id_column = full_data[0].index("Trans Id")
        trans_ids = []


        comments_column = credit_rows[0].index("Expnd Comment")
        comments = []
        # get the comments column in a list
        for row in credit_rows[1:]:
            comments.append(row[comments_column])
        # print(comments)
        # get the trans_ids in a list
        for row in full_data[1:]:
            trans_ids.append(row[trans_id_column])
        # print(trans_ids)
        # get the 2 char unit code
        if dest_project is not None:
            dest_unit = dest_project[:2]

        # set the quanitity to positive value again

        column_index = credit_rows[0].index("Quantity")
        for row in credit_rows[1:]:
            row[column_index] = row[column_index] * - 1
        # insert the destination project number

        column_index = credit_rows[0].index("Project Number")
        if str(pipeline).strip() == "3":
            for i, row in enumerate(credit_rows[1:]):
                row[column_index] = project_col[i]
        else:
            for row in credit_rows[1:]:
                row[column_index] = dest_project

        column_index = credit_rows[0].index("Expnd Type")
        if str(pipeline).strip() == "3":
            for row in credit_rows[1:]:
                row[column_index] = ""

        # insert the destination task number
        column_index = credit_rows[0].index("Task Number")
        if str(pipeline).strip() == "3":
            for i, row in enumerate(credit_rows[1:]):
                row[column_index] = task_col[i]
        else:
            for row in credit_rows[1:]:
                row[column_index] = dest_task
        # concat the comments
        column_index = credit_rows[0].index("Expnd Comment")
        for i, row in enumerate(credit_rows[1:]):
            # credit_rows[column_index] = f'From {source_proj}.{source_task} S/C: {row[column_index]} trans_id: {trans_ids[trans_id_column]}'
            row[column_index] = f"Trans: {trans_ids[i]} From {source_proj}.{source_task} S/C: {row[comments_column]}"


        column_index = credit_rows[0].index("Category DFF")
        if str(pipeline).strip() == "3":
            for row in credit_rows[1:]:
                row[column_index] = self.build_coding_string(exp_unit)
        else:
            for row in credit_rows[1:]:
                row[column_index] = self.build_coding_string(dest_unit)
        return credit_rows

    def write_unit_header(self, dest_task, journal):
        # print(dest_task)
        unit_name = None
        unit_code = dest_task[:2]
        webadi = journal.sheets["WebADI"]
        if unit_code in unit_dict:
            unit_name = unit_dict[unit_code]
            webadi.range("E7").value = f"{unit_name}"
        else:
            webadi.range("E7").value = "Invalid Unit"

    def financial_column_data_only(self, data):

        financial_data = []
        column_index = data[0].index("Quantity")
        for row in data[1:]:
            financial_data.append(row[column_index])
        return financial_data


    def summary_info(self, credits, ctx, debits=None):
        """Collates the total value of the lines moved and checks they net to zero where
        appropriate. For gl's, lets you know how much is being moved. 

        input: credits(all credit values in a list), optional debits in a list
        output: f string 
        
        """
        total = 0
        if debits == None:
            for i in range(len(credits)):
                total += credits[i]
            return f"""
        Credit {len(credits)} lines
        Total: {round(total,2)}
        Time taken: {round(ctx.end_time - ctx.start_time, 2)}"""
        if debits:
            for i in range(len(credits)):
                total += (credits[i] + debits[i])
            return f"""    
        Credit {len(credits)} lines
        Debit {len(debits)} lines
        Net zero check: {round(total,2)}
        Time taken: {round(ctx.end_time - ctx.start_time, 2)}"""

    def write_uploader_ref(self, dest_proj, journal):
        """Creates and writes a valid uploader ref to the journal based on the users
        windows username (pick ther initials) , the unit and the date. Adds in XXX
        prompting user to enter sequence number as theres no way of being able to 
        know this

        input, dest_proj, jounral
        side effect: reference is computed and written to the proper cell on the webadi
        output: none
        """
        # print(dest_proj)
        webadi = journal.sheets["WebADI"]
        unit = dest_proj[:2]
        username = getpass.getuser()
        today = datetime.today().strftime("%d%m%Y")
        self.uploader_ref = f"{unit}{username[:2]}{today}-XXX".upper()
        webadi.range("E8").value = f"{self.uploader_ref}"

    def write_data_to_webadi(self, filtered_data, xlwings_instance, credit=True):
        """Writes to the webadi tab of the journal. The 12 that appears here is hardcoded
        because the first user row of the sheet is 12. This won't be changing and time soon. 


        input: filtered_data, xl_wings_instance, default credit of True
        side effect: copying the prepared data to the jounral tab
        outut: None
        """
        web_adi = xlwings_instance.sheets["WebADI"]
        if credit:
            start = 12
            web_adi.range(f"C{start}").value = filtered_data[1:]
        else:
            start = 12 + 1 + len(filtered_data[1:])
            web_adi.range(f"C{start}").value = filtered_data[1:]

    def copy_data_to_journal(self, ctx):
        """Copies all the input data to the data tab within the journal for a record
        of what has been moved.

        input: ctx
        side effect: data copied to data tab
        output: none
        """
        data_tab = ctx.journal.sheets["data"]
        data_tab.range("A1").value = self.full_data





