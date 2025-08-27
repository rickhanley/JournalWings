# Think of pipeline.py as a high level co-ordinator.
# Run is instantiating AppContext. All classes assigned to AppContext
# will also be instantiated when run is called. Notice we immediatelt call
# bootstrap on AppCOntext, so it is instatiated and bootstrap fired all in
# one go. 


from modules.appcontext import AppContext
from modules.ascii import ShowHeader
from modules.pipeline_methods import p_to_p, p_to_gl, exps
from modules.endnotes import endnotes
from modules.scroller import scroller
import time

pipeline_dict = {
    "1": p_to_p,
    "2": p_to_gl,
    "3": exps
}

def run():
    ctx = None
    try:
        ctx = AppContext().bootstrap()
        sh = ShowHeader()
        sh.show_header()
        ctx.ui.get_pipeline()
        ctx.ui.pipeline_specific_choices()
        dispatch(ctx, ctx.ui.user_responses)
    except KeyboardInterrupt:
        print("\n\n   [!] Interrupted by user. Exiting...\n\n")
        return
    else:
         if ctx is not None:
              scroller(endnotes(ctx))
    finally:
        if ctx is not None and ctx.fm.app is not None:
            # ctx.fm.close_journal_xlwings(getattr(ctx, "journal", None))
            # if ctx.fm.app is not None:
                # scroller(endnotes(ctx))
                # print(endnotes(ctx))
                ctx.fm.app.quit()
                ctx.fm.app = None

def dispatch(ctx, user_responses):
    handler = pipeline_dict[user_responses["pipeline_choice"]]
    handler(ctx)




        




