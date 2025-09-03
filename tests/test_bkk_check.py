'''
Module with tests for BkkChecker class
'''
import pytest

from ap_utilities.logging.log_store       import LogStore
from ap_utilities.bookkeeping.bkk_checker import BkkChecker
from dmu.generic                          import utilities  as gut

log = LogStore.add_logger('ap_utilities:tests:test_bkk_check')
# ----------------------------------------
@pytest.fixture(scope='session', autouse=True)
def initialize():
    '''
    This runs before any test
    '''
    LogStore.set_level('ap_utilities:Bookkeeping.bkk_checker', 10)
# ----------------------------------------
def test_simple():
    '''
    Will save list of samples to YAML
    '''
    d_cfg      = gut.load_conf(package='ap_utilities_data', fpath='tests/rd_samples.yaml')
    d_sections = d_cfg['sections']
    for name, d_section in d_sections.items():
        log.info(f'Processing section: {name}')
        obj=BkkChecker(name, d_section)
        obj.save(dry=True)
# ----------------------------------------
def test_nick_evt():
    '''
    Will test reading when there are both evt_type and nickname sections 
    '''
    d_cfg        = gut.load_conf(package='ap_utilities_data', fpath='tests/nick_evt.yaml')
    d_sections   = d_cfg['sections']
    for name, d_section in d_sections.items():
        log.info(f'Processing section: {name}')
        obj=BkkChecker(name, d_section)
        obj.save(dry=True)
# ----------------------------------------
def test_multithreaded():
    '''
    Will save list of samples to YAML using 4 threads
    '''
    d_cfg    = gut.load_conf(package='ap_utilities_data', fpath='tests/rd_samples.yaml')
    d_config = d_cfg['sections']
    for name, cfg in d_config.items():
        log.info(f'Processing section: {name}')
        obj=BkkChecker(name=name, cfg=cfg)
        obj.save(dry=True, nthreads=4)
# ----------------------------------------
