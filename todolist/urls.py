
from django.urls import path
from todolist.views import TodoListCreateView, TodoDetailView, AllTodoListView, TodoUpdateView, TodoDeleteView

urlpatterns = [
    path('', TodoListCreateView.as_view(), name='to-do-list-create'),
    path('<int:pk>/', TodoDetailView.as_view(), name='to-do-list-detail'),
    path('all/', AllTodoListView.as_view(), name='all-to-do-list'),
    path('delete/<int:pk>/', TodoUpdateView.as_view(), name='to-do-list-delete'),
    path('update/<int:pk>/', TodoDeleteView.as_view(), name='to-do-list-update'),

]
