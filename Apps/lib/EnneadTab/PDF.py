import os
import ENVIRONMENT
import tempfile
import TIME



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




def documentation2pdf(app, doc_data_list, pdf_path):
    PDFGenerator(app, pdf_path).generate((doc_data_list))
    
class PDFGenerator:
    def __init__(self, app, pdf_path):
        self.app = app
        self.pdf_path = pdf_path
        
        # Define margins as class attributes
        self.LEFT_MARGIN = 1 * inch
        self.RIGHT_MARGIN = 1 * inch
        self.TOP_MARGIN = 1 * inch
        self.BOTTOM_MARGIN = 1 * inch
        
        self.styles = getSampleStyleSheet()
        self.book_title_style = ParagraphStyle(
            'BookTitleStyle',
            parent=self.styles['Heading1'],
            fontSize=60,
            alignment=1,
            textColor=colors.white,
            backColor=colors.transparent,
            fontName='Helvetica-Bold'
        )
        self.command_style = ParagraphStyle(
            'CommandStyle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=6
        )
        self.tooltip_style = ParagraphStyle(
            'TooltipStyle',
            parent=self.styles['BodyText'],
            fontSize=8,
            textColor=colors.darkgrey
        )
        self.tab_header_style = ParagraphStyle(
            'TabHeaderStyle',
            fontSize=10,
            textColor=colors.lightgrey,
            alignment=2
        )
        self.sub_title_style = ParagraphStyle(
            'SubtitleStyle',
            fontSize=10,
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
        tab_table = Table(tab_data, colWidths=[100, 30])
        tab_table.setStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ])
        
        tab_table.wrapOn(canvas, 200, 20)
        tab_table.drawOn(canvas, page_width - self.RIGHT_MARGIN - 100, page_height - self.TOP_MARGIN + 10)
        
        # Add page number at bottom center
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(page_width / 2, self.BOTTOM_MARGIN / 3, "{}".format(self.current_page_num))
        
        canvas.restoreState()

        self.current_page_num += 1


    def format_return_line(self, text):
        return text.replace("\n", "<br/>")
    
    def generate_segment_pdf(self, segment_data, tab_name, tab_icon_path, temp_pdf_path):
        """Generate a temporary PDF for a single segment."""
        doc = SimpleDocTemplate(temp_pdf_path, pagesize=letter,
                                rightMargin=self.RIGHT_MARGIN, leftMargin=self.LEFT_MARGIN,
                                topMargin=self.TOP_MARGIN, bottomMargin=self.BOTTOM_MARGIN)
        story = []

        for doc_data in segment_data:
            is_popular = doc_data.get('is_popular', False)

            
            alias_info = doc_data.get('alias', "No alias")
            if isinstance(alias_info, list):
                alias_info = " / ".join(alias_info)
            alias = Paragraph(alias_info, self.command_style)
            tooltip_text = Paragraph("<b>Tooltip:</b> {}".format(self.format_return_line(doc_data.get('doc', 'No description available'))), self.tooltip_style)
            if self.app == "Rhino":
                access = "Left Click" if "_left" in doc_data.get("script") else "Right Click"
                access_text = Paragraph("<b>Access:</b> {}".format(access), self.tooltip_style)
            else:
                access_text = ""
                
            if self.app == "Rhino":
                icon = Image(os.path.join(ENVIRONMENT.RHINO_FOLDER, doc_data['icon']), width=0.5 * inch, height=0.5 * inch) if doc_data.get('icon') else Spacer(1, 0.8 * inch)
            else:
                icon = Image(os.path.join(ENVIRONMENT.REVIT_PRIMARY_EXTENSION, doc_data['icon']), width=0.5 * inch, height=0.5 * inch) if doc_data.get('icon') else Spacer(1, 0.8 * inch)

            if is_popular:
                poplular_info = "[Popular]"
            else:
                poplular_info = ""
            style_1 = ParagraphStyle('temp',fontSize=7,textColor=colors.grey,alignment=1)
            poplular_info = Paragraph(poplular_info, style_1)
            
            data = [[icon, alias], ['', tooltip_text], [poplular_info, access_text]]
            table = Table(data, colWidths=[1.2 * inch, 6 * inch])

            table_style = [
                ('SPAN', (0,0), (0,1)),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (0,0), (0,-1), 'CENTER'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4)
            ]

            # Add thick border if popular
            if is_popular:
                table_style.append(('BOX', (0,0), (-1,-1), 3, colors.lightgrey))  # Thick black border


            table.setStyle(table_style)
            story.append(KeepTogether([table, Spacer(1, 0.2 * inch)]))
        
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


        used_scripts = set()
        # Split data into segments based on tab
        for doc_data in doc_data_list:
            if doc_data.get("script") in used_scripts:
                continue
            else:
                used_scripts.add(doc_data.get("script"))
                
            tab_name = doc_data.get('tab', 'Unknown Tab')
            if tab_name is None:
                continue
            if self.app == "Rhino":
                tab_icon_path = os.path.join(ENVIRONMENT.RHINO_FOLDER, doc_data['tab_icon']) if doc_data.get('tab_icon') else None
            else:
                tab_icon_path = os.path.join(ENVIRONMENT.REVIT_PRIMARY_EXTENSION, doc_data['tab_icon']) if doc_data.get('tab_icon') else None
            
            if tab_name not in segmented_data:
                segmented_data[tab_name] = {'data': [], 'tab_icon': tab_icon_path}
            segmented_data[tab_name]['data'].append(doc_data)
        
        # Generate temporary PDFs for each segment and track TOC entries
        for tab_name, segment in segmented_data.items():
            temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
            temp_pdfs.append(temp_pdf)
            toc_entries.append((tab_name, self.current_page_num, segment['tab_icon']))
            self.generate_segment_pdf(segment['data'], tab_name, segment['tab_icon'], temp_pdf)

        
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
        
        print("\n\nHandBook Final PDF saved at: " + self.pdf_path)

    def generate_table_of_contents(self, temp_pdf_path, toc_entries):
        """Generate a table of contents page."""
        doc = SimpleDocTemplate(temp_pdf_path, pagesize=letter,
                                rightMargin=self.RIGHT_MARGIN, leftMargin=self.LEFT_MARGIN,
                                topMargin=self.TOP_MARGIN, bottomMargin=self.BOTTOM_MARGIN)
        story = [Paragraph("Table of Contents", self.styles['Title']), Spacer(1, 0.5 * inch)]
        
        table_data = []
        for tab_name, page_number, tab_icon_path in toc_entries:
            tab_icon = Image(tab_icon_path, width=0.2 * inch, height=0.2 * inch) if tab_icon_path else Spacer(0.2 * inch, 0.2 * inch)
            style_1 = ParagraphStyle('x',fontSize=9,textColor=colors.darkgray,alignment=0)
            style_2 = ParagraphStyle('y',fontSize=9,textColor=colors.darkgray,alignment=2)
            table_data.append([tab_icon, 
                               Paragraph(tab_name, style_1),
                               Paragraph("~~~~~~~~~~~~~~~~~~~~", self.sub_title_style), 
                               Paragraph("Page {}".format(page_number), style_2)])
        
        toc_table = Table(table_data, colWidths=[0.3 * inch, 1.2 * inch, 1.8 * inch, 1.2 * inch])
        toc_table.setStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ])
        
        story.append(toc_table)
        doc.build(story)

        
    def generate_cover_page(self, temp_pdf_path):
        """Generate a cover page for the document."""
        doc = SimpleDocTemplate(temp_pdf_path, pagesize=letter,
                                rightMargin=self.RIGHT_MARGIN, leftMargin=self.LEFT_MARGIN,
                                topMargin=self.TOP_MARGIN, bottomMargin=self.BOTTOM_MARGIN)


        style = ParagraphStyle('x',fontSize=9,textColor=colors.white,alignment=1)


        story = [
            Spacer(1, 3 * inch),
            Paragraph("<b>EnneadTab</b>", self.book_title_style),
            Spacer(1, 0.5 * inch),
            Paragraph("<b>For</b>", self.book_title_style),
            Spacer(1, 0.5 * inch),
            Paragraph("<b>{}</b>".format(self.app), self.book_title_style),
            Spacer(1, 2 * inch),
            Paragraph("Secret Documentation", style),
            Paragraph("{}".format(TIME.get_YYYY_MM_DD()), style)
        ]
        def add_background(canvas, doc):
            canvas.saveState()
            cover_color = colors.lightsalmon if self.app == "Rhino" else colors.lightseagreen
            canvas.setFillColor(cover_color)  # Set background color to light orange
            canvas.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
            canvas.restoreState()

        doc.build(story, onFirstPage=add_background)