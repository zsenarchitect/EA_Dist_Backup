import os
import ENVIRONMENT
import tempfile




def pdf2img(pdf_path, output_path = None):
    pass


def img2pdf(image_path, output_path = None):
    """convert image to pdf.

    Args:
        image_path (str): path for the input image
        pdf_path (str): path for the output pdf
    """
    from PIL import Image

    
    if pdf_path is None:
        # replace any image extension with pdf extension
        extension = os.path.splitext(image_path)[1]
        pdf_path = image_path.replace(extension, ".pdf")
    
    # Open the image
    with Image.open(image_path) as img:
        # Converting the image to RGB, to ensure compatibility
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save as PDF
        img.save(pdf_path, "PDF", resolution=100.0)
    return pdf_path



def pdfs2pdf(combined_pdf_file_path, list_of_filepaths, reorder = False):
    """merge multiple pdfs to single pdf.

    Args:
        combined_pdf_file_path (str): path for final product
        list_of_filepaths (list): list of l=path for the input pdfs
        reorder (bool, optional): reorder the pdf alphabetically. Defaults to False.
    """
    from PyPDF2 import PdfFileMerger

    merger = PdfFileMerger()

    if reorder:
        list_of_filepaths.sort()

    for filepath in list_of_filepaths:
        merger.append(filepath)

    merger.write(combined_pdf_file_path)
    merger.close()


def images2pdf(combined_pdf_file_path, list_of_filepaths, reorder = False):
    """merge multiple images to single pdf.

    Args:
        combined_pdf_file_path (str): path for final product
        list_of_filepaths (list): list of l=path for the input images
        reorder (bool, optional): reorder the pdf alphabetically. Defaults to False.
    """
    from PyPDF2 import PdfFileMerger

    from PIL import Image
    merger = PdfFileMerger()

    if reorder:
        list_of_filepaths.sort()

    for filepath in list_of_filepaths:
        with Image.open(filepath) as img:
            merger.append(img)


    merger.write(combined_pdf_file_path)
    merger.close()

try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table  
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus.flowables import KeepTogether
except:
    pass




def documentation2pdf(doc_data_list, pdf_path):
    PDFGenerator(pdf_path).generate((doc_data_list))
