from rest_framework import generics
from .models import Todo
from .serializers import TodoSerializer
from rest_framework.response import Response

class TodoListCreateView(generics.ListCreateAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer

class TodoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer

class AllTodoListView(generics.ListAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer

class TodoUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    partial = True

class TodoDeleteView(generics.DestroyAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(print("Todo deleted"))