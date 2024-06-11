__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "review group by image"


#place group instance, zoom to fit, export view as image, file name is group name, delete group instance


"""Exports the current view to a 600DPI PNG image."""

from pyrevit.framework import Forms
from pyrevit import revit, DB


# collect file location from user
dialog = Forms.SaveFileDialog()
dialog.Title = 'Export current view as PNG'
dialog.Filter = 'PNG files (*.PNG)|*.PNG'

if dialog.ShowDialog() == Forms.DialogResult.OK:
    # set up the export options
    options = DB.ImageExportOptions()
    options.ExportRange = DB.ExportRange.VisibleRegionOfCurrentView
    options.FilePath = dialog.FileName
    options.HLRandWFViewsFileType = DB.ImageFileType.PNG
    options.ImageResolution = DB.ImageResolution.DPI_600
    options.ZoomType = DB.ZoomFitType.Zoom
    options.ShadowViewsFileType = DB.ImageFileType.PNG

    revit.doc.ExportImage(options)
