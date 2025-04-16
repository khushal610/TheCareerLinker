from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from devapp import models as devModels
from devapp import forms
from studentapp.models import User,Quiz_attempt,Attempted_session,Contact_us,Course_Enrollment,Feedback
from TheCareerLinker import views as TCL_views
from devapp import views as dev_views
from django.core.paginator import Paginator
from django.db.models import Q
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from django.db.models import Sum

# Create your views here.
def index(request):
    totalStudents = User.objects.filter(role="Student").count()
    totalDevelopers = User.objects.filter(role="Developer").count()
    totalQuiz = devModels.QuizCategory.objects.all().count()
    totalOnlineClasses = devModels.Online_sessions.objects.all().count()
    totalContactDetails = Contact_us.objects.all().count()
    totalShortlistedStudentData = User.objects.filter(role="Student").count()
    totalCourseEnrollmentData = Course_Enrollment.objects.all().count()
    totalFeedbacks = Feedback.objects.all().count()
    totalIssuedCertificates = devModels.Issued_Certificate.objects.all().count()
    totalCourses = devModels.Online_Certification_Course.objects.all().count()
    context = {
        'totalStudents':totalStudents,
        'totalDevelopers':totalDevelopers,
        'totalQuiz':totalQuiz,
        'totalOnlineClasses':totalOnlineClasses,
        'totalContactDetails':totalContactDetails,
        'totalShortlistedStudentData':totalShortlistedStudentData,
        'totalCourseEnrollmentData':totalCourseEnrollmentData,
        'totalFeedbacks':totalFeedbacks,
        'totalIssuedCertificates':totalIssuedCertificates,
        "totalCourses":totalCourses,
    }
    return render(request,'adminapp/index.html',context=context)

def signout(request):
    logout(request)
    return redirect(TCL_views.main_login)

def formview(request):
    return render(request,'adminapp/form.html')

def studentTable(request):
    query = request.GET.get('search', '')
    students = User.objects.filter(role="Student", is_superuser=False)
    if query:
        students = students.filter(
            Q(username__icontains=query) | Q(course__icontains=query) | Q(institute_name__icontains=query)
        )
    paginator = Paginator(students, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'students': page_obj,
        'search_query': query
    }
    return render(request, 'adminapp/student-table.html', context)

def deleteUser(request,id):
    data = User.objects.get(id=id)
    data.delete()
    return redirect(studentTable)

def chartview(request):
    return render(request,'adminapp/chart.html')

def widget(request):
    return render(request,'adminapp/widget.html')

def assessment(request):
    return render(request,'adminapp/assessment.html')

