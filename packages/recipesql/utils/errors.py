import logging


def log_exception(caller, row, table_name):
    logging.exception(
        f"Failed to complete {caller} on:\n{row} from {table_name} table."
    )


class TableError(TypeError):
    def __init__(self, row, model):
        logging.error(f"Invalid row {row} of type {model}.")
        self.message = "Table not found."
        self.code = 400
        super().__init__(self.message)


class UniqueError(ValueError):
    def __init__(self, caller, row, table_name):
        found = str(row) + " already" if "save" in caller else " doesn't"
        logging.error(f"{found} exists in {table_name} table.")

        self.message = "Invalid value in unique colmun"
        self.code = 400
        super().__init__(self.message)


class ColumnError(ValueError):
    def __init__(self, column, table_name):
        logging.error(f"{table_name} table does not have a {column} column.")
        self.message = "Invalid table's column."
        self.code = 400
        super().__init__(self.message)
