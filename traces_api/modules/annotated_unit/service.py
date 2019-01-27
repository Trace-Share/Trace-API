import json
import sqlalchemy.exc
from enum import Enum
from datetime import datetime
from sqlalchemy import desc, or_, and_

from traces_api.database.model.annotated_unit import ModelAnnotatedUnit, ModelAnnotatedUnitLabel

from traces_api.trace_tools import TraceAnalyzer, TraceNormalizer
from traces_api.storage import FileStorage, File


class AnnotatedUnitDoesntExistsException(Exception):
    """
    Annotated unit does not exits
    This exception is raised when annotated unit is not found in database
    """
    pass


class UnableToRemoveAnnotatedUnitException(Exception):
    """
    Unable to remove annotated unit.
    Possible reason: There exists mix that contains this annotated unit
    """
    pass


class OperatorEnum(Enum):
    """
    SQL operators
    """
    AND = "AND"
    OR = "OR"


class AnnotatedUnitService:
    """
    This class allows to perform all business logic regarding to annotated units
    """

    def __init__(self, session_maker, file_storage: FileStorage, trace_analyzer: TraceAnalyzer, trace_normalizer: TraceNormalizer):
        self._session_maker = session_maker
        self._file_storage = file_storage
        self._trace_analyzer = trace_analyzer
        self._trace_normalizer = trace_normalizer

    @property
    def _session(self):
        return self._session_maker()

    def create_annotated_unit(self, name, description, ip_mapping, mac_mapping, timestamp, ip_details, unit_file, labels):
        """
        New annotated unit will be crated, normalized and saved into database

        :param name: Name of annotated unit
        :param description: Description of annotated unit
        :param ip_mapping:
        :param mac_mapping:
        :param timestamp:
        :param ip_details:
        :param unit_file:
        :param labels: Annotated unit labels
        :return: new annotated unit
        """
        new_ann_unit_file = File.create_new()

        configuration = self._trace_normalizer.prepare_configuration(ip_mapping, mac_mapping, timestamp)
        self._trace_normalizer.normalize(unit_file.location, new_ann_unit_file.location, configuration)

        analyzed_data = self._trace_analyzer.analyze(new_ann_unit_file.location)

        with open(new_ann_unit_file.location, "rb") as f:
            ann_unit_file_name = self._file_storage.save_file(f)

        annotated_unit = ModelAnnotatedUnit(
            name=name,
            description=description,
            creation_time=datetime.now(),
            stats=json.dumps(analyzed_data),
            ip_details=json.dumps(ip_details.dict()),
            file_location=ann_unit_file_name,
            labels=[ModelAnnotatedUnitLabel(label=l) for l in labels]
        )

        self._session.add(annotated_unit)
        return annotated_unit

    def get_annotated_unit(self, id_annotated_unit):
        """
        Get annotated unit by uid_id from database

        :param id_annotated_unit:
        :return: annotated unit
        """
        ann_unit = self._session.query(ModelAnnotatedUnit).filter(ModelAnnotatedUnit.id_annotated_unit == id_annotated_unit).first()
        return ann_unit

    def download_annotated_unit(self, id_annotated_unit):
        """
        Return absolute file location of annotated unit

        :param id_annotated_unit:
        :return: File
        """
        ann_unit = self.get_annotated_unit(id_annotated_unit)
        if not ann_unit:
            raise AnnotatedUnitDoesntExistsException()

        return self._file_storage.get_file(ann_unit.file_location)

    def get_annotated_units(self, limit=100, page=0, name=None, labels=None, description=None, operator=OperatorEnum.AND):
        """
        Find annotated units

        :param limit: number of annotated units returned in one request, default 100
        :param page: page id, starting from 0
        :param name: search annotated units by name - exact match
        :param labels: search annotated units by labels
        :param description: search mix by description
        :param operator: OperatorEnum
        :return: list of annotated units that match given criteria
        """
        q = self._session.query(ModelAnnotatedUnit)

        filters = []

        if name:
            filters.append(ModelAnnotatedUnit.name.like("%{}%".format(name)))

        if description:
            filters.append(ModelAnnotatedUnit.description.like("%{}%".format(description)))

        if labels:
            for label in labels:
                sub_q = self._session.query(ModelAnnotatedUnit).filter(ModelAnnotatedUnitLabel.label == label).filter(
                    ModelAnnotatedUnitLabel.id_annotated_unit == ModelAnnotatedUnit.id_annotated_unit
                )
                filters.append(sub_q.exists())

        if operator is OperatorEnum.AND:
            q = q.filter(and_(*filters))
        else:
            q = q.filter(or_(*filters))

        q = q.order_by(desc(ModelAnnotatedUnit.creation_time))
        q = q.offset(page*limit).limit(limit)

        ann_units = q.all()
        return ann_units

    def delete_annotated_unit(self, id_annotated_unit):
        """
        Delete annotated unit using id

        :param id_annotated_unit: ID to be deleted
        """

        ann_unit = self.get_annotated_unit(id_annotated_unit)
        if not ann_unit:
            raise AnnotatedUnitDoesntExistsException()

        try:
            self._session.delete(ann_unit)
            self._session.commit()
        except sqlalchemy.exc.IntegrityError as ex:
            raise UnableToRemoveAnnotatedUnitException() from ex
