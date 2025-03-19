from construct import Struct, Tell, Bytes, Computed
from typing_extensions import Literal, TypedDict

from archerdfu.profile.typedefs.profile import CalcDataHeader, Profile, PROFILES_COUNT, DragCoeff

DragModelType = Literal['G1', 'G7', 'CUSTOM', 'UNKNOWN']


class DragPoint(TypedDict):
    mach: float
    cd: float


class DragModel(list):

    def __init__(self, *coeffs: DragPoint, typ: DragModelType):
        if not all(self._is_valid_drag_point(r) for r in coeffs):
            raise TypeError("Value should match DragPoint signature")
        super().__init__(coeffs)
        self.typ = typ

    def __setitem__(self, index, value):
        if not self._is_valid_drag_point(value):
            raise TypeError(f"Value should match DragPoint signature")
        super().__setitem__(index, value)
        self._sort()

    def append(self, value: DragPoint):
        if not self._is_valid_drag_point(value):
            raise TypeError("Value should match DragPoint signature")
        super().append(value)
        self._sort()

    def extend(self, values):
        if not all(self._is_valid_drag_point(v) for v in values):
            raise TypeError("All values should match DragPoint signature")
        super().extend(values)
        self._sort()  # Sort after extending

    def insert(self, index, value):
        if not self._is_valid_drag_point(value):
            raise TypeError("Value should match DragPoint signature")
        super().insert(index, value)
        self._sort()  # Sort after inserting

    def __repr__(self):
        return f"<{self.__class__.__name__}({super().__repr__()})>"

    def _sort(self):
        """Sort the list by mach after any modification."""
        self.sort(key=lambda x: x["mach"])

    @staticmethod
    def _is_valid_drag_point(d: dict) -> bool:
        return (
                isinstance(d, dict)
                and all(key in d for key in DragPoint.__annotations__)  # Ensure required keys exist
                and isinstance(d.get("mach"), (float, int))
                and isinstance(d.get("cd"), (float, int))
        )


def _split_tables(ctx):
    tables = []
    for prof in ctx.profiles:
        table = ctx.table[prof.drf_start:prof.drf_end]
        tables.append(DragModel(*table, typ=prof.bc_type))
    return tables


prof = Struct(
    'header' / CalcDataHeader,
    'profiles' / Profile[lambda ctx: ctx.header.profiles_count],
    '_empty_profiles' / Profile[lambda ctx: PROFILES_COUNT - ctx.header.profiles_count],
    '_profiles_end' / Tell,
    'pad' / Bytes(lambda ctx: ctx.header.c_drag_func_start - ctx._profiles_end),
    'table' / DragCoeff[lambda ctx: ctx.header.c_drag_func_start + ctx.header.c_drag_func_size // DragCoeff.sizeof()],
    'tables' / Computed(_split_tables),
)


def test_profile_parse():
    with open("../assets/profiles.dfu", 'rb') as fp:
        buffer = fp.read()[4096:]

    profiles = prof.parse(buffer)
    # print(profiles)
    #
    # print(profiles.pad)
    # end 421 / 6444
    print(profiles.tables[0].typ)

    print(profiles)
