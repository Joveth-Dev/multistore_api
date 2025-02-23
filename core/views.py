from djoser.views import UserViewSet as BaseUserViewSet


class UserViewSet(BaseUserViewSet):
    def get_queryset(self):
        return super().get_queryset().prefetch_related("groups")

    def get_instance(self):
        """
        For the '/me' endpoint, Djoser normally sets:
           self.get_object = self.get_instance
        and simply returns 'request.user'.

        We want to return the *prefetched* user object from the database
        so that accessing '.groups' won't cause multiple queries.
        """
        if self.action == "me":
            return self.get_queryset().get(pk=self.request.user.pk)
        return super().get_instance()