def admin_add_form(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirmPassword')
        if password == confirmPassword:
            try:
                User.objects.get(username=username)
                return render(request,"adminapp/admin-add-form.html",{'alert':"Admin already exist"})
            except:
                User.objects.create_user(
                    username=username,
                    password=password,
                    role=User.ADMIN,
                    is_superuser=True,
                    is_staff=True,
                )
                return render(request,"adminapp/admin-add-form.html",{'new_add_msg':"New Admin Created"})
        else:
            return render(request,"adminapp/admin-add-form.html",{'error':"Password Doesn't Match"})
    return render(request,"adminapp/admin-add-form.html")


def dev_list_table(request):
    query = request.GET.get('search', '')
    dev_details = User.objects.filter(role="Developer")
    if query:
        dev_details = dev_details.filter(
            Q(username__icontains=query) | Q(company_name__icontains=query)
        )
    paginator = Paginator(dev_details, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'dev_details': page_obj,
        'search_query': query
    }
    return render(request, "adminapp/dev-table.html", context)


def authorize_dev(request,id):
    data = User.objects.get(id=id)
    if request.method == "POST":
        data.is_verified = True
        data.save()
        return redirect(dev_list_table)
    return render(request,"adminapp/dev-table.html")

def unauthorize_dev(request,id):
    data = User.objects.get(id=id)
    if request.method == "POST":
        data.is_verified = False
        data.save()
        return redirect(dev_list_table)
    return render(request,"adminapp/dev-table.html")

def deleteDev(request,id):
    data = User.objects.get(id=id)
    data.delete()
    return redirect(dev_list_table)

def quiz_category_list_table(request):
    quiz_data = devModels.QuizCategory.objects.all()
    context = {'quiz_data':quiz_data}
    return render(request,"adminapp/quiz-category-list-table.html",context=context)

def delete_quiz_category(request,id):
    data = devModels.QuizCategory.objects.get(id=id)
    if request.user.role == "Admin":
        data.delete()
        return redirect(quiz_category_list_table)
    elif request.user.role == "Developer":
        data.delete()
        return redirect(dev_views.table)


# def quiz_attempt_table(request):
#     data = Quiz_attempt.objects.all()
#     findTotalQuestions = devModels.QuizQuestions.objects.filter(quiz_category_id=data.quiz_category).count()
#     print("--------------------------->",findTotalQuestions)
#     context = {
#         'data':data
#     }
#     return render(request,"adminapp/quiz-attempts-table.html",context=context)

def quiz_attempt_table(request,id):
    data = Quiz_attempt.objects.filter(quiz_category=id)
    quiz_data = devModels.QuizCategory.objects.get(id=id)
    total_questions = devModels.QuizQuestions.objects.filter(quiz_category_id=id).count()
    paginator = Paginator(data, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'data': page_obj,
        'quiz_data':quiz_data,
        'total_questions':total_questions,
    }
    return render(request, "adminapp/quiz-attempts-table.html", context=context)


def delete_quiz_attempt(request,id):
    quiz_attempt_data = Quiz_attempt.objects.get(id=id)
    if request.user.role == "Admin":
        quiz_attempt_data.delete()
        return redirect(quiz_category_list_table)
    if request.user.role == "Developer":
        quiz_attempt_data.delete()
        return redirect(dev_views.quiz_category_table)


def manage_online_session_table(request):
    session_data = devModels.Online_sessions.objects.all()
    paginator = Paginator(session_data, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'session_data':page_obj
    }
    return render(request,"adminapp/manage-online-session-table.html",context=context)

def session_attempted_student(request,id):
    session_attempted_data = Attempted_session.objects.filter(session_id=id)
    session_data = devModels.Online_sessions.objects.get(id=id)
    session_name = session_data.topic_name
    context = {
        'session_data':session_attempted_data,
        'session_name':session_name
    }
    return render(request,"adminapp/session-attempted-student.html",context=context)


def shortlisted_student_detail(request):
    query = request.GET.get('search', '')
    shortlisted_student_data = User.objects.filter(role="Student")
    if query:
        shortlisted_student_data = shortlisted_student_data.filter(
            Q(username__icontains=query) | Q(company_name__icontains=query) | Q(institute_name__icontains=query) | Q(course__icontains=query)
        )
    paginator = Paginator(shortlisted_student_data, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'shortlisted_student_data': page_obj,
        'search_query': query
    }
    return render(request, "adminapp/shortlisted-student-detail.html", context)


def contact_details(request):
    contact_details_data = Contact_us.objects.all()
    paginator = Paginator(contact_details_data, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'contact_details_data':page_obj,
    }
    return render(request,"adminapp/contact-details.html",context=context)

def delete_contact_details(request,id):
    contact_data = Contact_us.objects.get(id=id)
    contact_data.delete()
    return redirect(contact_details)


def course_enrollment_data(request):
    query = request.GET.get('search', '')
    month = request.GET.get('month', '')
    year = request.GET.get('select', '')

    data = Course_Enrollment.objects.all()

    if query:
        data = data.filter(
            Q(student_id__username__icontains=query) |
            Q(course_id__course_name__icontains=query) |
            Q(course_id__course_type__icontains=query)
        )

    if month and month != "None":
        month_number = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
            'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
            'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }.get(month)
        if month_number:
            data = data.filter(date_time__month=month_number)

    if year:
        data = data.filter(date_time__year=year)

    paginator = Paginator(data, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    context = {
        'course_enrollment_data': page_obj,
        'search_query': query,
        'selected_month': month,
        'selected_year': year,
        'months': months
    }
    return render(request, "adminapp/course-enrollment-data.html", context)


def generate_course_enrollment_pdf(request):
    query = request.GET.get('search', '')
    month = request.GET.get('month', '')
    year = request.GET.get('select', '')
    data = Course_Enrollment.objects.all()
    if query:
        data = data.filter(
            Q(student_id__username__icontains=query) |
            Q(course_id__course_name__icontains=query) |
            Q(course_id__course_type__icontains=query)
        )
    if month and month != "None":
        month_number = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
            'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
            'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }.get(month)
        if month_number:
            data = data.filter(date_time__month=month_number)

    if year:
        data = data.filter(date_time__year=year)
    filename_parts = ["TCL_course_enrollment_report"]
    if month and month != "None":
        filename_parts.append(month)
    if year:
        filename_parts.append(str(year))
    filename = "_".join(filename_parts) + ".pdf"

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    pdf = SimpleDocTemplate(response, pagesize=landscape(letter))
    elements = []
    styles = getSampleStyleSheet()
    centered_title = ParagraphStyle(name='CenteredTitle', parent=styles['Title'], alignment=TA_CENTER)
    centered_heading = ParagraphStyle(name='CenteredHeading', parent=styles['Heading1'], alignment=TA_CENTER)
    
    elements.append(Paragraph("<b>The Career Linker</b>", centered_title))
    elements.append(Spacer(1, 6))
    
    report_title = "Course Enrollment Report"
    if month and month != "None" and year:
        report_title += f" for {month} {year}"
    elif month and month != "None":
        report_title += f" for {month}"
    elif year:
        report_title += f" for {year}"
    elements.append(Paragraph(report_title, centered_heading))
    elements.append(Spacer(1, 12))
    # Table column
    table_data = [[
        Paragraph("ID", styles['Normal']),
        Paragraph("Student", styles['Normal']),
        Paragraph("Course", styles['Normal']),
        Paragraph("Type", styles['Normal']),
        Paragraph("Price", styles['Normal']),
        Paragraph("Payment", styles['Normal']),
        Paragraph("Course Status", styles['Normal']),
        Paragraph("Payment ID", styles['Normal']),
        Paragraph("Order ID", styles['Normal']),
        Paragraph("Date", styles['Normal']),
    ]]
    total_amount = 0
    for index, course_data in enumerate(data, start=1):
        course_type = course_data.course_id.course_type
        course_price = course_data.course_id.course_charges if course_type != "Free" else 0
        total_amount += int(course_price)
        table_data.append([
            Paragraph(str(index), styles['Normal']),
            Paragraph(course_data.student_id.username, styles['Normal']),
            Paragraph(course_data.course_id.course_name, styles['Normal']),
            Paragraph(course_type, styles['Normal']),
            Paragraph(str(course_price) if course_price else "-", styles['Normal']),
            Paragraph("Paid" if course_data.is_payment_received else "-", styles['Normal']),
            Paragraph("Completed" if course_data.is_course_completed else "Not Completed", styles['Normal']),
            Paragraph(course_data.razorpay_payment_id or "-", styles['Normal']),
            Paragraph(course_data.razorpay_order_id or "-", styles['Normal']),
            Paragraph(course_data.date_time.strftime('%Y-%m-%d') if course_data.date_time else "-", styles['Normal']),
        ])
    # Add total row
    table_data.append([
        "-", 
        Paragraph("<b>Total</b>", styles['Normal']),
        "-", 
        "-", 
        Paragraph(f"<b>{total_amount}</b>", styles['Normal']),
        "-", 
        "-", 
        "-", 
        "-", 
        "-"
    ])

    # Column widths
    col_widths = [
        0.4 * inch,  # ID
        1.2 * inch,  # Student
        1.6 * inch,  # Course
        0.6 * inch,  # Type
        0.5 * inch,  # Price
        0.9 * inch,  # Payment
        0.9 * inch,  # Course Status
        1.6 * inch,  # Payment ID
        1.6 * inch,  # Order ID
        1.2 * inch,  # Date
    ]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (-10, -1), (-1, -1), 'Helvetica-Bold'),  # Bold for total row
    ]))

    elements.append(table)
    pdf.build(elements)
    return response


