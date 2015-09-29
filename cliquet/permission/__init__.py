from cliquet.storage.exceptions import BackendError

__HEARTBEAT_KEY__ = '__heartbeat__'


class PermissionBase(object):

    def __init__(self, *args, **kwargs):
        pass

    def initialize_schema(self):
        """Create every necessary objects (like tables or indices) in the
        backend.

        This is excuted with the ``cliquet migrate`` command.
        """
        raise NotImplementedError

    def flush(self, request=None):
        """Delete all data stored in the permission backend.
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`
        """
        raise NotImplementedError

    def add_user_principal(self, user_id, principal, request=None):
        """Add an additional principal to a user.

        :param str user_id: The user_id to add the principal to.
        :param str principal: The principal to add.
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`
        """
        raise NotImplementedError

    def remove_user_principal(self, user_id, principal, request=None):
        """Remove an additional principal from a user.

        :param str user_id: The user_id to remove the principal to.
        :param str principal: The principal to remove.
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`
        """
        raise NotImplementedError

    def user_principals(self, user_id, request=None):
        """Return the set of additionnal principals given to a user.

        :param str user_id: The user_id to get the list of groups for.
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`
        :returns: The list of group principals the user is in.
        :rtype: set

        """
        raise NotImplementedError

    def add_principal_to_ace(self, object_id, permission, principal,
                             request=None):
        """Add a principal to an Access Control Entry.

        :param str object_id: The object to add the permission principal to.
        :param str permission: The permission to add the principal to.
        :param str principal: The principal to add to the ACE.
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`
        """
        raise NotImplementedError

    def remove_principal_from_ace(self, object_id, permission, principal,
                                  request=None):
        """Remove a principal to an Access Control Entry.

        :param str object_id: The object to remove the permission principal to.
        :param str permission: The permission that should be removed.
        :param str principal: The principal to remove to the ACE.
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`
        """
        raise NotImplementedError

    def object_permission_principals(self, object_id, permission,
                                     request=None):
        """Return the set of principals of a bound permission
        (unbound permission + object id).

        :param str object_id: The object_id the permission is set to.
        :param str permission: The permission to query.
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`
        :returns: The list of user principals
        :rtype: set

        """
        raise NotImplementedError

    def principals_accessible_objects(self, principals, permission,
                                      object_id_match=None,
                                      get_bound_permissions=None,
                                      request=None):
        """Return the list of objects id where the specified `principals`
        have the specified `permission`.

        :param list principal: List of user principals
        :param str permission: The permission to query.
        :param str object_id_match: Filter object ids based on a pattern
            (e.g. ``'*articles*'``).
        :param function get_bound_permissions:
            The methods to call in order to generate the list of permission to
            verify against. (ie: if you can write, you can read)
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`
        :returns: The list of object ids
        :rtype: set

        """
        raise NotImplementedError

    def object_permission_authorized_principals(self, object_id, permission,
                                                get_bound_permissions=None,
                                                request=None):
        """Return the full set of authorized principals for a given
        permission + object (bound permission).

        :param str object_id: The object_id the permission is set to.
        :param str permission: The permission to query.
        :param function get_bound_permissions:
            The methods to call in order to generate the list of permission to
            verify against. (ie: if you can write, you can read)
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`

        :returns: The list of user principals
        :rtype: set

        """
        raise NotImplementedError

    def check_permission(self, object_id, permission, principals,
                         get_bound_permissions=None,
                         request=None):
        """Test if a principal set have got a permission on an object.

        :param str object_id:
            The identifier of the object concerned by the permission.
        :param str permission: The permission to test.
        :param set principals:
            A set of user principals to test the permission against.
        :param function get_bound_permissions:
            The method to call in order to generate the set of
            permission to verify against. (ie: if you can write, you can read)
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`
        """
        principals = set(principals)
        authorized_principals = self.object_permission_authorized_principals(
            object_id, permission, get_bound_permissions)
        return len(authorized_principals & principals) > 0

    def ping(self, request, request=None):
        """Test the permission backend is operationnal.

        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`
        :returns: ``True`` is everything is ok, ``False`` otherwise.
        :rtype: bool
        """
        try:
            self.add_user_principal(__HEARTBEAT_KEY__, 'alive', request)
            self.remove_user_principal(__HEARTBEAT_KEY__, 'alive', request)
        except BackendError:
            return False
        return True

    def object_permissions(self, object_id, permissions=None, request=None):
        """Return the set of principals for each object permission.

        :param str object_id: The object_id the permission is set to.
        :param list permissions: List of permissions to retrieve.
                                 If not define will try to find them all.
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`
        :returns: The dictionnary with the list of user principals for
                  each object permissions
        :rtype: dict

        """
        raise NotImplementedError

    def replace_object_permissions(self, object_id, permissions, request=None):
        """Replace given object permissions.

        :param str object_id: The object to replace permissions to.
        :param str permissions: The permissions dict to replace.
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`
        """
        raise NotImplementedError

    def delete_object_permissions(self, *object_id_list, request=None):
        """Delete all listed object permissions.

        :param str object_id: Remove given objects permissions.
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`
        """
        raise NotImplementedError
