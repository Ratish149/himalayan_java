from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as rest_filters
from rest_framework import generics

from .models import Branch
from .serializers import BranchSerializer


# -------------------------------
# Branch Views
# -------------------------------
class BranchListCreateView(generics.ListCreateAPIView):
    serializer_class = BranchSerializer
    filter_backends = [DjangoFilterBackend, rest_filters.SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "role") and user.role in ["admin"]:
            if user.branch:
                return Branch.objects.filter(id=user.branch.id)
            else:
                return Branch.objects.all()
        return Branch.objects.all()


class BranchDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BranchSerializer
    queryset = Branch.objects.all()
