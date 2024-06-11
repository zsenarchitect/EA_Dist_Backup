__doc__ = "When load a family to doc, check if the object style already existed in this category, if not, pop to ask if want to revise object style before load, if so, cancell load, otherwise confrim and load."
__title__ = "check object style used-hook"


#pyrevit event: family-loaded or loading
#becasue of protentional nesting family, it might be hard to obtain sub-c diretly from the main host family without exhasut all the nesting faimly(it is posibile recursitively). I will suggest during loading, check project sub-c list and compare to  after once load what is being added.



#sister script---open all the family, and find sub-c not used by any. this is computing intensive
