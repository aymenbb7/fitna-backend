from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QuizViewSet, QuestionViewSet, StartQuizAttemptView,
    SubmitQuizAttemptView, QuizResultsAdminView, QuizMyResultsView
)

router = DefaultRouter()
router.register(r'', QuizViewSet, basename='quiz')

urlpatterns = [
    path('<int:pk>/start/', StartQuizAttemptView.as_view(), name='quiz_start'),
    path('<int:pk>/submit/', SubmitQuizAttemptView.as_view(), name='quiz_submit'),
    path('<int:pk>/results/', QuizResultsAdminView.as_view(), name='quiz_results_admin'),
    path('<int:pk>/my-results/', QuizMyResultsView.as_view(), name='quiz_my_results'),
    
    path('<int:quiz_pk>/questions/', QuestionViewSet.as_view({'get': 'list', 'post': 'create'}), name='question_list'),
    path('<int:quiz_pk>/questions/<int:pk>/', QuestionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='question_detail'),
    
    path('', include(router.urls)),
]
