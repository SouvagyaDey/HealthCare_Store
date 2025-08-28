from rest_framework import permissions
from .models import Order

class IsAdminOrOwner(permissions.BasePermission):
    """
    Allow access only to authenticated users.
    Admins can access all objects.
    Owners can only access their own objects.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        return obj.user == request.user


class IsOwnerOfOrderOrAdmin(permissions.BasePermission):
    """
    Allow access only to the owner of the order (for POST) or to admins.
    """

    def has_permission(self, request, view):
        # For creating (POST), check ownership from request.data
        if request.method == "POST":
            order_id = request.data.get("order")
            if not order_id:
                return False  # No order id given
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                return False
            return order.user == request.user or request.user.is_staff
        return True  # for other actions, defer to object permission

    def has_object_permission(self, request, view, obj):
        # For read/update/delete on an existing OrderItem
        if request.user.is_staff:
            return True
        return obj.order.user == request.user
