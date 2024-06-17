
try {
    var myDocument = app.documents.add();
    myDocument.documentPreferences.pageWidth = "17in";
    myDocument.documentPreferences.pageHeight = "11in";
    myDocument.documentPreferences.facingPages = false;
    var pdfPath = "J:/1643/2_Master File/B-03_Ewing Cole/01_In/2024-05-30 Plan Set Deliverables\\20160364_LHH BOD-A_FO_Plan Set 1_Existing Departmental.pdf";
    var pageCount = 18;

    for (var i = 0; i < pageCount; i++) {
        try {
            if (i > 0) {
                myDocument.spreads.add();
            }
            app.scriptPreferences.measurementUnit = MeasurementUnits.INCHES_DECIMAL;
            var mySpread = myDocument.spreads.item(i);
            app.pdfPlacePreferences.pageNumber = i + 1;
            var myPDFPage = mySpread.place(File(pdfPath), [0, 0])[0];
            myPDFPage.geometricBounds = [0, 0, myDocument.documentPreferences.pageHeight, myDocument.documentPreferences.pageWidth];
            myPDFPage.fit(FitOptions.FRAME_TO_CONTENT);
            myPDFPage.fit(FitOptions.FILL_PROPORTIONALLY);
            
        } catch (e) {
            alert("Error placing page " + (i + 1) + ": " + e.message);
        }
    }

    try {
        var myFile = new File("J:/1643/2_Master File/B-03_Ewing Cole/01_In/2024-05-30 Plan Set Deliverables\\20160364_LHH BOD-A_FO_Plan Set 1_Existing Departmental.indd");
        myDocument.save(myFile);
    } catch (e) {
        alert("Error saving document: " + e.message);
    } finally {
        myDocument.close();
    }
} catch (e) {
    alert("Error creating document: " + e.message);
}
