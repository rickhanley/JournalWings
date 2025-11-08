# JournalWings Executable

This folder contains example data for JournalWings for demonstration purposes.
The JournalWings.exe is availabe under releases.

---

## 📦 Contents
- `data.xlsx` — sample input data  
- `journal.xlsm` — journal template  

---

## ▶️ How to Run
1. Ensure `JournalWings.exe`, `data.xlsx`, and `journal.xlsm` are in the **same folder**.  
2. Double-click `JournalWings.exe`.  
3. The program will:
   - Prompt the user:  
     - **Option 1** → try `HCR / AJR / B9R` (e.g. `HCR99999`) for the project code to pass validation.  
       For the Task, try `HC / AJ / B9` (e.g. `HC99.99`) to pass validation.  
     - **Option 2** → try `HC / AJ / B9` (e.g. `HC9999`). Accept the default or enter a 5-digit code when prompted. 
     - **Option 3** → No input required. Prepares a journal with the expenditure type column blanked out on the debits. 
   - Read the input file.  
   - Process the data.  
   - Generate a `.xlsm` output file in the same folder following naming conventions.  
     > Delete this file before trying again with different options.  

---

## ℹ️ Notes
- This executable is for **portfolio demonstration only**.  
- No real institutional data is included.  
- For source code and development instructions, see the main [JournalWings README](../README.md).  
