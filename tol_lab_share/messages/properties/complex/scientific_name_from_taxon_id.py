from tol_lab_share.messages.properties import MessageProperty
from requests import get, codes
from functools import cached_property, lru_cache
from tol_lab_share.helpers import get_config
from tol_lab_share import error_codes
from typing import Any, cast
from typing import Callable


class StatusCodeException(Exception):
    def __init__(self, status_code: int):
        super().__init__(status_code)
        self.status_code = status_code


@lru_cache(maxsize=1000)
def get_taxon_id_from_ebi(base_url: str, taxon_id: str) -> Any:
    r = get(f"{base_url}/{taxon_id}")
    if r.status_code != codes.ok:
        raise StatusCodeException(r.status_code)
    return r.json()["scientificName"]


class ScientificNameFromTaxonId(MessageProperty):
    """MessageProperty subclass to manage resolving the scientific name that
    represents the taxon id received as input.
    """

    @property
    def validators(self) -> list[Callable]:
        """Checks the input is a string"""
        return [self.string_checker()]

    @cached_property
    def taxonomy_url(self) -> str:
        """URL with the reference to the EBI taxonomy service that resolves
        taxon ids into scientific names."""
        return cast(str, get_config("").EBI_TAXONOMY_URL)

    @cached_property
    def value(self) -> Any:
        """Resolves the value of the scientific name by querying the EBI service
        for the value given to the taxon id stored in current instance. It also
        caches the value so it can be reused by other objects.
        """
        try:
            return get_taxon_id_from_ebi(self.taxonomy_url, self._input.value)
        except StatusCodeException as e:
            self.trigger_error(
                error_codes.ERROR_14_PROBLEM_ACCESSING_TAXON_ID,
                text=f"HTTP code {e.status_code} - Problem when accessing taxon id {self._input.value}",
            )
            return None

    @staticmethod
    def reset_cache():
        """Static method to reset the cache shared by all instances"""
        get_taxon_id_from_ebi.cache_clear()
