from django.contrib.auth.mixins import UserPassesTestMixin
class SmartUserIsOwnerMixin(UserPassesTestMixin):
    raise_exception = True
    admin_allowed = True

    def test_func(self):
        user = self.request.user
        obj = self.get_object()
        
        if hasattr(obj, 'can_manage'):
            return obj.can_manage(user, allow_admin=self.admin_allowed)

        return user.is_admin and self.admin_allowed

    def user_can_manage(self):
        """Этот метод используеться из шаблона"""
        return self.test_func()