def feedback_table(request):
    feedback_data = Feedback.objects.all()
    paginator = Paginator(feedback_data, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'feedback_data':page_obj
    }
    return render(request,"adminapp/feedback-table.html",context=context)

def delete_feedback(request,id):
    feedback_data = Feedback.objects.get(id=id)
    feedback_data.delete()
    return redirect(feedback_table)


def issued_certificate_detail(request):
    query = request.GET.get('search', '')
    # data = Course_Enrollment.objects.all()
    issued_certificate_data = devModels.Issued_Certificate.objects.all()
    if query:
        issued_certificate_data = issued_certificate_data.filter(
            Q(student_id__username__icontains=query) | 
            Q(course_id__course_name__icontains=query) | 
            Q(course_id__course_type__icontains=query) |
            Q(digital_signature__icontains=query)
        )
    paginator = Paginator(issued_certificate_data, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'issued_certificate_data':page_obj,
        'search_query': query
    }
    return render(request,"adminapp/issued-certificate-details.html",context=context)


def manage_course_details(request):
    course_data = devModels.Online_Certification_Course.objects.all()
    paginator = Paginator(course_data, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'course_data':page_obj,
    }
    return render(request,"adminapp/manage-course-details.html",context=context)


def delete_course(request,id):
    course_data = devModels.Online_Certification_Course.objects.get(id=id)
    course_data.delete()
    return redirect(manage_course_details)