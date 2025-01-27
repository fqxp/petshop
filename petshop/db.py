import os

from sqlalchemy import Engine
from sqlmodel import create_engine

_engine = None


def engine() -> Engine:
    global _engine

    if not _engine:
        _engine = create_engine(os.environ["DATABASE_URL"], echo=True)

    return _engine


# class CreateMaterializedView(DDLElement):
#     name: str
#     selectable: SelectBase
#
#     def __init__(self, name: str, selectable: SelectBase):
#         self.name = name
#         self.selectable = selectable
#
#
# class DropMaterializedView(DDLElement):
#     name: str
#
#     def __init__(self, name: str):
#         self.name = name
#
#
# @compiler.compiles(CreateMaterializedView)
# def _create_materialized_view(  # pyright: ignore[reportUnusedFunction]
#     element: CreateMaterializedView,
#     compiler: DDLCompiler,
#     **kwargs: dict[str, Any],  # pyright: ignore[reportUnusedParameter, reportExplicitAny]
# ):
#     return "CREATE MATERIALIZED VIEW %s AS %s" % (
#         element.name,
#         compiler.sql_compiler.process(element.selectable, literal_binds=True),
#     )
#
#
# @compiler.compiles(DropMaterializedView)
# def _drop_materialized_view(  # pyright: ignore[reportUnusedFunction]
#     element: DropMaterializedView,
#     compiler: DDLCompiler,  # pyright: ignore[reportUnusedParameter]
#     **kwargs: dict[str, Any],  # pyright: ignore[reportUnusedParameter, reportExplicitAny]
# ):
#     return "DROP MATERIALIZED VIEW %s" % (element.name)
#
#
# def generate_view_exists(name: str) -> DDLIfCallable:
#     def view_exists(
#         ddl: BaseDDLElement,  # pyright: ignore[reportUnusedParameter]
#         target: SchemaItem,  # pyright: ignore[reportUnusedParameter]
#         bind: Connection | None,
#         tables: list[Table] | None = None,  # pyright: ignore[reportUnusedParameter]
#         state: Any | None = None,  # pyright: ignore[reportExplicitAny, reportUnusedParameter]
#         *,
#         dialect: Dialect,  # pyright: ignore[reportUnusedParameter]
#         compiler: DDLCompiler | None = None,  # pyright: ignore[reportUnusedParameter]
#         checkfirst: bool,  # pyright: ignore[reportUnusedParameter]
#     ) -> bool:
#         inspection_object = inspect(bind)
#         return (
#             inspection_object is not None and name in inspection_object.get_view_names()  # pyright: ignore[reportAny]
#         )
#
#     return view_exists
#
#
# def generate_view_doesnt_exist(name: str) -> DDLIfCallable:
#     def view_doesnt_exist(
#         ddl: BaseDDLElement,
#         target: SchemaItem,
#         bind: Connection | None,
#         tables: list[Table] | None = None,
#         state: Any | None = None,  # pyright: ignore[reportExplicitAny]
#         *,
#         dialect: Dialect,
#         compiler: DDLCompiler | None = None,  # pyright: ignore[reportUnusedParameter]
#         checkfirst: bool,
#     ) -> bool:
#         view_exists: DDLIfCallable = generate_view_exists(name)
#         return not view_exists(
#             ddl, target, bind, tables, state, dialect=dialect, checkfirst=checkfirst
#         )
#
#     return view_doesnt_exist
#
#
# def create_materialized_view(
#     name: str, metadata: MetaData, selectable: SelectBase
# ) -> TableClause:
#     t = Table(
#         name,
#         MetaData(),
#         *(
#             Column(column.key, column.type, primary_key=column.primary_key)
#             for column in selectable.selected_columns
#         ),
#     )
#
#     # t.columns._populate_separate_keys(  # pyright: ignore[reportPrivateUsage]
#     #     column._make_proxy(t)  # pyright: ignore[reportPrivateUsage]
#     #     for column in selectable.selected_columns
#     # )
#
#     event.listen(
#         metadata,
#         "after_create",
#         CreateMaterializedView(name, selectable).execute_if(
#             callable_=generate_view_doesnt_exist(name)
#         ),
#     )
#     event.listen(
#         metadata,
#         "before_drop",
#         DropMaterializedView(name).execute_if(callable_=generate_view_exists(name)),
#     )
#
#     return t
