# Think of this as the craftsperson / cook
# its taking the tools and using them in the right way / order
# to create the final output. There's 3 main recipes here
# Project to Project
# Project to GL
# Exp type change

# also note how it's easier to have methods return here for data to then be passed
# to the next stage

import time


def p_to_p(ctx):
    """Runs the logical steps to process the data on a project to project basis
    input: ctx - shared app context containing managers and user_inputs
    side effects: Creates and saves the finished journal uploader
    output: None
    
    """
    ctx.start_time = time.perf_counter()
    ctx.fm.create_xlwings_instance()
    app = ctx.fm.app
    if not app:
        raise RuntimeError("    [!] failed to get webadi reference")

    try:
        credit_numbers, debit_numbers = None, None
        ctx.journal = ctx.fm.open_journal_with_xlwings(ctx.paths, app)
        ctx.dm.clean_journal(ctx.journal)
        filtered_data = ctx.dm.filter_data_to_journal_headings(ctx.data)
        date_formatted_filtered_data = ctx.dm.datetimes_to_strings(filtered_data)
        credit_rows = ctx.dm.build_credit_rows(date_formatted_filtered_data, ctx)
        credit_numbers = ctx.dm.financial_column_data_only(credit_rows)
        ctx.dm.write_data_to_webadi(credit_rows, ctx.journal)
        dest_project = ctx.ui.user_responses["dest_proj"]
        dest_task = ctx.ui.user_responses["dest_task"]
        debit_rows = ctx.dm.build_debit_rows(credit_rows, ctx.data, dest_project=dest_project, dest_task=dest_task)
        debit_numbers = ctx.dm.financial_column_data_only(debit_rows)
        ctx.dm.write_data_to_webadi(debit_rows, ctx.journal, False)
        ctx.dm.write_unit_header(ctx.ui.user_responses["dest_proj"], ctx.journal)
        ctx.dm.write_uploader_ref(ctx.ui.user_responses["dest_proj"], ctx.journal)
        ctx.dm.copy_data_to_journal(ctx)
        ctx.journal.save()
        try:
            ctx.fm.file_rename(ctx.paths[0], ctx)
        except Exception as e:
            print(f"    [!] Failed to copy / rename journal: {e}")
        ctx.end_time = time.perf_counter()
        ctx.tt.summary_string = ctx.dm.summary_info(credit_numbers, ctx, debit_numbers)

    finally:
        if ctx.journal:
            try:
                ctx.journal.close()
            except Exception as e:
                print(f"    [!] Failed to close journal: {e}")
            ctx.journal = None

        if ctx.fm.app:
            try:
                ctx.fm.app.quit()
            except Exception as e:
                print(f"    [!] Failed to quit Excel app: {e}")
            ctx.fm.app = None




def p_to_gl(ctx):
    ctx.start_time = time.perf_counter()
    ctx.fm.create_xlwings_instance()
    app = ctx.fm.app
    if not app:
        raise RuntimeError("    [!] failed to get webadi reference")
    try:
        credit_numbers = None
        ctx.journal = ctx.fm.open_journal_with_xlwings(ctx.paths, app)
        ctx.dm.clean_journal(ctx.journal)
        filtered_data = ctx.dm.filter_data_to_journal_headings(ctx.data)
        date_formatted_filtered_data = ctx.dm.datetimes_to_strings(filtered_data)
        credit_rows = ctx.dm.build_credit_rows(date_formatted_filtered_data, ctx)
        credit_numbers = ctx.dm.financial_column_data_only(credit_rows)

        ctx.dm.write_data_to_webadi(credit_rows, ctx.journal)
        ctx.dm.write_unit_header(ctx.ui.user_responses["dest_proj"], ctx.journal)
        ctx.dm.write_uploader_ref(ctx.ui.user_responses["dest_proj"], ctx.journal)
        ctx.dm.copy_data_to_journal(ctx)

        ctx.journal.save()
        try:
            ctx.fm.file_rename(ctx.paths[0], ctx)
        except Exception as e:
            print(f"    [!] Failed to copy / rename journal: {e}")
        ctx.end_time = time.perf_counter()
        ctx.tt.summary_string = ctx.dm.summary_info(credit_numbers, ctx)

    finally:
        if ctx.journal:
            try:
                ctx.journal.close()
            except Exception as e:
                print(f"    [!] Failed to close journal: {e}")
            ctx.journal = None

        if ctx.fm.app:
            try:
                ctx.fm.app.quit()
            except Exception as e:
                print(f"    [!] Failed to quit Excel app: {e}")
            ctx.fm.app = None



def exps(ctx):
    ctx.start_time = time.perf_counter()
    ctx.fm.create_xlwings_instance()
    app = ctx.fm.app
    if not app:
        raise RuntimeError("    [!] failed to get webadi reference")
    try:
        credit_numbers, debit_numbers = None, None
        ctx.journal = ctx.fm.open_journal_with_xlwings(ctx.paths, app)
        ctx.dm.clean_journal(ctx.journal)
        filtered_data = ctx.dm.filter_data_to_journal_headings(ctx.data)
        date_formatted_filtered_data = ctx.dm.datetimes_to_strings(filtered_data)
        source_project = filtered_data[1][0]
        credit_rows = ctx.dm.build_credit_rows(date_formatted_filtered_data, ctx)
        credit_numbers = ctx.dm.financial_column_data_only(credit_rows)
        ctx.dm.write_data_to_webadi(credit_rows, ctx.journal)
        project_column, task_column = ctx.dm.get_project_and_task_columns_for_exp_change(filtered_data)
        chosen_pipeline = str(ctx.ui.user_responses["pipeline_choice"]).strip()
        debit_rows = ctx.dm.build_debit_rows(credit_rows, ctx.data, project_col=project_column, task_col=task_column, pipeline=chosen_pipeline)
        debit_numbers = ctx.dm.financial_column_data_only(debit_rows)
        ctx.dm.write_data_to_webadi(debit_rows, ctx.journal, False)
        ctx.dm.write_unit_header(source_project, ctx.journal)
        ctx.dm.write_uploader_ref(source_project, ctx.journal)
        ctx.dm.copy_data_to_journal(ctx)
        ctx.journal.save()
        try:
            ctx.fm.file_rename(ctx.paths[0], ctx)
        except Exception as e:
            print(f"    [!] Failed to copy / rename journal: {e}")

        ctx.end_time = time.perf_counter()
        ctx.tt.summary_string = ctx.dm.summary_info(credit_numbers, ctx, debit_numbers)

    finally:
        if ctx.journal:
            try:
                ctx.journal.close()
            except Exception as e:
                print(f"    [!] Failed to close journal: {e}")
            ctx.journal = None

        if ctx.fm.app:
            try:
                ctx.fm.app.quit()
            except Exception as e:
                print(f"    [!] Failed to quit Excel app: {e}")
            ctx.fm.app = None

