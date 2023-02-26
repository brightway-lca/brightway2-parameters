from .pint import PintWrapper
from warnings import warn


class Config:

    _use_pint = False

    @classmethod
    def warn_if_no_pint(cls):
        if not PintWrapper.pint_installed:
            warn(
                "Could not initialize pint. Reverting to default interpreter. Using units in formulas may lead to "
                "errors and/or unexpected results. To suppress this warning, set "
                "`bw2data.config.use_pint_parameters = False`."
            )

    @property
    def use_pint(self):
        return self._use_pint

    @use_pint.setter
    def use_pint(self, value):
        if value is True:
            self.warn_if_no_pint()
        self._use_pint = value


config = Config()