class PDFGenerator:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        
        # Define margins as class attributes
        self.LEFT_MARGIN = 1 * inch
        self.RIGHT_MARGIN = 1 * inch
        self.TOP_MARGIN = 1 * inch
        self.BOTTOM_MARGIN = 1 * inch
        
        self.styles = getSampleStyleSheet()
        self.command_style = ParagraphStyle(
            'CommandStyle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=6
        )
        self.tooltip_style = ParagraphStyle(
            'TooltipStyle',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.darkgrey
        )
        self.tab_header_style = ParagraphStyle(
            'TabHeaderStyle',
            fontSize=9,
            textColor=colors.lightgrey,
            alignment=2
        )
        self.sub_title_style = ParagraphStyle(
            'SubTitleStyle',
            fontSize=9,
            textColor=colors.darkgray,
            alignment=1
        )
        
    def get_header(self, canvas, doc, tab_name, tab_icon_path):
        """Draw tab header on each page, ensuring it stays within page bounds."""
        canvas.saveState()
        page_width, page_height = canvas._pagesize
        
        # Create a table for tab name and icon, aligning them together at the top-right
        tab_header = Paragraph("<b>{}</b>".format(tab_name), self.tab_header_style)
        
        icon_width = 0.2 * inch
        icon_height = 0.2 * inch
        tab_icon = Image(tab_icon_path, width=icon_width, height=icon_height) if tab_icon_path else Spacer(icon_width, icon_height)
        
        tab_data = [[tab_header, tab_icon]]
        tab_table = Table(tab_data, colWidths=[150, 30])
        tab_table.setStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ])
        
        tab_table.wrapOn(canvas, 200, 20)
        tab_table.drawOn(canvas, page_width - self.RIGHT_MARGIN - 200, page_height - self.TOP_MARGIN + 10)
        
        # Add page number at bottom center
        canvas.drawCentredString(page_width / 2, self.BOTTOM_MARGIN / 2, "{}".format(self.current_page_num))
        
        canvas.restoreState()

        self.current_page_num += 1
    
    def generate_segment_pdf(self, segment_data, tab_name, tab_icon_path, temp_pdf_path):
        """Generate a temporary PDF for a single segment."""
        doc = SimpleDocTemplate(temp_pdf_path, pagesize=letter,
                                rightMargin=self.RIGHT_MARGIN, leftMargin=self.LEFT_MARGIN,
                                topMargin=self.TOP_MARGIN, bottomMargin=self.BOTTOM_MARGIN)
        story = []

        for doc_data in segment_data:
            alias_info = doc_data.get('alias', "No alias")
            if isinstance(alias_info, list):
                alias_info = " / ".join(alias_info)
            alias = Paragraph(alias_info, self.command_style)
            tooltip_text = Paragraph("<b>Tooltip:</b> {}".format(doc_data.get('doc', 'No description available')), self.tooltip_style)
            access = "Left Click" if "_left" in doc_data.get("script") else "Right Click"
            access_text = Paragraph("<b>Access:</b> {}".format(access), self.tooltip_style)
            icon = Image(os.path.join(ENVIRONMENT.RHINO_FOLDER, doc_data['icon']), width=0.5 * inch, height=0.5 * inch) if doc_data.get('icon') else Spacer(1, 0.8 * inch)
            
            data = [[icon, alias], ['', tooltip_text], ["", access_text]]
            table = Table(data, colWidths=[1.2 * inch, 6 * inch])
            table.setStyle([
                ('SPAN', (0,0), (0,1)),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (0,0), (0,-1), 'CENTER'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 12)
            ])
            
            story.append(KeepTogether([table, Spacer(1, 0.5 * inch)]))
        
        doc.build(story, onFirstPage=lambda c, d: self.get_header(c, d, tab_name, tab_icon_path),
                  onLaterPages=lambda c, d: self.get_header(c, d, tab_name, tab_icon_path))
    
    def generate(self, doc_data_list):
        """Generates the final PDF with cover page, TOC, segmented content, and page numbers."""
        temp_pdfs = []
        segmented_data = {}
        toc_entries = []
        self.current_page_num = 1
        
        # Generate cover page
        cover_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
        self.generate_cover_page(cover_pdf)
        temp_pdfs.append(cover_pdf)
        
        # Split data into segments based on tab
        for doc_data in doc_data_list:
            tab_name = doc_data.get('tab', 'Unknown Tab')
            if tab_name is None:
                continue
            tab_icon_path = os.path.join(ENVIRONMENT.RHINO_FOLDER, doc_data['tab_icon']) if doc_data.get('tab_icon') else None
            
            if tab_name not in segmented_data:
                segmented_data[tab_name] = {'data': [], 'icon': tab_icon_path}
            segmented_data[tab_name]['data'].append(doc_data)
        
        # Generate temporary PDFs for each segment and track TOC entries
        for tab_name, segment in segmented_data.items():
            temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
            temp_pdfs.append(temp_pdf)
            toc_entries.append((tab_name, self.current_page_num))
            self.generate_segment_pdf(segment['data'], tab_name, segment['icon'], temp_pdf)

        
        # Generate table of contents
        toc_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
        self.generate_table_of_contents(toc_pdf, toc_entries)
        temp_pdfs.insert(1, toc_pdf)  # Insert TOC after cover
        
        # Merge all PDFs into the final document
        from PyPDF2 import PdfMerger
        merger = PdfMerger()
        for temp_pdf in temp_pdfs:
            merger.append(temp_pdf)
        merger.write(self.pdf_path)
        merger.close()
        
        # Delete temporary PDFs
        for temp_pdf in temp_pdfs:
            os.remove(temp_pdf)
        
        print("Final PDF saved at " + self.pdf_path)

    def generate_table_of_contents(self, temp_pdf_path, toc_entries):
        """Generate a table of contents page."""
        doc = SimpleDocTemplate(temp_pdf_path, pagesize=letter,
                                rightMargin=self.RIGHT_MARGIN, leftMargin=self.LEFT_MARGIN,
                                topMargin=self.TOP_MARGIN, bottomMargin=self.BOTTOM_MARGIN)
        story = [Paragraph("Table of Contents", self.styles['Title']), Spacer(1, 0.5 * inch)]
        
        for tab_name, page_number in toc_entries:
            story.append(Paragraph("{} ----------- Page {}".format(tab_name, page_number), self.sub_title_style))
            story.append(Spacer(1, 0.2 * inch))
        
        doc.build(story)

    def generate_cover_page(self, temp_pdf_path):
        """Generate a cover page for the document."""
        doc = SimpleDocTemplate(temp_pdf_path, pagesize=letter,
                                rightMargin=self.RIGHT_MARGIN, leftMargin=self.LEFT_MARGIN,
                                topMargin=self.TOP_MARGIN, bottomMargin=self.BOTTOM_MARGIN)
        story = [
            Spacer(1, 3 * inch),
            Paragraph("<b>EnneadTab For Rhino Secret</b>", self.styles['Title']),
            Spacer(1, 2 * inch),
            Paragraph("Confidential Documentation", self.sub_title_style)
        ]
        doc.build(story)