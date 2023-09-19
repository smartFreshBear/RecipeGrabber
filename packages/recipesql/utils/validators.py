from .errors import TableError, UniqueError


class Validators:
    def __init__(self, tables):
        self.tables = tables

    def table(self, row, filters):
        model = type(row) if not filters else row
        if (
            not (table_name := getattr(model, "__tablename__", False))
            or table_name not in self.tables.keys()
        ):
            raise TableError(row, model)

        return table_name, model

    def unique_row(self, caller, row, query, table_name):
        if ("save" in caller) ^ (not query):
            raise UniqueError(caller, row, table_name)
