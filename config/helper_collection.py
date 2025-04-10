from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Dict, Union

import yaml


class ObjBuildingDict(ABC, dict):
    """
    Dictionary subclass that builds objects on demand from key and value.

    Extends the built‐in dict with the ability to “build” (or convert) a stored
    value into an object of a predefined type.
    Upon accessing an item via __getitem__, if the stored value is already an
    instance of the expected object type (specified during initialization via
    the 'obj' parameter), then that instance is returned as is. Otherwise, the
    abstract method build_obj(key, value) is called for a transformation.

    Subclasses must implement:
        build_obj(key: str, value: Any) -> object:
            Converts the raw value stored under key to a proper instance of the
            expected object type.

    Parameters
    ----------
    *args : any
        Positional arguments passed to the parent dict initializer.
    obj : object or None, optional
        Object used for the transformation. If provided, __getitem__ will check
        whether the stored value is an instance of this type, if not, build_obj
        will be invoked.
    **kwargs : dict
        Keyword arguments passed to the parent dict initializer.
    """

    def __init__(
        self,
        *args: Any,
        obj: Union[object, None] = None,
        **kwargs: Dict[str, Any],
    ):
        super().__init__(*args, **kwargs)
        self.obj = obj

    @abstractmethod
    def build_obj(self, key: str, value: Any) -> object:
        """
        Build and return the object corresponding to the given key.

        Parameters
        ----------
        key : str
            The dictionary key.
        value : Any
            The original value stored in the dictionary; typically not yet in
            the desired object form.

        Returns
        -------
        object
            The constructed object.
        """
        raise NotImplementedError

    def __getitem__(self, key: Any) -> Any:
        """
        Extends the built-in __getitem__ method to return the stored object
        if it is already an instance of the expected type, or build it using
        build_obj() otherwise.

        Parameters
        ----------
        key : str
            The key to look up.

        Returns
        -------
        object
            The stored object if it is already built, or the result of build_obj().
        """
        if self.obj is None:
            return super().__getitem__(key)
        try:
            obj = super().__getitem__(key)
            if isinstance(obj, self.obj):
                return obj
            return self.build_obj(key, obj)
        except KeyError:
            raise KeyError(f"Key {key} not found in the dictionary")


class NestedDefaultDict(defaultdict):
    """
    A nested defaultdict that allows for easy creation of
    multi-level dictionaries with default values.
    This class is a subclass of defaultdict and is used to
    create a nested dictionary structure where each level
    is also a defaultdict.
    """
    def __init__(self, *args, **kwargs) -> None:
        super(NestedDefaultDict, self).__init__(NestedDefaultDict, *args, **kwargs)

    def __repr__(self) -> str:
        return repr(dict(self))

    @property
    def regular(self) -> dict:
        """
        Convert the defaultdict to a regular dictionary, useful i.e. when saving as yaml
        """
        def convert(d):
            if isinstance(d, defaultdict):
                d = {k: convert(v) for k, v in d.items()}
            return d
        return convert(self)


class PreserveROOTPathsAsStrings(yaml.Dumper):
    """
    Custom YAML dumper that preserves ROOT paths as strings.
    This is necessary, since paths containing "root://" are not
    automatically converted to strings by PyYAML and raise errors upon loading.

    usage:
        yaml.dump(data, Dumper=PreserveROOTPathsAsStrings)

    """

    def represent_data(self, data):
        """
        Override the represent_data method to handle ROOT paths.
        """
        if isinstance(data, str) and data.startswith("root://"):
            return self.represent_scalar('tag:yaml.org,2002:str', data, style="'")

        return super(PreserveROOTPathsAsStrings, self).represent_data(data)
