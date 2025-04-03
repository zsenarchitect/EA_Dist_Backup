#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """Monitor and compare grid and level elements between current document and linked documents.
This tool helps track differences in grids and levels between the host document and its linked models.
It identifies elements that exist in one document but not in others, and checks monitoring status."""
__title__ = "Monitor\nLink Status"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 
from pyrevit import script
from collections import defaultdict

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

class RevitElementCollector:
    """Handles collection and analysis of Revit elements (grids and levels)."""
    
    def __init__(self, doc):
        self.doc = doc
        self.output = script.get_output()
        
    def get_elements_by_category(self, category, doc=None):
        """Get elements of specified category from document."""
        doc = doc or self.doc
        return DB.FilteredElementCollector(doc).OfCategory(category).WhereElementIsNotElementType().ToElements()
        
    def get_elements_in_primary_option(self, elements):
        """Filter elements to only include those in primary design option."""
        return [element for element in elements 
                if element.DesignOption is None or element.DesignOption.IsPrimary]
                
    def get_element_by_name(self, elements, name):
        """Get element by name from a list of elements."""
        return next((x for x in elements if x.Name == name), None)
        
    def compare_elements(self, current_elements, link_elements):
        """Compare elements between current and linked documents."""
        current_names = {x.Name for x in current_elements}
        link_names = {x.Name for x in link_elements}
        
        return {
            'current_only': sorted(current_names - link_names),
            'link_only': sorted(link_names - current_names)
        }
        


    
class LinkComparisonAnalyzer:
    """Analyzes and compares elements between host document and linked documents."""
    
    def __init__(self, doc):
        self.doc = doc
        self.element_collector = RevitElementCollector(doc)
        
    def get_linked_documents(self):
        """Get all linked Revit documents."""
        links = DB.FilteredElementCollector(self.doc).OfClass(DB.RevitLinkInstance).WhereElementIsNotElementType().ToElements()
        return [(link, link.GetLinkDocument()) for link in links]
        
    def analyze_links(self):
        """Analyze and compare elements between current and linked documents."""
        links = self.get_linked_documents()
        if not links:
            print("No links loaded")
            return
            
        # Collect all grids and levels from links
        all_link_grids = []
        all_link_levels = []
        
        for link, link_doc in links:
            self.link_doc = link_doc
            self.element_collector.output.print_md("# {}".format(link_doc.Title))
            
            grids = self.element_collector.get_elements_by_category(DB.BuiltInCategory.OST_Grids, link_doc)
            levels = self.element_collector.get_elements_by_category(DB.BuiltInCategory.OST_Levels, link_doc)
            
            all_link_grids.extend(self.element_collector.get_elements_in_primary_option(grids))
            all_link_levels.extend(levels)
            
        # Get current document elements
        current_grids = self.element_collector.get_elements_in_primary_option(
            self.element_collector.get_elements_by_category(DB.BuiltInCategory.OST_Grids)
        )
        current_levels = self.element_collector.get_elements_by_category(DB.BuiltInCategory.OST_Levels)
        
        # Print element counts
        print("Number of grids in current document = {}".format(len(current_grids)))
        print("Number of grids in links = {}".format(len(all_link_grids)))
        print("*"*20)
        print("Number of levels in current document = {}".format(len(current_levels)))
        print("Number of levels in links = {}".format(len(all_link_levels)))
        
        # Compare elements
        grid_comparison = self.element_collector.compare_elements(current_grids, all_link_grids)
        level_comparison = self.element_collector.compare_elements(current_levels, all_link_levels)
        
        # Print comparison results
        self._print_comparison_results(grid_comparison, level_comparison)
        
        # Check monitoring status
        self._check_monitoring_status(current_grids, current_levels)
        
    def _print_comparison_results(self, grid_comparison, level_comparison):
        """Print formatted comparison results."""
        def print_names(title, names):
            print("\n{}".format(title))
            if not names:
                print("Empty")
                return
            print("|" + "|".join(names) + "|")
            
        print_names("Grids in current document but not in links", grid_comparison['current_only'])
        print("*"*20)
        print_names("Grids in links but not in current document", grid_comparison['link_only'])
        print("*"*20)
        print_names("Levels in current document but not in links", level_comparison['current_only'])
        print("*"*20)
        print_names("Levels in links but not in current document", level_comparison['link_only'])
        
    def _check_monitoring_status(self, current_grids, current_levels):
        """Check monitoring status of elements."""
        print("&"*40)
        list(map(lambda grid: self.check_monitoring_status(grid, "grids"), current_grids))
        list(map(lambda level: self.check_monitoring_status(level, "levels"), current_levels))


        
    def check_monitoring_status(self, element, element_type):
        """Check if element is monitoring linked elements."""
        if not element.IsMonitoringLinkElement():
            print ("----[{}] is not monitoring {} in link {}".format(element.Name, element_type, self.link_doc.Title))
            return 
            
        # monitored_ids = list(element.GetMonitoredLinkElementIds())

        # for monitored_id in monitored_ids:
        #     print (monitored_id)
        #     link_element = self.doc.GetElement(monitored_id)
        #     if link_element:
        #         print ("{} is monitoring {} in {}".format(element.Name, link_element.Name, self.link_doc.Title))
        

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def monitor_link_status(doc):
    """Main function to monitor link status."""
    analyzer = LinkComparisonAnalyzer(doc)
    analyzer.analyze_links()

if __name__ == "__main__":
    monitor_link_status(DOC)







