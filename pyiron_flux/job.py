from pyiron_base import HasHDF, HasStorage, GenericJob
from pyiron_atomistics import Atoms
from pyiron_contrib import Project

import contextlib
from typing import Optional, Callable

class VaspFactory(HasStorage):

    def __init__(self):
        super().__init__()

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value):
        self._project = value

    @property
    def hamilton(self):
        return "Vasp"

    def set_encut(*args, **kwargs):
        self.storage.encut_args = args
        self.storage.encut_kwargs = kwargs

    def _prepare_job(self, job, structure):
        job.set_encut(
                *self.storage.get('encut_args', ()),
                **self.storage.get('encut_kwargs', {})
        )
        job.set_kpoints(
                *self.storage.get('kpoints_args', ()),
                **self.storage.get('kpoints_kwargs', {})
        )
        return job

    def run(self,
            name: str, modify: Callable[[GenericJob], GenericJob],
            structure: Atoms,
            delete_existing_job=False, delete_aborted_job=True
    ) -> Optional[GenericJob]:

        # short circuit if job already successfully ran
        if name in self.project.list_nodes() \
                and self.project.get_job_status(name) == 'finished':
            return None

        job = self.project.create.job.Vasp(
                name,
                delete_existing_job=delete_existing_job,
                delete_aborted_job=delete_aborted_job
        )
        if not job.status.initialized: return job

        job = self._prepare_job(job, structure)
        job = modify(job)

        with open('/dev/null', 'w') as f, contextlib.redirect_stdout(f):
            job.run()
        return job

class MlipFactory(HasHDF):

    def __init__(self, project=None):
        self._project = project
        self._potential = None

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value):
        self._project = value

    @property
    def potential(self):
        return self._potential

    @potential.setter
    def potential(self, value):
        self._potential = value

    @property
    def hamilton(self):
        return "LammpsMlip"

    def _prepare_job(self, job, structure):
        job.structure = structure
        job.potential = self.potential
        return job

    def run(self,
            name: str, modify: Callable[[GenericJob], GenericJob],
            structure: Atoms,
            delete_existing_job=False, delete_aborted_job=True
    ) -> Optional[GenericJob]:

        # short circuit if job already successfully ran
        if name in self.project.list_nodes() \
                and self.project.get_job_status(name) == 'finished':
            return None

        job = self.project.create.job.LammpsMlip(
                name,
                delete_existing_job=delete_existing_job,
                delete_aborted_job=delete_aborted_job
        )
        if not job.status.initialized: return job

        job = self._prepare_job(job, structure)
        job = modify(job)

        with open('/dev/null', 'w') as f, contextlib.redirect_stdout(f):
            job.run()
        return job

    def _to_hdf(self, hdf):
        hdf['potential'] = self.potential

    def _from_hdf(self, hdf, version=None):
        self.potential = hdf['potential']
