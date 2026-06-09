from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from access_control.services import has_permission

# Бизнес логика захардкожена, так как в ТЗ не просили создавать под нее БД
# Надеюсь не будет ошибкой

PRODUCTS = [
    {"id": 1, "name": "Product 1", "owner_id": 1},
    {"id": 5, "name": "Product 2", "owner_id": 5}
]

ORDERS = [
    {"id": 1, "name": "Order 1", "owner_id": 1},
    {"id": 2, "name": "Order 2", "owner_id": 2},
]

SHOPS = [
    {"id": 1, "name": "Shop 1", "owner_id": 1},
    {"id": 2, "name": "Shop 2", "owner_id": 2},
]


def get_autenticated_user(request):
    user = getattr(request, "jwt_user", None)
    if not user or not getattr(user, "is_active", False):
        return None
    
    return user


def filter_owned_objects(objects, user):
    return [
        obj for obj in objects
        if obj["owner_id"] == user.id
    ]


class ProductsView(APIView):
    def get(self, request):
        user = get_autenticated_user(request)

        if user is None:
            return Response(
                {"detail": "Authentication creditials were not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        if has_permission(user, "products", "read_all"):
            return Response(PRODUCTS, status=status.HTTP_200_OK)
        
        if has_permission(user, "products", "read"):
            return Response(
                filter_owned_objects(PRODUCTS, user),
                status=status.HTTP_200_OK,
            )
        
        return Response(
            {"detail": "FOrbidden"},
            status=status.HTTP_403_FORBIDDEN,
        )
    
    def post(self, request):
        user = get_autenticated_user(request)

        if user is None:
            return Response(
                {"detail": "Authentication credentials were not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        if not has_permission(user, "products", "create"):
            return Response(
                {"detail": "Forbidden"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        return Response(
            {
                "message": "Product created successfully",
                "owner_id": user.id,
                "data": request.data,
            },
            status=status.HTTP_201_CREATED
        )
    

class OrdersView(APIView):
    def get(self, request):
        user = get_authenticated_user(request)

        if user is None:
            return Response(
                {"detail": "Authentication credentials were not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if has_permission(user, "orders", "read_all"):
            return Response(ORDERS, status=status.HTTP_200_OK)

        if has_permission(user, "orders", "read"):
            return Response(
                filter_owned_objects(ORDERS, user),
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "Forbidden"},
            status=status.HTTP_403_FORBIDDEN,
        )


class ShopsView(APIView):
    def get(self, request):
        user = get_authenticated_user(request)

        if user is None:
            return Response(
                {"detail": "Authentication credentials were not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if has_permission(user, "shops", "read_all"):
            return Response(SHOPS, status=status.HTTP_200_OK)

        if has_permission(user, "shops", "read"):
            return Response(
                filter_owned_objects(SHOPS, user),
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "Forbidden"},
            status=status.HTTP_403_FORBIDDEN,
        )
