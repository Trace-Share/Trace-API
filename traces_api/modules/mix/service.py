import json
from datetime import datetime
from sqlalchemy import desc

from traces_api.database.model.mix import ModelMix, ModelMixLabel

from traces_api.tools import TraceAnalyzer, TraceNormalizer
from traces_api.storage import FileStorage, File


class MixService:
    """
    This class allows to perform all business logic regarding to mixes
    """

    def __init__(self, session, file_storage: FileStorage, trace_analyzer: TraceAnalyzer, trace_normalizer: TraceNormalizer):
        self._session = session
        self._file_storage = file_storage
        self._trace_analyzer = trace_analyzer
        self._trace_normalizer = trace_normalizer

    def crete_mix(self, name, description, ip_mapping, mac_mapping, timestamp, ip_details, unit_file_location, labels):
        random_file_name = "/tmp/TMP_TEST_FILE_NAME"
        with open(random_file_name, "w"):
            pass

        configuration = self._trace_normalizer.prepare_configuration(ip_mapping, mac_mapping, timestamp)
        self._trace_normalizer.normalize(unit_file_location, random_file_name, configuration)

        new = File(random_file_name)
        file_location = self._file_storage.save_file2(new)

        analyzed_data = self._trace_analyzer.analyze(new.location)

        annotated_unit = ModelMix(
            name=name,
            description=description,
            creation_time=datetime.now(),
            stats=json.dumps(analyzed_data),
            ip_details=json.dumps(ip_details.dict()),
            file_location=file_location,
            labels=[ModelMixLabel(label=l) for l in labels]
        )

        self._session.add(annotated_unit)
        return annotated_unit

    def get_mix(self, id_mix):
        """
        Get mix by id_mix from database

        :param id_mix:
        :return: mix
        """
        mix = self._session.query(ModelMix).filter(ModelMix.id_mix == id_mix).first()
        return mix

    def download_annotated_unit(self, id_mix):
        """
        Return absolute file location of mix

        :param id_mix:
        :return: absolute path
        """
        mix = self.get_mix(id_mix)

        # return self._file_storage.get_absolute_file_path(ann_unit.file_location)

    def get_mixes(self, limit=100, page=0, name=None, labels=None, description=None):
        """
        Get all mixes

        :return: list of annotated units
        """
        q = self._session.query(ModelMix)

        if name:
            q = q.filter(ModelMix.name.like("%{}%".format(name)))

        if description:
            q = q.filter(ModelMix.description.like("%{}%".format(description)))

        if labels:
            q = q.outerjoin(ModelMixLabel)
            for label in labels:
                q = q.filter(ModelMixLabel.label == label)

        q = q.order_by(desc(ModelMix.creation_time))
        q = q.offset(page*limit).limit(limit)

        ann_units = q.all()
        return ann_units
