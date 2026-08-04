from rest_framework import views, status, generics
from rest_framework.response import Response
from core.permissions import IsSuperAdmin
from modules.models import Payment, Module, Enrollment
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
import csv
import io
from django.http import HttpResponse

class RevenueStatsView(views.APIView):
    permission_classes = (IsSuperAdmin,)

    def get(self, request):
        now = timezone.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today - timedelta(days=now.weekday())
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)

        successful_payments = Payment.objects.filter(payment_status='SUCCESS')
        payment_rev = successful_payments.aggregate(Sum('amount'))['amount__sum'] or 0
        
        all_enrollments = Enrollment.objects.select_related('module')
        enrollment_rev = sum(e.module.price for e in all_enrollments if e.module and e.module.price)
        
        total_revenue = float(max(payment_rev, enrollment_rev))
        revenue_today = float(successful_payments.filter(paid_at__gte=today).aggregate(Sum('amount'))['amount__sum'] or 0)
        revenue_this_week = float(successful_payments.filter(paid_at__gte=week_start).aggregate(Sum('amount'))['amount__sum'] or 0)
        revenue_this_month = float(successful_payments.filter(paid_at__gte=month_start).aggregate(Sum('amount'))['amount__sum'] or 0)
        revenue_this_year = float(successful_payments.filter(paid_at__gte=year_start).aggregate(Sum('amount'))['amount__sum'] or 0)

        pending_payments = Payment.objects.filter(payment_status='PENDING').count()
        success_payments_count = max(successful_payments.count(), all_enrollments.count())
        refunded_payments = Payment.objects.filter(payment_status='REFUNDED').count()
        
        average_order_value = total_revenue / success_payments_count if success_payments_count > 0 else 0

        modules_revenue = successful_payments.values('module__name', 'module__slug').annotate(
            total_revenue=Sum('amount'),
            enrollment_count=Count('student', distinct=True)
        ).order_by('-total_revenue')

        best_selling = list(modules_revenue)[:5]
        if not best_selling:
            for m in Module.objects.annotate(ecount=Count('enrollments')).order_by('-ecount')[:5]:
                best_selling.append({
                    "module__name": m.name,
                    "module__slug": m.slug,
                    "total_revenue": float(m.ecount * m.price),
                    "enrollment_count": m.ecount
                })

        thirty_days_ago = today - timedelta(days=30)
        daily_revenue_qs = successful_payments.filter(paid_at__gte=thirty_days_ago).extra(
            select={'day': 'date(paid_at)'}
        ).values('day').annotate(total=Sum('amount')).order_by('day')
        
        daily_revenue = [{"date": str(x['day']), "revenue": float(x['total'])} for x in daily_revenue_qs]

        latest_purchases = Payment.objects.filter(payment_status='SUCCESS').order_by('-paid_at')[:10]
        purchases_data = []
        for p in latest_purchases:
            purchases_data.append({
                "id": p.id,
                "student": p.student.full_name or p.student.email if p.student else 'طالب',
                "module": p.module.name if p.module else 'وحدة',
                "amount": float(p.amount),
                "date": p.paid_at or p.created_at,
                "method": p.payment_method,
            })
        
        if not purchases_data:
            for e in Enrollment.objects.select_related('student', 'module').order_by('-enrolled_at')[:10]:
                purchases_data.append({
                    "id": e.id,
                    "student": e.student.full_name or e.student.email if e.student else 'طالب',
                    "module": e.module.name if e.module else 'وحدة',
                    "amount": float(e.module.price if e.module else 0),
                    "date": e.enrolled_at,
                    "method": 'CASH',
                })

        return Response({
            "total_revenue": total_revenue,
            "revenue_today": revenue_today,
            "revenue_this_week": revenue_this_week,
            "revenue_this_month": revenue_this_month,
            "revenue_this_year": revenue_this_year,
            "pending_payments_count": pending_payments,
            "successful_payments_count": success_payments_count,
            "refunded_payments_count": refunded_payments,
            "average_order_value": average_order_value,
            "best_selling_modules": best_selling,
            "daily_revenue": daily_revenue,
            "latest_purchases": purchases_data
        })

class RevenueExportView(views.APIView):
    permission_classes = (IsSuperAdmin,)

    def get(self, request):
        export_format = request.GET.get('export_format', 'csv')
        payments = Payment.objects.all().order_by('-created_at')

        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="revenue_export.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['ID', 'Student', 'Module', 'Amount', 'Currency', 'Status', 'Method', 'Date'])
            
            for p in payments:
                writer.writerow([
                    p.id, 
                    p.student.email if p.student else '', 
                    p.module.name if p.module else '', 
                    p.amount, 
                    p.currency, 
                    p.payment_status, 
                    p.payment_method, 
                    p.created_at.strftime("%Y-%m-%d %H:%M:%S")
                ])
            return response
            
        elif export_format == 'excel':
            import openpyxl
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="revenue_export.xlsx"'
            
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Revenue"
            ws.append(['ID', 'Student', 'Module', 'Amount', 'Currency', 'Status', 'Method', 'Date'])
            
            for p in payments:
                ws.append([
                    p.id, 
                    p.student.email if p.student else '', 
                    p.module.name if p.module else '', 
                    float(p.amount), 
                    p.currency, 
                    p.payment_status, 
                    p.payment_method, 
                    p.created_at.strftime("%Y-%m-%d %H:%M:%S")
                ])
            wb.save(response)
            return response
            
        elif export_format == 'pdf':
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from core.pdf_utils import setup_arabic_font, render_arabic

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="revenue_export.pdf"'
            
            font_name = setup_arabic_font()

            doc = SimpleDocTemplate(response, pagesize=landscape(letter))
            elements = []

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(name='TitleStyle', fontName=font_name, fontSize=18, alignment=1)
            elements.append(Paragraph(render_arabic('تقرير العوائد المالية - منصة فطنة', font_name), title_style))
            elements.append(Spacer(1, 20))

            data = [[
                render_arabic('التاريخ', font_name), 
                render_arabic('طريقة الدفع', font_name), 
                render_arabic('الحالة', font_name), 
                render_arabic('المبلغ', font_name), 
                render_arabic('الدورة', font_name), 
                render_arabic('الطالب', font_name), 
                render_arabic('ID', font_name)
            ]]

            for p in payments:
                data.append([
                    p.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    render_arabic(p.payment_method, font_name),
                    render_arabic(p.payment_status, font_name),
                    f"{p.amount} {p.currency}",
                    render_arabic(p.module.name if p.module else '', font_name),
                    render_arabic(p.student.full_name if (p.student and p.student.full_name) else (p.student.email if p.student else ''), font_name),
                    str(p.id)
                ])

            table = Table(data, colWidths=[100, 80, 70, 70, 150, 150, 40])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0D0B2B')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,-1), font_name),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f9f9f9')),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cccccc')),
            ]))

            elements.append(table)
            doc.build(elements)
            return response
