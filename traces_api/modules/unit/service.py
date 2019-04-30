import json

from datetime import datetime
from sqlalchemy import desc

from traces_api.database.model.unit import ModelUnit
from traces_api.modules.annotated_unit.service import AnnotatedUnitService
from traces_api.trace_tools import TraceAnalyzer
from traces_api.storage import FileStorage
from traces_api.tools import escape


class UnitDoesntExistsException(Exception):
    """
    Unit doesnt exits
    This exception is raised when annotated unit is not found in database
    """
    pass


class InvalidUnitStageException(Exception):
    """
    Unit is not not stage it should be use another method
    """
    pass


class IPDetailsUnknownIPException(Exception):
    """
    This exception is raised when IP in IPDetails object does not exists in mapping IPs.
    """
    def __init__(self, ip):
        self.ip = ip


class Mapping:
    """
    Class that holds information about mapping
    """

    def __init__(self):
        self._data = []

    def add_pair(self, original, replacement):
        """
        Add new pair to mapping table

        :param original: Current value that will be replaced
        :param replacement: New value
        """
        self._data.append((original, replacement))

    @property
    def data(self):
        """
        Access saved pairs

        :return: list that contains tuples (ORIGINAL_VALUE, NEW_VALUE)
        """
        return self._data

    @staticmethod
    def create_from_dict(data_dict):
        """
        Create new mapping object from dictionary
        :param data_dict:
        :return: Mapping
        """
        mapping = Mapping()
        for d in data_dict:
            mapping.add_pair(d["original"], d["replacement"])
        return mapping


class IPDetails:
    """
    Class that separate ips into 3 groups

    Groups:
    - Target nodes
    - Intermediate nodes
    - Source nodes
    """

    def __init__(self, target_nodes, intermediate_nodes, source_nodes):
        """
        :param target_nodes: list ips
        :param intermediate_nodes: list ips
        :param source_nodes: list ips
        """
        self.target_nodes = target_nodes
        self.intermediate_nodes = intermediate_nodes
        self.source_nodes = source_nodes

    def dict(self):
        """
        Convert class to dict
        :return: dict
        """
        return dict(
            target_nodes=self.target_nodes,
            intermediate_nodes=self.intermediate_nodes,
            source_nodes=self.source_nodes,
        )


class UnitServiceAbstract:
    """
    This class allows to create unit and transform it into annotated unit.
    """

    def unit_upload(self, file):
        """
        Create unit step 1

        In this step uploaded unit is saved.
        This method returns analyzed data from uploaded unit and unit_id.

        :param file: Uploaded file
        :return: tuple - unit, analyzed data
        """
        raise NotImplementedError()

    def unit_annotate(self, id_unit, name, description=None, labels=None):
        """
        Create unit step 2

        This method allows user to provide additional information to unit
        Add name, description, labels to unit.

        :param id_unit: ID of existing unit
        :param name: Name of unit
        :param description: Description of unit
        :param labels: list of labels
        :return: unit
        """

        raise NotImplementedError()

    def unit_normalize(self, id_unit, ip_mapping, mac_mapping, ip_details, timestamp):
        """
        Create unit step 3

        Final step when processing unit.
        Workflow:
        - unit is normalised using ip, mac mappings
        - all timestamps in unit are reset to epoch time
        - new annotated unit is created based on unit

        :param id_unit: ID of existing unit
        :param ip_mapping: list that contains dicts {"original": ORIGINAL_IP, "replacement": REPLACEMENT_IP}
        :param mac_mapping: list that contains dicts {"original": ORIGINAL_MAC, "replacement": REPLACEMENT_MAC}
        :param ip_details:
        :param timestamp: base timestamp
        :return: annotated_unit
        """

        raise NotImplementedError()

    def unit_delete(self, id_unit):
        """
        Delete unit with given id

        :param id_unit: ID of existing unit
        """

        raise NotImplementedError()

    def get_units(self, limit=100, page=0):
        """
        Find units

        :param limit: number of mixes returned in one request, default 100
        :param page: page id, starting from 0
        :return: list of units
        """
        raise NotImplementedError()


