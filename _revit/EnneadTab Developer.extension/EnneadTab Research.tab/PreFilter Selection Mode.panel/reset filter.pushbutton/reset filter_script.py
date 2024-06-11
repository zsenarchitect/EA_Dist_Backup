__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Reset\nAll Filters"


from pyrevit.loader import sessionmgr
#from pyrevit import script
#from pyrevit.loader import sessioninfo

#logger = script.get_logger()
#results = script.get_results()
sessionmgr.reload_pyrevit()
#results.newsession = sessioninfo.get_session_uuid()
