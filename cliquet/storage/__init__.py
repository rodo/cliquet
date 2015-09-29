import random
from collections import namedtuple

from . import generators


Filter = namedtuple('Filter', ['field', 'value', 'operator'])
"""Filtering properties."""

Sort = namedtuple('Sort', ['field', 'direction'])
"""Sorting properties."""

DEFAULT_ID_FIELD = 'id'
DEFAULT_MODIFIED_FIELD = 'last_modified'
DEFAULT_DELETED_FIELD = 'deleted'

_HEARTBEAT_DELETE_RATE = 0.6
_HEARTBEAT_COLLECTION_ID = '__heartbeat__'
_HEART_PARENT_ID = _HEARTBEAT_COLLECTION_ID
_HEARTBEAT_RECORD = {'__heartbeat__': True}


class StorageBase(object):
    """Storage abstraction used by resource views.

    It is meant to be instantiated at application startup.
    Any operation may raise a `HTTPServiceUnavailable` error if an error
    occurs with the underlying service.

    Configuration can be changed to choose which storage backend will
    persist the objects.

    :raises: :exc:`~pyramid:pyramid.httpexceptions.HTTPServiceUnavailable`
    """

    id_generator = generators.UUID4()

    def initialize_schema(self):
        """Create every necessary objects (like tables or indices) in the
        backend.

        This is excuted when the ``cliquet migrate`` command is ran.
        """
        raise NotImplementedError

    def flush(self, request=None):
        """Remove **every** object from this storage.
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`
        """
        raise NotImplementedError

    def ping(self, request):
        """Test that storage is operationnal.

        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`
        :returns: ``True`` is everything is ok, ``False`` otherwise.
        :rtype: bool
        """
        try:
            if random.random() < _HEARTBEAT_DELETE_RATE:
                self.delete_all(_HEARTBEAT_COLLECTION_ID, _HEART_PARENT_ID,
                                request=request)
            else:
                self.create(_HEARTBEAT_COLLECTION_ID, _HEART_PARENT_ID,
                            _HEARTBEAT_RECORD, request=request)
            return True
        except:
            return False

    def collection_timestamp(self, collection_id, parent_id, request=None):
        """Get the highest timestamp of every objects in this `collection_id` for
        this `parent_id`.

        .. note::

            This should take deleted objects into account.

        :param str collection_id: the collection id.
        :param str parent_id: the collection parent.
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`

        :returns: the latest timestamp of the collection.
        :rtype: int
        """
        raise NotImplementedError

    def create(self, collection_id, parent_id, object, id_generator=None,
               unique_fields=None, id_field=DEFAULT_ID_FIELD,
               modified_field=DEFAULT_MODIFIED_FIELD,
               request=None):
        """Create the specified `object` in this `collection_id` for this `parent_id`.
        Assign the id to the object, using the attribute
        :attr:`cliquet.resource.BaseResource.id_field`.

        .. note::

            This will update the collection timestamp.

        :raises: :exc:`cliquet.storage.exceptions.UnicityError`

        :param str collection_id: the collection id.
        :param str parent_id: the collection parent.
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`

        :param dict object: the object to create.

        :returns: the newly created object.
        :rtype: dict
        """
        raise NotImplementedError

    def get(self, collection_id, parent_id, object_id,
            id_field=DEFAULT_ID_FIELD,
            modified_field=DEFAULT_MODIFIED_FIELD,
            request=None):
        """Retrieve the object with specified `object_id`, or raise error
        if not found.

        :raises: :exc:`cliquet.storage.exceptions.RecordNotFoundError`

        :param str collection_id: the collection id.
        :param str parent_id: the collection parent.
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`

        :param str object_id: unique identifier of the object

        :returns: the object object.
        :rtype: dict
        """
        raise NotImplementedError

    def update(self, collection_id, parent_id, object_id, object,
               unique_fields=None, id_field=DEFAULT_ID_FIELD,
               modified_field=DEFAULT_MODIFIED_FIELD,
               request=None):
        """Overwrite the `object` with the specified `object_id`.

        If the specified id is not found, the object is created with the
        specified id.

        .. note::

            This will update the collection timestamp.

        :raises: :exc:`cliquet.storage.exceptions.UnicityError`

        :param str collection_id: the collection id.
        :param str parent_id: the collection parent.
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`

        :param str object_id: unique identifier of the object
        :param dict object: the object to update or create.

        :returns: the updated object.
        :rtype: dict
        """
        raise NotImplementedError

    def delete(self, collection_id, parent_id, object_id,
               with_deleted=True, id_field=DEFAULT_ID_FIELD,
               modified_field=DEFAULT_MODIFIED_FIELD,
               deleted_field=DEFAULT_DELETED_FIELD,
               request=None):
        """Delete the object with specified `object_id`, and raise error
        if not found.

        Deleted objects must be removed from the database, but their ids and
        timestamps of deletion must be tracked for synchronization purposes.
        (See :meth:`cliquet.storage.StorageBase.get_all`)

        .. note::

            This will update the collection timestamp.

        :raises: :exc:`cliquet.storage.exceptions.RecordNotFoundError`

        :param str collection_id: the collection id.
        :param str parent_id: the collection parent.
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`

        :param str object_id: unique identifier of the object
        :param bool with_deleted: track deleted record with a tombstone

        :returns: the deleted object, with minimal set of attributes.
        :rtype: dict
        """
        raise NotImplementedError

    def delete_all(self, collection_id, parent_id, filters=None,
                   with_deleted=True, id_field=DEFAULT_ID_FIELD,
                   modified_field=DEFAULT_MODIFIED_FIELD,
                   deleted_field=DEFAULT_DELETED_FIELD,
                   request=None):
        """Delete all objects in this `collection_id` for this `parent_id`.

        :param str collection_id: the collection id.
        :param str parent_id: the collection parent.
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`

        :param filters: Optionnally filter the objects to delete.
        :type filters: list of :class:`cliquet.storage.Filter`
        :param bool with_deleted: track deleted records with a tombstone

        :returns: the list of deleted objects, with minimal set of attributes.
        :rtype: list of dict
        """
        raise NotImplementedError

    def purge_deleted(self, collection_id, parent_id, before=None,
                      id_field=DEFAULT_ID_FIELD,
                      modified_field=DEFAULT_MODIFIED_FIELD,
                      request=None):
        """Delete all deleted object tombstones in this `collection_id`
        for this `parent_id`.

        :param str collection_id: the collection id.
        :param str parent_id: the collection parent.
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`

        :param int before: Optionnal timestamp to limit deletion (exclusive)

        :returns: The number of deleted objects.
        :rtype: int

        """
        raise NotImplementedError

    def get_all(self, collection_id, parent_id, filters=None, sorting=None,
                pagination_rules=None, limit=None, include_deleted=False,
                id_field=DEFAULT_ID_FIELD,
                modified_field=DEFAULT_MODIFIED_FIELD,
                deleted_field=DEFAULT_DELETED_FIELD,
                request=None):
        """Retrieve all objects in this `collection_id` for this `parent_id`.

        :param str collection_id: the collection id.
        :param str parent_id: the collection parent.
        :param request: Optional current request object.
        :type request: :class:`~pyramid:pyramid.request.Request`

        :param filters: Optionally filter the objects by their attribute.
            Each filter in this list is a tuple of a field, a value and a
            comparison (see `cliquet.utils.COMPARISON`). All filters
            are combined using *AND*.
        :type filters: list of :class:`cliquet.storage.Filter`

        :param sorting: Optionnally sort the objects by attribute.
            Each sort instruction in this list refers to a field and a
            direction (negative means descending). All sort instructions are
            cumulative.
        :type sorting: list of :class:`cliquet.storage.Sort`

        :param pagination_rules: Optionnally paginate the list of objects.
            This list of rules aims to reduce the set of objects to the current
            page. A rule is a list of filters (see `filters` parameter),
            and all rules are combined using *OR*.
        :type pagination_rules: list of list of :class:`cliquet.storage.Filter`

        :param int limit: Optionnally limit the number of objects to be
            retrieved.

        :param bool include_deleted: Optionnally include the deleted objects
            that match the filters.

        :returns: the limited list of objects, and the total number of
            matching objects in the collection (deleted ones excluded).
        :rtype: tuple (list, integer)
        """
        raise NotImplementedError
