import json

from datetime import datetime
from sqlalchemy import desc, update

from traces_api.database.model.mix import ModelMix, ModelMixLabel, ModelMixOrigin, ModelMixFileGeneration

from traces_api.modules.annotated_unit.service import AnnotatedUnitService
from traces_api.tools import TraceNormalizer, TraceMixing
from traces_api.storage import FileStorage, File


class AnnotatedUnitDoesntExistsException(Exception):
    pass


class MixDoesntExistsException(Exception):
    pass


class MixService:
    """
    This class allows to perform all business logic regarding to mixes
    """

    def __init__(self, session, annotated_unit_service: AnnotatedUnitService, file_storage: FileStorage, trace_normalizer: TraceNormalizer, trace_mixing: TraceMixing):
        self._session = session
        self._annotated_unit_service = annotated_unit_service
        self._file_storage = file_storage
        self._trace_normalizer = trace_normalizer
        self._trace_mixing = trace_mixing

    def _exits_ann_unit(self, id_annotated_unit):
        return self._annotated_unit_service.get_annotated_unit(id_annotated_unit) is not None

    def _mix(self, mix_generation_id, annotated_units_data):
        if not (all([self._exits_ann_unit(ann_unit["id_annotated_unit"]) for ann_unit in annotated_units_data])):
            raise AnnotatedUnitDoesntExistsException()

        self._update_mix_generation_progress(mix_generation_id, 1)
        mixing = self._trace_mixing.create_new_mixer(File.create_new().location)

        for ann_unit in annotated_units_data:
            id_annotated_unit = ann_unit["id_annotated_unit"]

            new_ann_unit_file = File.create_new()
            ann_unit_location = self._annotated_unit_service.download_annotated_unit(id_annotated_unit)
            configuration = self._trace_normalizer.prepare_configuration(ann_unit["ip_mapping"], ann_unit["mac_mapping"], ann_unit["timestamp"])
            self._trace_normalizer.normalize(ann_unit_location, new_ann_unit_file.location, configuration)

            mixing.mix(new_ann_unit_file.location)

        self._update_mix_generation_progress(mix_generation_id, 99)

        mix_file = File(mixing.get_mixed_file_location())
        file_name = self._file_storage.save_file2(mix_file)

        mix_generation = self.get_mix_generation_by_id_generation(mix_generation_id)
        mix_generation.progress = 100
        mix_generation.file_location = file_name

        self._session.add(mix_generation)
        self._session.commit()

    def create_mix(self, name, description, labels, annotated_units):
        if not (all([self._exits_ann_unit(ann_unit["id_annotated_unit"]) for ann_unit in annotated_units])):
            raise AnnotatedUnitDoesntExistsException()

        mix = ModelMix(
            name=name,
            description=description,
            creation_time=datetime.now(),
            labels=[ModelMixLabel(label=l) for l in labels],
            origins=[
                ModelMixOrigin(
                    id_annotated_unit=ann_unit["id_annotated_unit"],
                    ip_mapping=json.dumps(ann_unit["ip_mapping"]),
                    mac_mapping=json.dumps(ann_unit["mac_mapping"]),
                    timestamp=ann_unit["timestamp"],
                ) for ann_unit in annotated_units
            ],
        )

        self._session.add(mix)
        self._session.commit()
        return mix

    def generate_mix(self, id_mix):
        mix = self.get_mix(id_mix)
        if not mix:
            raise MixDoesntExistsException(id_mix)

        annotated_units_data = []
        for origin in mix.origins:
            annotated_units_data.append(dict(
                id_annotated_unit=origin.id_annotated_unit,
                ip_mapping=json.loads(origin.ip_mapping),
                mac_mapping=json.loads(origin.mac_mapping),
                timestamp=origin.timestamp,
            ))

        mix_generation = ModelMixFileGeneration(
            id_mix=mix.id_mix,
            creation_time=datetime.now(),
            expired=False,
            progress=0,
        )
        self._session.add(mix_generation)
        self._session.commit()

        self._mix(mix_generation.id_mix_generation, annotated_units_data)

        return mix_generation

    def get_mix(self, id_mix):
        """
        Get mix by id_mix from database

        :param id_mix:
        :return: mix
        """
        mix = self._session.query(ModelMix).filter(ModelMix.id_mix == id_mix).first()
        if not mix:
            raise MixDoesntExistsException()
        return mix

    def get_mix_generation(self, id_mix):
        q = self._session.query(ModelMixFileGeneration).filter_by(expired=False).filter_by(id_mix=id_mix)
        q = q.order_by(desc(ModelMixFileGeneration.creation_time))
        mix_generation = q.first()
        return mix_generation

    def get_mix_generation_by_id_generation(self, id_mix_generation):
        q = self._session.query(ModelMixFileGeneration).filter_by(id_mix_generation=id_mix_generation)
        mix_generation = q.first()
        return mix_generation

    def _update_mix_generation_progress(self, id_mix_generation, progress):
        q = update(ModelMixFileGeneration).values(progress=progress)\
            .where(ModelMixFileGeneration.id_mix_generation == id_mix_generation)
        self._session.execute(q)
        self._session.commit()

    def download_mix(self, id_mix):
        """
        Return absolute file location of mix

        :param id_mix:
        :return: absolute path
        """
        mix_generation = self.get_mix_generation(id_mix)
        return self._file_storage.get_absolute_file_path(mix_generation.file_location)

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
