import json
from pathlib import Path
from collections import UserDict
import typing


class JsonDict(UserDict):
    def __init__(self, file_path: Path = None, parent: tuple['JsonDict', str] = None, data: dict = None):
        if (file_path is None) and not (parent is not None and data is not None):
            raise ValueError()

        self.data = data or {}

        if file_path is not None:
            self._file: Path = Path(file_path)

            try:
                self.data = json.loads(self._file.read_text())
            except json.decoder.JSONDecodeError:
                self.data = data or {}
                self._file.write_text(json.dumps(self.data))

        self._parent = parent

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

        if self._parent is not None:
            self._parent[0].data[self._parent[1]] = self

        for key, value in self.data.items():
            if not isinstance(value, (dict, JsonDict)):
                continue

            self.data[key] = self._process_basic_dict(value, key)
        self.save()

    def save(self):
        if self._parent is not None:
            self._parent[0].save()
            return

        self._file.write_text(self.to_json())

    def _process_basic_dict(self, basic_dict: dict, pos: str):
        for key, value in basic_dict.items():
            if isinstance(value, dict):
                basic_dict[key] = self._process_basic_dict(value, key)

        return JsonDict(parent=(self, pos), data=basic_dict)

    def to_json(self) -> str:
        res = json.dumps(self.to_dict())
        return res

    def to_dict(self) -> dict:
        res: dict = eval(f'{self}'.replace('JsonDict(', '').replace(')', ''))
        return {int(key) if (not isinstance(key, int)) and (key.removeprefix('-').isdigit()) else key: value for
                key, value in res.items()}

    def __setattr__(self, key, value):
        if key == 'data' and isinstance(value, JsonDict):
            value = value.data
        super().__setattr__(key, value)

    def __getitem__(self, key):
        item = super().__getitem__(key)
        if not isinstance(item, (dict, UserDict)):
            return item
        return self._process_basic_dict(item, key)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.data})'


class KeyToAttrMixin(UserDict):
    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError as e:
            try:
                return super().get(item)
            except KeyError:
                raise e


class FriendlyDict(KeyToAttrMixin):
    @staticmethod
    def _make_dict_available(d: dict[str, typing.Any],
                             annotations: dict[str, type],
                             aggressive: bool = False) -> dict[str, typing.Any]:
        for key, value in d.items():
            try:
                value_excepted_type = annotations[key]
            except KeyError:
                if aggressive:
                    raise TypeError(f'Dict item {key} not mentioned in the annotations')
                continue
            if type(value) != value_excepted_type:  # Потому что пайчарм ругается на isinstance
                if issubclass(value_excepted_type, FriendlyDict) and value_excepted_type != FriendlyDict:
                    d[key] = value_excepted_type(value)
                    continue
                if aggressive:
                    raise TypeError(f'Dict item {key} have type {type(value)}, but excepted {value_excepted_type}')
        return d

    def __init__(self, *args, aggressive: bool = False, **kwargs):
        if len(args) > 0:
            first_arg = args[0]
            if isinstance(first_arg, str):
                first_arg = json.loads(first_arg)
            try:
                kwargs.update(first_arg)
            except TypeError as e:
                print(first_arg)
                raise e

        kwargs = self._make_dict_available(kwargs,
                                           typing.get_type_hints(self.__class__),
                                           aggressive=aggressive)

        self.data = {}
        self.data.update(kwargs)

    def to_dict(self) -> dict:
        for key, value in self.data.items():
            try:
                json.dumps(value)
            except TypeError:
                self.data[key] = value.to_dict()
        return self.data
