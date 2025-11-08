def endnotes(ctx):


    return(f"""
        \033[92m***************** 
        *    Success    *
        *****************\033[0m
        {ctx.tt.summary_string}
                    
        Remember: JournalWings copies and arranges existing data.
        If the input is incorrect the output will also be incorrect!

        Check:

            1. Destination project and task are correct
            2. Your 'Value' field reference is correct:
               Do enter your correct sequence number
            3. Your unit is correct
            4. You've attached justifications (emails,
               screenshots etc on the backups tab)
            5. The correct rows are flagged
                    
        The journal is now ready to upload manually as normal

        IMPORTANT:
        If transferring to a unit outside of your own, forward the uploader to
        the unit for action or get authorisation to do the upload once checked
        by the other department.
            """)
