'''
Module with tests for BkkChecker class
'''
from importlib.resources import files

import pytest

from dmu.logging.log_store                import LogStore
from ap_utilities.bookkeeping.bkk_checker import BkkChecker

# ----------------------------------------
@pytest.fixture(scope='session', autouse=True)
def _initialize():
    LogStore.set_level('ap_utilities:Bookkeeping.bkk_checker', 20)
# ----------------------------------------
def test_simple():
    '''
    Will save list of samples to YAML
    '''
    samples_path = files('ap_utilities_data').joinpath('rd_samples.yaml')

    obj=BkkChecker(samples_path)
    obj.save(path='/tmp/ap_utilities/existing_samples.yaml')
# ----------------------------------------
