from django.urls import path

from . import views

urlpatterns = [
    path("auth/csrf/", views.csrf),
    path("auth/login/", views.login_view),
    path("auth/logout/", views.logout_view),
    path("auth/role/", views.SelectRole.as_view()),
    path("me/", views.Me.as_view()),
    path("profile/photo/", views.MyPhoto.as_view()),
    path("teacher/sections/", views.TeacherSections.as_view()),
    path("teacher/report/pdf/", views.TeacherReport.as_view()),
    path("catalog/", views.Catalog.as_view()),
    path("preselection/", views.PreselectionView.as_view()),
    path("enrollments/", views.EnrollmentView.as_view()),
    path("enrollments/<int:enrollment_id>/pdf/", views.Receipt.as_view()),
    path("grades/", views.Grades.as_view()),
    path("admin/data/", views.AdminData.as_view()),
    path("admin/periods/", views.AdminPeriod.as_view()),
    path("admin/periods/<int:pk>/", views.AdminPeriod.as_view()),
    path("admin/plans/", views.AdminPlan.as_view()),
    path("admin/courses/", views.AdminCourse.as_view()),
    path("admin/courses/<int:pk>/", views.AdminCourse.as_view()),
    path("admin/sections/", views.AdminSection.as_view()),
    path("admin/sections/<int:pk>/", views.AdminSection.as_view()),
    path("admin/teachers/", views.AdminTeacher.as_view()),
    path("admin/students/", views.AdminStudent.as_view()),
    path("admin/grades/", views.AdminGrade.as_view()),
    path("admin/demand/", views.AdminDemand.as_view()),
    path("admin/audit/", views.AdminAudit.as_view()),
]
