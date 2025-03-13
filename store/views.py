from decimal import Decimal

from django.db import transaction
from django.db.models import Avg, Count, Exists, FloatField, OuterRef, Value
from django.db.models.functions import Coalesce
from django.db.models.query import Prefetch
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .models import Cart, CartItem, Category, Feedback, Order, OrderItem, Product, Store
from .permissions import IsCartItemOwner, IsCategoryOwner, IsProductOwner, IsStoreOwner
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    CategorySerializer,
    CreateOrderSerializer,
    FeedbackSerializer,
    ListAndRetrieveCartItemSerializer,
    ListAndRetrieveProductSerializer,
    OrderSerializer,
    ProductSerializer,
    StoreSerializer,
    UpdateCartItemSerializer,
    UpdateOrderStatusSerializer,
)


class StoreViewSet(ModelViewSet):
    serializer_class = StoreSerializer

    def get_queryset(self):
        queryset = Store.objects.prefetch_related("user__groups").select_related(
            "user", "address"
        )

        # Annotate rating for all queries
        queryset = queryset.annotate(
            rating=Coalesce(
                Avg("order__feedbacks__rating"),
                Value(0.0),
                output_field=FloatField(),
            )
        )

        if self.action in ["list", "retrieve"] and not self.request.user.is_staff:
            queryset = queryset.annotate(product_count=Count("product")).filter(
                product_count__gt=0, is_live=True
            )
            if self.request.user.is_authenticated:
                queryset = queryset.exclude(user=self.request.user)
        return queryset

    def get_permissions(self):
        user_groups = self.get_user_groups()
        if self.action == "my_store":
            if "Store Owner" not in user_groups:
                raise PermissionDenied({"store": "You must own a store!"})
        if self.action == "create":
            if self.request.user.is_staff:
                raise PermissionDenied({"store": "Admins cannot create a store!"})
            if "Store Owner" in user_groups:
                raise PermissionDenied({"store": "You're already a store owner!"})
            self.permission_classes = [IsAuthenticated]
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [AllowAny]
        if self.action in ["partial_update", "update", "destroy"]:
            self.permission_classes = [IsStoreOwner | IsAdminUser]
        return super().get_permissions()

    def get_serializer_context(self):
        if self.action == "create":
            return {"user": self.request.user}
        return super().get_serializer_context()

    def get_user_groups(self):
        user = self.request.user
        user_groups = getattr(user, "_cached_groups", None)
        if user_groups is None:
            user_groups = set(user.groups.values_list("name", flat=True))
            setattr(user, "_cached_groups", user_groups)
        return user_groups

    @action(detail=False, methods=["GET"])
    def my_store(self, request):
        store = Store.objects.annotate(
            rating=Coalesce(
                Avg("order__feedbacks__rating"), Value(0.0), output_field=FloatField()
            )
        ).get(user=request.user)
        return Response(self.get_serializer(store).data, status=status.HTTP_200_OK)


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Category.objects.prefetch_related(
            Prefetch("store__user__groups")
        ).select_related("store__user", "store__address")
        if user.is_staff:
            return queryset
        return queryset.filter(store__user=user)

    def get_permissions(self):
        if self.action == "create":
            user_groups = self.get_user_groups()
            if "Store Owner" not in user_groups:
                raise PermissionDenied({"store": "You must own a store!"})
        if self.action in ["partial_update", "update", "destroy"]:
            self.permission_classes = [IsCategoryOwner | IsAdminUser]
        return super().get_permissions()

    def get_serializer_context(self):
        return {"user": self.request.user}

    def get_user_groups(self):
        user = self.request.user
        user_groups = getattr(user, "_cached_groups", None)
        if user_groups is None:
            user_groups = set(user.groups.values_list("name", flat=True))
            setattr(user, "_cached_groups", user_groups)
        return user_groups


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related(
        Prefetch("store__user__groups")
    ).select_related("store__user", "store__address", "category")
    serializer_class = ProductSerializer
    filterset_fields = ["store"]

    def get_permissions(self):
        if self.action in ["create", "my_products"]:
            user_groups = self.get_user_groups()
            if "Store Owner" not in user_groups:
                raise PermissionDenied({"store": "You must own a store!"})
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [AllowAny]
        if self.action in ["partial_update", "update", "destroy"]:
            self.permission_classes = [IsProductOwner | IsAdminUser]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve", "my_products"]:
            self.serializer_class = ListAndRetrieveProductSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        response_serializer = ListAndRetrieveProductSerializer(
            product, context=self.get_serializer_context()
        )
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        response_serializer = ListAndRetrieveProductSerializer(
            instance, context=self.get_serializer_context()
        )

        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def get_serializer_context(self):
        return {"user": self.request.user}

    def get_user_groups(self):
        user = self.request.user
        user_groups = getattr(user, "_cached_groups", None)
        if user_groups is None:
            user_groups = set(user.groups.values_list("name", flat=True))
            setattr(user, "_cached_groups", user_groups)
        return user_groups

    @action(detail=False, methods=["GET"])
    def my_products(self, request):
        products = self.get_queryset().filter(store__user=request.user)
        return Response(
            self.get_serializer(products, many=True).data, status=status.HTTP_200_OK
        )


