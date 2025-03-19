from django.contrib import admin
from studentapp import models

# Register your models here.
admin.site.register(models.User)
admin.site.register(models.Bookmarked_session)
admin.site.register(models.Contact_us)
admin.site.register(models.Student_Course_Query)
admin.site.register(models.Feedback)


class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'quiz_category', 'score', 'date_time')  
    readonly_fields = ('date_time',)
admin.site.register(models.Quiz_attempt, QuizAttemptAdmin)

class AttemptedSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'student_name', 'date_time', 'is_attempted')  
    readonly_fields = ('date_time',)
admin.site.register(models.Attempted_session, AttemptedSessionAdmin)

class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'course_id', 'is_payment_received', 'is_course_completed','razorpay_payment_id','razorpay_order_id', 'razorpay_signature', 'date_time')
    readonly_fields = ('date_time',)
admin.site.register(models.Course_Enrollment, CourseEnrollmentAdmin)

class CourseProgressTrackerAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'course_id', 'document_id', 'quiz_id', 'is_completed', 'date_time')
    readonly_fields = ('date_time',)
admin.site.register(models.Course_Progress_Tracker, CourseProgressTrackerAdmin)

# @admin.register(models.Quiz_attempt)
# class Quiz_attempt(admin.ModelAdmin):
#     list_display = ['student_id','quiz_category','score','date_time']
    # model = models.Quiz_attempt