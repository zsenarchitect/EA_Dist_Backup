
from pyrevit import script


__title__ = "test print \ntable"
__doc__ = 'try print a table and bring to excel?'




output = script.get_output()

data = [['a', 'afs', 'aaertegeaa', 80],['sdsvswv', 'wetw4', 'a66u6ja', 45],['qwdqow3', 'dqwda', 'dqwf24gata', 45],['a5yaaa', 'daadwaca', 'aaave', 45]]


output.print_table(table_data=data,title="Example Table",columns=["Row Name", "Column 1", "Column 2", "Percentage"],formats=['', '${}', 'prefix_{}', '{}%'],last_line_style='color:red;')
