import logging
from .errors import ColumnError


class Executors:
    def __init__(self, session):
        self.session = session

    def commit(self, caller, row, table_name):
        try:
            if "saved" in caller:
                self.session.add(row)

            elif "deleted" in caller:
                self.session.delete(row)

        except Exception as exc:
            self.session.rollback()
            raise exc

        else:
            self.session.commit()
            logging.info(f"{table_name} table {caller} row:\n{row}.")
            return row

    def update_row(self, table_name, table_row, updated_data: dict):
        try:
            for column, value in updated_data.items():
                if not hasattr(table_row, column):
                    raise ColumnError(column, table_name)

                setattr(table_row, column, value)
        except Exception as exc:
            raise exc

    def search_by(self, table_row, model, filters):
        table_name = model.__tablename__
        try:
            if filters:
                return model.query.filter(table_row.id == filters).first()

            filters = {
                column.name: getattr(table_row, column.name, None)
                for column in model.__table__.columns
                if column.unique
            }
            logging.info(f"{table_name} table search by filters:\n{filters}.")

            query = self.session.query(model).filter_by(**filters).first()
            logging.info(f"{table_name} table search result:\n{query}")

            return query
        except Exception as exc:
            raise exc
