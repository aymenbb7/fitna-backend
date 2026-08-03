import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from django.conf import settings

def generate_certificate_pdf(student_name, course_name, issue_date, certificate_id):
    buffer = io.BytesIO()
    
    # A4 dimensions in landscape
    width, height = landscape(A4)
    p = canvas.Canvas(buffer, pagesize=landscape(A4))
    
    # Draw Background (Gold/Black theme)
    p.setFillColor(HexColor('#0B0B0F')) # bgDark
    p.rect(0, 0, width, height, fill=1)
    
    # Draw Border
    p.setStrokeColor(HexColor('#F5C518')) # accentGold
    p.setLineWidth(10)
    p.rect(30, 30, width - 60, height - 60)
    p.setLineWidth(2)
    p.rect(40, 40, width - 80, height - 80)
    
    # Title
    p.setFont("Helvetica-Bold", 40)
    p.setFillColor(HexColor('#F5C518'))
    p.drawCentredString(width/2.0, height - 120, "CERTIFICATE OF COMPLETION")
    
    # Subtitle
    p.setFont("Helvetica", 16)
    p.setFillColor(HexColor('#FFFFFF'))
    p.drawCentredString(width/2.0, height - 160, "This is to certify that")
    
    # Student Name
    p.setFont("Helvetica-Bold", 35)
    p.setFillColor(HexColor('#FFFFFF'))
    p.drawCentredString(width/2.0, height - 220, student_name)
    
    # Course line
    p.setFont("Helvetica", 16)
    p.setFillColor(HexColor('#FFFFFF'))
    p.drawCentredString(width/2.0, height - 270, "has successfully completed the course")
    
    # Course Name
    p.setFont("Helvetica-Bold", 25)
    p.setFillColor(HexColor('#F5C518'))
    p.drawCentredString(width/2.0, height - 320, course_name)
    
    # Date and ID
    p.setFont("Helvetica", 12)
    p.setFillColor(HexColor('#AAAAAA'))
    
    # Left side: Date
    p.drawString(100, 100, f"Date: {issue_date}")
    
    # Right side: Certificate ID
    p.drawRightString(width - 100, 100, f"ID: {certificate_id}")
    
    # Signature Line
    p.setStrokeColor(HexColor('#FFFFFF'))
    p.setLineWidth(1)
    p.line(width/2.0 - 100, 120, width/2.0 + 100, 120)
    p.drawCentredString(width/2.0, 105, "Course Director")
    
    p.showPage()
    p.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
