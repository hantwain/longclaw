from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from longclaw.orders.models import Order
from longclaw.orders.serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Order.objects.all()

    @action(detail=True, methods=["post"])
    def refund_order(self, request, pk):
        """Refund the order specified by the pk"""
        order = Order.objects.get(id=pk)
        order.refund()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def fulfill_order(self, request, pk):
        """Mark the order specified by pk as fulfilled"""
        order = Order.objects.get(id=pk)
        order.fulfill()
        return Response(status=status.HTTP_204_NO_CONTENT)