class UnitService(UnitServiceAbstract):

    def __init__(self, session_maker, annotated_unit_service: AnnotatedUnitService, file_storage: FileStorage, trace_analyzer: TraceAnalyzer):
        """
        :param session_maker: SqlAlchemy session maker
        :param annotated_unit_service: AnnotatedUnitService
        :param file_storage: file storage for storing datasets
        :param trace_analyzer: trace analyzer is used to extract analytical data from dataset
        """
        self._session_maker = session_maker
        self._annotated_unit_service = annotated_unit_service
        self._trace_analyzer = trace_analyzer
        self._file_storage = file_storage

    @property
    def _session(self):
        return self._session_maker()

    def _get_unit(self, id_unit) -> ModelUnit:
        """
        Take unit from database using id_unit

        :param id_unit: ID of existing unit
        :return: unit
        """
        unit = self._session.query(ModelUnit).filter(ModelUnit.id_unit == id_unit).first()
        return unit

    def unit_upload(self, file):
        if file.filename.endswith(".pcapng"):
            format = "pcapng"
        else:
            format = "pcap"

        file_path = self._file_storage.save_file(file.stream, format)

        unit = ModelUnit(
            creation_time=datetime.now(),
            last_update_time=datetime.now(),
            uploaded_file_location=file_path,
            stage="upload"
        )

        self._session.add(unit)
        self._session.commit()
        return unit, escape(self._trace_analyzer.analyze(self._file_storage.get_file(file_path).location))

    def unit_annotate(self, id_unit, name, description=None, labels=None):
        unit = self._get_unit(id_unit)
        if not unit:
            raise UnitDoesntExistsException()

        if unit.stage != "upload":
            raise InvalidUnitStageException()

        annotation = dict(name=name, description=description, labels=labels)
        unit.annotation = json.dumps(annotation)
        unit.stage = "annotate"

        self._session.add(unit)
        self._session.commit()
        return unit

    def unit_normalize(self, id_unit, ip_mapping, mac_mapping, ip_details, timestamp):
        unit = self._get_unit(id_unit)
        if not unit:
            raise UnitDoesntExistsException()

        if unit.stage != "annotate":
            raise InvalidUnitStageException()

        unit_annotation = json.loads(unit.annotation)

        self._validate_ip_details(ip_details, ip_mapping)

        annotated_unit = self._annotated_unit_service.create_annotated_unit(
            name=unit_annotation["name"],
            description=unit_annotation["description"],
            ip_mapping=ip_mapping,
            mac_mapping=mac_mapping,
            timestamp=timestamp,
            ip_details=ip_details,
            unit_file=self._file_storage.get_file(unit.uploaded_file_location),
            labels=unit_annotation["labels"]
        )

        unit_file_location = unit.uploaded_file_location
        self._session.delete(unit)
        self._session.commit()

        self._file_storage.remove_file(unit_file_location)

        return annotated_unit

    @staticmethod
    def _validate_ip_details(ip_details, ip_mapping):
        """
        Validate IP details
        IPs in IP details should exists in replacement IPs in ip_mapping object.
        :param ip_details: IPDetails
        :param ip_mapping: Mapping
        """
        new_ips = [ip[1] for ip in ip_mapping.data]

        for ip in ip_details.target_nodes:
            if ip not in new_ips:
                raise IPDetailsUnknownIPException(ip)

        for ip in ip_details.intermediate_nodes:
            if ip not in new_ips:
                raise IPDetailsUnknownIPException(ip)

        for ip in ip_details.source_nodes:
            if ip not in new_ips:
                raise IPDetailsUnknownIPException(ip)

    def unit_delete(self, id_unit):
        unit = self._get_unit(id_unit)
        if not unit:
            raise UnitDoesntExistsException()

        unit_file_location = unit.uploaded_file_location
        self._session.delete(unit)
        self._session.commit()

        self._file_storage.remove_file(unit_file_location)

    def get_units(self, limit=100, page=0):
        q = self._session.query(ModelUnit)

        q = q.order_by(desc(ModelUnit.creation_time))
        q = q.offset(page*limit).limit(limit)

        units = q.all()
        return units
