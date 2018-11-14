import json

from datetime import datetime

from traces_api.database.model.unit import ModelUnit
from traces_api.modules.annotated_unit.service import AnnotatedUnitService
from traces_api.tools import TraceAnalyzer
from traces_api.storage import FileStorage


class UnitDoesntExists(Exception):
    pass


class Mapping:

    def __init__(self):
        self._data = []

    def add_pair(self, original, replacement):
        self._data = (original, replacement)

    @property
    def data(self):
        return self._data


class IPDetails:

    def __init__(self, target_nodes, intermediate_nodes, source_nodes):
        self.target_nodes = target_nodes
        self.intermediate_nodes = intermediate_nodes
        self.source_nodes = source_nodes


class UnitServiceAbstract:

    def create_unit_step1(self, file, author):
        raise NotImplementedError()

    def create_unit_step2(self, id_unit, name, description=None, labels=None):
        raise NotImplementedError()

    def create_unit_step3(self, id_unit, ip_mapping, mac_mapping, ips, timestamp):
        raise NotImplementedError()


class UnitService(UnitServiceAbstract):

    def __init__(self, session, annotated_unit_service: AnnotatedUnitService, file_storage: FileStorage, trace_analyzer: TraceAnalyzer):
        self._session = session
        self._annotated_unit_service = annotated_unit_service
        self._trace_analyzer = trace_analyzer
        self._file_storage = file_storage

    def _get_unit(self, id_unit) -> ModelUnit:
        """

        :param id_unit:
        :return:
        """
        unit = self._session.query(ModelUnit).filter(ModelUnit.id_unit == id_unit).first()
        return unit

    def _save_unit(self, unit):
        self._session.add(unit)
        return unit

    def create_unit_step1(self, file, author):
        file_path = self._file_storage.save_file(file, ["application/vnd.tcpdump.pcap"])

        unit = ModelUnit(
            creation_time=datetime.now(),
            last_update_time=datetime.now(),
            uploaded_file_location=file_path,
            id_author=author
        )

        self._save_unit(unit)
        self._session.commit()
        return unit, self._trace_analyzer.get_pcap_dump_information("storage/units/"+unit.uploaded_file_location)

    def create_unit_step2(self, id_unit, name, description=None, labels=None):
        unit = self._get_unit(id_unit)
        if not unit:
            raise UnitDoesntExists()

        annotation = dict(name=name, description=description, labels=labels)
        unit.annotation = json.dumps(annotation)

        self._save_unit(unit)
        self._session.commit()
        return unit

    def create_unit_step3(self, id_unit, ip_mapping, mac_mapping, ip_details, timestamp):
        unit = self._get_unit(id_unit)
        if not unit:
            raise UnitDoesntExists()

        unit_annotation = json.loads(unit.annotation)

        annotated_unit = self._annotated_unit_service.create_annotated_unit(
            name=unit_annotation["name"],
            description=unit_annotation["description"],
            id_author=unit.id_author,
            stats=None,  #todo
            ip_mapping=ip_mapping,
            file_location="to/do",
            labels=unit_annotation["labels"]
        )

        self._session.commit()
        return annotated_unit

