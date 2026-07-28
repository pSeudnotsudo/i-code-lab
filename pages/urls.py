from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from django.urls import path
from django.shortcuts import render
from . import views



urlpatterns = [
    path('', views.index, name='index'),
    # AUTHENTICATION
    path('auth/',views.login_view,   name='login'),
    # path('auth/register/',views.register,name='register'),
    path('auth/confirm-email/<uidb64>/<token>/',views.confirm_email,name='confirm_email'),
    path('auth/confirm-sent/', lambda r: render(r, 'authentication/email_confirm_sent.html'),name='email_confirm_sent'),
    
    # ADMIN
    path('secure-control-9x7a2k-panel/',  views.icode_admin,  name='admin_dashboard'),
    path('icode-admin/create-user/',views.create_user, name='create_user'),
    path('activate/<uuid:token>/',views.activate_account,name='activate_account'),
    path('enrollment-list',  views.icode_enrollments,  name='enrollments_list'),
    path("enrollments/<int:pk>/update-status/", views.enrollment_update_status, name="enrollment_update_status"),
    path('age-brackets/',views.age_brackets,name='age_brackets'),

    path("age-brackets/store/",views.age_bracket_store,name="age_bracket_store"),
    
    path("statuses/",views.status_list,name="status_list"),
    path("statuses/store/",views.status_store,name="status_store"),
    path("statuses/<int:pk>/update/",views.status_update,name="status_update"),
    
    path("icode-admin/programs/",views.programs_list,name="programs_list"),
    path("programs/store/",views.program_store,name="program_store"),
    path("programs/<int:pk>/update/",views.program_update,name="program_update"),
    
    
    path("timelines/",views.timeline_list,name="timeline_list"),
    path("timelines/store/",views.timeline_store,name="timeline_store"),
    path("timelines/<int:pk>/update/",views.timeline_update,name="timeline_update"),
    
    
    # ENROLLMENT
    path("enrollments/store/", views.enrollment_store, name="enrollment_store"),
    
    # DASHBOARDS
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/parent/',  views.parent_dashboard,  name='parent_dashboard'),
    # path('dashboard/admin/',   views.admin_dashboard,   name='admin_dashboard'),

    
    # MORE ADMIN URLS 
    path("icode-admin/fees/", views.fees_manager, name="fees_manager"),
    path("icode-admin/program-types/",               views.program_types,          name="program_types"),
    path("icode-admin/program-types/store/",         views.program_type_store,     name="program_type_store"),
    path("icode-admin/program-types/<int:pk>/update/", views.program_type_update,  name="program_type_update"),

    path("icode-admin/term-fees/",                   views.term_fees,              name="term_fees"),
    path("icode-admin/term-fees/store/",             views.term_fee_store,         name="term_fee_store"),
    path("icode-admin/term-fees/<int:pk>/update/",   views.term_fee_update,        name="term_fee_update"),

    path("icode-admin/additional-costs/",            views.additional_costs,       name="additional_costs"),
    path("icode-admin/additional-costs/store/",      views.additional_cost_store,  name="additional_cost_store"),
    path("icode-admin/additional-costs/<int:pk>/update/", views.additional_cost_update, name="additional_cost_update"),

    path("icode-admin/fee-config/",                  views.fee_config,             name="fee_config"),
    path("icode-admin/fee-config/update/",           views.fee_config_update,      name="fee_config_update"),
    
    path("icode-admin/level-list/",            views.level_list,       name="level_list"),
    path("icode-admin/level-list/store/",      views.level_store,  name="level_store"),
    path("icode-admin/level-list/<int:pk>/update/", views.level_update, name="level_store_update"),

    path("icode-admin/tool-type-list/",            views.tool_type_list,       name="tool_type_list"),
    path("icode-admin/tool-type-list/store/",      views.tool_type_store,  name="tool_type_store"),
    path("icode-admin/tool-type-list/<int:pk>/update/", views.tool_type_update, name="tool_type_update"),

    path("icode-admin/program-tool-list/",            views.program_tool_list,       name="program_tool_list"),
    path("icode-admin/program-tool-store/store/",      views.program_tool_store,  name="program_tool_store"),
    path("icode-admin/program-tool-update/<int:pk>/update/", views.program_tool_update, name="program_tool_update"),
    # TESTIMONIALS ADMIN
      path("icodeadmin/testimonials/",                views.testimonials_admin,  name="testimonials_admin"),
    path("icode-admin/testimonials/<int:pk>/toggle/", views.testimonial_toggle,  name="testimonial_toggle"),
    path("icode-admin/testimonials/<int:pk>/delete/", views.testimonial_delete,  name="testimonial_delete"),
    
    #summer-bootcamp
    path('summer-bootcamp/', views.bootcamp_2026, name='bootcamp_2026'),
    path('submit-bootcamp-form/', views.submit_bootcamp_form, name='submit_bootcamp_form'),

    
    # PUBLIC URLS
    
    path('programs/', views.programs, name='programs'),
    path('about/', views.about, name='about'),
    path('logout/', views.logout_view, name='logout'),
    path('our-team/', views.team, name='team'),
    path('socials/', views.socials, name='socials'),
    path('privacy-policy/', views.serve_privacy_policy, name='serve_privacy_policy'),
    path('programs/<slug:slug>/', views.program_detail, name='programme-detail'),
    # TESTIMONIALS
    path("testimonial/submit/", views.submit_testimonial, name="submit_testimonial"),
    # UPLOAD IMAGES $ VIDEOS.
    path('gallery/upload/', views.gallery_upload, name='gallery_upload'),
    
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='authentication/password_reset_form.html',
        email_template_name='authentication/password_reset_email.html',
        success_url='/password-reset/sent/',
    ), name='password_reset'),

    path('password-reset/sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='authentication/password_reset_done.html',
    ), name='password_reset_done'),

    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='authentication/password_reset_confirm.html',
        success_url='/password-reset/complete/',
    ), name='password_reset_confirm'),

    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='authentication/password_reset_complete.html',
    ), name='password_reset_complete'),
    # terms and conditions
    path('terms/', views.terms, name='terms'),
    # NEWSLETTER SUBSCRIBE
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('newsletter/unsubscribe/<str:email>/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
    path('secure-control-9x7a2k-panel/gallery/', views.gallery_admin, name='gallery_admin'),
    path('secure-control-9x7a2k-panel/gallery/upload/', views.gallery_upload, name='gallery_upload'),
    path('secure-control-9x7a2k-panel/gallery/delete/<int:pk>/', views.gallery_delete, name='gallery_delete'),
    
    
    # ADMIN MEMBER PAGE UPLOAD

    # ── Team admin ──────────────────────────────────────────────────────
    path('team/',views.team_icode,name='team_members'),
    path('icode-admin/team/add/',                     views.team_member_add,      name='team_member_add'),
    path('icode-admin/team/<int:pk>/detail/',         views.team_member_detail,   name='team_member_detail'),
    path('icode-admin/team/<int:pk>/update/',         views.team_member_update,   name='team_member_update'),
    path('icode-admin/team/<int:pk>/toggle/',         views.team_member_toggle,   name='team_member_toggle'),
    path('icode-admin/team/<int:pk>/delete/',         views.team_member_delete,   name='team_member_delete'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    
    
    
    