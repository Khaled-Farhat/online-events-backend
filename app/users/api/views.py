from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from ..models import User
from .serializers import UserSerializer
from .permissions import IsOwnerOrReadOnly


class UserViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrReadOnly]
    lookup_field = "username"
