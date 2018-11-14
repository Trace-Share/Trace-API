from datetime import datetime

from traces_api.database.model.annotated_unit import ModelAnnotatedUnit, ModelAnnotatedUnitLabel


class AnnotatedUnitService:

    def __init__(self, session):
        self._session = session

    def create_annotated_unit(self, name, description, id_author, stats, ip_mapping, file_location, labels):
        annotated_unit = ModelAnnotatedUnit(
            name=name,
            description=description,
            id_author=id_author,
            creation_time=datetime.now(),
            stats=None,
            ip_mapping="TODO",
            file_location=file_location,
            labels=[ModelAnnotatedUnitLabel(label=l) for l in labels]
        )

        self._session.add(annotated_unit)
        return annotated_unit
