from django.contrib.auth.mixins import UserPassesTestMixin

class SmartUserIsOwnerMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        user = self.request.user
        obj = self.get_object()

        if hasattr(obj, 'can_manage'):
            return obj.can_manage(user)

        creator = getattr(obj, 'creator', None)
        if creator is not None:
            return creator == user or user.is_admin

        if obj == user:
            return True

        return user.is_admin