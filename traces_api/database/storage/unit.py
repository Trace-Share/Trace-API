from traces_api.database.model.unit import ModelUnit


class StorageUnit:

    def __init__(self, session):
        self.session = session

    def get_unit(self, id_unit):
        """

        :param id_unit:
        :return:
        """
        unit = self.session.query(ModelUnit).filter(ModelUnit.id_unit == id_unit).one()
        return unit

    def save_unit(self, unit):
        self.session.add(unit)
        self.session.commit()
        return unit