class CartViewSet(GenericViewSet, ListModelMixin):
    queryset = Cart.objects.prefetch_related(
        Prefetch(
            "cartitem_set",
            queryset=CartItem.objects.select_related("product__store__address"),
        )
    ).annotate(cart_item_count=Count("cartitem"))
    serializer_class = CartSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)
        return queryset


class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsCartItemOwner]

    def get_queryset(self):
        queryset = CartItem.objects.prefetch_related("cart__user").filter(
            cart__user=self.request.user
        )
        return queryset.order_by("-created_at")

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ListAndRetrieveCartItemSerializer
        if self.action in ["partial_update", "update"]:
            return UpdateCartItemSerializer
        else:
            return CartItemSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_cart = Cart.objects.get(user=self.request.user)
        new_product = serializer.validated_data.get("product")
        new_store = new_product.store  # Assuming the Product model has a store field

        # Fetch existing cart items
        existing_cart_items = CartItem.objects.filter(cart=user_cart)

        if existing_cart_items.exists():
            existing_store = (
                existing_cart_items.first().product.store
            )  # Get store of existing items

            if existing_store != new_store:
                # If the new product belongs to a different store, clear the cart
                existing_cart_items.delete()

        with transaction.atomic():
            cartitem, created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=new_product,
                defaults={"quantity": serializer.validated_data.get("quantity")},
            )
            if not created:
                cartitem.quantity += serializer.validated_data.get("quantity")
                cartitem.save()

        response_serializer = ListAndRetrieveCartItemSerializer(
            cartitem, context=self.get_serializer_context()
        )
        headers = self.get_success_headers(response_serializer.data)

        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        response_serializer = ListAndRetrieveCartItemSerializer(
            instance, context=self.get_serializer_context()
        )

        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def get_serializer_context(self):
        return {"user": self.request.user}


class OrderViewSet(GenericViewSet, CreateModelMixin):
    queryset = Order.objects.select_related(
        "cart__user", "store__address"
    ).prefetch_related("items__product", "feedbacks__customer")
    serializer_class = OrderSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return CreateOrderSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        return {"action": self.action}

    def create(self, request, *args, **kwargs):
        cart = self.request.user.cart
        cart_items = CartItem.objects.filter(cart=cart)
        if not cart_items.exists():
            raise ValidationError({"cart": "Your cart does not contain any items."})

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        print("validated_data", serializer.validated_data)
        store = serializer.validated_data.get("store")
        
        # set delivery_fee to 0 for Pick Up order
        if serializer.validated_data.get("type") == "Pick Up":
            store.delivery_fee = 0
            
        total_price = (
            sum(item.product.price * item.quantity for item in cart_items)
            + store.delivery_fee
        )
        order = Order.objects.create(
            cart=cart,
            total_price=total_price,
            **serializer.validated_data,
        )

        # Create OrderItem instances from CartItems
        order_items = [
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_per_item=Decimal(item.product.price * item.quantity),
            )
            for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)

        # Delete all CartItems from the cart
        cart_items.delete()

        headers = self.get_success_headers(serializer.data)
        return Response(
            OrderSerializer(order).data, status=status.HTTP_201_CREATED, headers=headers
        )

    def get_user_groups(self):
        user = self.request.user
        user_groups = getattr(user, "_cached_groups", None)
        if user_groups is None:
            user_groups = set(user.groups.values_list("name", flat=True))
            setattr(user, "_cached_groups", user_groups)
        return user_groups

    @action(detail=False, methods=["GET"])
    def my_orders(self, request: Request):
        user = request.user
        # Create subquery to check for existing feedback
        feedback_subquery = Feedback.objects.filter(customer=user, order=OuterRef("pk"))
        # Annotate queryset
        orders = (
            self.get_queryset()
            .filter(cart__user=user)
            .annotate(has_submitted_feedback=Exists(feedback_subquery))
        )
        return Response(
            self.get_serializer(orders, many=True).data, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["GET"])
    def my_store_orders(self, request: Request):
        user_groups = self.get_user_groups()
        if "Store Owner" not in user_groups:
            raise PermissionDenied({"store": "You must own a store!"})
        store = Store.objects.get(user=request.user)
        orders = self.get_queryset().filter(store=store)
        return Response(
            self.get_serializer(orders, many=True).data, status=status.HTTP_200_OK
        )

    @action(
        detail=True, methods=["PATCH"], serializer_class=UpdateOrderStatusSerializer
    )
    def update_order_status(self, request: Request, pk=None):
        user_groups = self.get_user_groups()
        if "Store Owner" not in user_groups:
            raise PermissionDenied({"store": "You must own a store!"})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = Order.objects.get(pk=pk)
        order.status = serializer.validated_data["status"]
        order.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


class FeedbackViewSet(GenericViewSet, CreateModelMixin):
    queryset = Feedback.objects.select_related(
        "customer", "order__store", "order__cart"
    )
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(order__store=self.request.user.store)
        return queryset

    def get_permissions(self):
        if self.action == "list":
            if "Store Owner" not in self.get_user_groups():
                raise PermissionDenied("You must own a store!")
        return super().get_permissions()

    def get_serializer_context(self):
        return {"customer": self.request.user}

    def get_user_groups(self):
        user = self.request.user
        user_groups = getattr(user, "_cached_groups", None)
        if user_groups is None:
            user_groups = set(user.groups.values_list("name", flat=True))
            setattr(user, "_cached_groups", user_groups)
        return user_groups
