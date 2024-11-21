'''
Module with BkkChecker class
'''

import os
import yaml

from dmu.logging.log_store import LogStore

log=LogStore.add_logger('ap_utilities:Bookkeeping.bkk_checker')
# ---------------------------------
class BkkChecker:
    '''
    Class meant to check if samples exist in Bookkeeping using multithreading.
    This is useful with large lists of samples, due to low performance of Dirac
    '''
    # pylint disable=too-few-public-methods
    # -------------------------
    def __init__(self, path : str):
        '''
        Takes the path to a YAML file with the list of samples
        '''

        with open(path, encoding='utf-8') as ifile:
            self._l_sample = yaml.safe_load(ifile)
    # -------------------------
    def _was_found(self, sample : list[str]) -> bool:
        sample_id, event_type, mc_path, polarity, _, _, nu_path, _, sim_version, generator = sample

        sample_path = f'/MC/{sample_id}/Beam6800GeV-{mc_path}-{polarity}-{nu_path}-25ns-{generator}/{sim_version}/HLT2-2024.W31.34/{event_type}/DST'

        log.debug(f'{"":<4}{sample_path:<100}')

        return True
    # -------------------------
    def save(self, path : str) -> None:
        '''
        Will save list of found samples to given path
        '''

        log.info('Filtering input')
        l_sample = [ sample for sample in self._l_sample if self._was_found(sample) ]

        dir_name = os.path.dirname(path)
        os.makedirs(dir_name, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as ofile:
            yaml.safe_dump(l_sample, ofile)

        log.info(f'Saving to: {path}')
# ---------------------------------
