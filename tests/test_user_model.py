import unittest

from app.models import Role, User, Permission, AnonymousUser


class UserModelTestCase(unittest.TestCase):
    def test_roles_and_permissions(self):
        Role.insert_roles()
        u = User(email='123456@example.com', password='password')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))
        self.assertFalse(u.can(Permission.ADMINISTRATOR))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))
        self.assertFalse(u.can(Permission.ADMINISTRATOR))
        self.assertFalse(u.can(Permission.COMMENT))

    def test_administrator(self):
        u=User(email='kevinforlj@163.com',password='password')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.MODERATE_COMMENTS))
        self.assertTrue(u.can(Permission.ADMINISTRATOR))

