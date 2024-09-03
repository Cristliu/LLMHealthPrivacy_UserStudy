from django.urls import path
from LLMHPri import views

app_name = 'LLMHPri'

urlpatterns = [
    path('encindexzh/', views.encindexzh,name="encindexzh"),
    path('showMessageAlert/', views.showMessageAlert,name="showMessageAlert"),
    path('dialogue/', views.dialogue,name="dialogue"),
    path('survey/', views.survey,name="survey"),
    path('send_message/<int:session_id>/', views.send_message, name='send_message'),
    path('send_message_en/<int:session_id>/', views.send_message_en, name='send_message_en'),
    path('end_session/<int:session_id>/', views.end_session, name='end_session'),
    path('end_session_en/<int:session_id>/', views.end_session_en, name='end_session_en'),
    path('encindexen/', views.encindexen, name='encindexen'),
    path('qnsurvey/', views.qnsurvey, name='qnsurvey'),
    path('consultdia/', views.consultdia,name="consultdia"),
]