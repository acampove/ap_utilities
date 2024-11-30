'''
Script used to build decay fields from YAML file storing event type -> decay correspondence
'''
import re
import argparse
from typing                         import Union
from importlib.resources            import files

import yaml
import ap_utilities.decays.utilities as aput
from ap_utilities.logging.log_store import LogStore

log = LogStore.add_logger('ap_utilities:make_fields')
# ---------------------------
class Data:
    '''
    Class storing shared data
    '''
    l_skip_type= [
            '12952000',
            '11453001',
            '13454001',
            '15454101',
            '12442001',
            '11442001',
            '13442001',
            '15444001',
            '15442001',
            '12873002',
            ]

    d_repl_sym = {
            'cc'        :      'CC',
            '->'        :     '==>',
            }

    d_repl_par = {
            'psi(2S)'    :   'psi_2S_',
            'psi(1S)'    :   'psi_1S_',
            'K*(892)'    :   'K*_892_',
            'phi(1020)'  : 'phi_1020_',
            'K_1(1270)'  : 'K_1_1270_',
            'K_2*(1430)' : 'K_2*_1430_',
            }

    d_repl_spa = {
            '('        :     ' ( ',
            ')'        :     ' ) ',
            '['        :     ' [ ',
            ']'        :     ' ] ',
            }

    l_event_type : list[str]
    d_decay      : dict[str,str]

    d_nicknames = {
            'pi0' : 'pi0',
            'pi+' : 'pip',
            'pi-' : 'pim',
            'X'   : 'X',

            'K+'  : 'Kp',
            'K-'  : 'Km',

            'e+'  : 'Ep',
            'e-'  : 'Em',

            'mu+' : 'Mp',
            'mu-' : 'Mm',

            'tau+': 'taup',
            'tau-': 'taum',

            'p+'  : 'Pp',
            'p~-' : 'Pm',
            'K_S0': 'KS',

            'D-'    : 'D',
            'D0'    : 'D',
            'D_s-'  : 'D',
            'D_s*-' : 'D',
            'D~0'   : 'D',
            'nu_tau': 'nu',
            'nu_mu' : 'nu',
            'nu_e'  : 'nu',

            'B+'  : 'Bu',
            'B-'  : 'Bu',
            'B0'  : 'Bd',
            'X0'  :  'X',
            'B_s0': 'Bs',
            'phi' : 'phi',
            'eta' : 'eta',

            'K_2*(1430)+'    : 'K2',
            'Beauty'         : 'B',
            'K_1+'           : 'K1',
            'K_1(1270)0'     : 'K1',
            'K_1(1270)+'     : 'K1',
            'phi(1020)'      : 'phi',
            'gamma'          : 'gm',
            'K*(892)0'       : 'Kst',
            'K*(892)+'       : 'Kstp',
            'J/psi(1S)'      : 'Jpsi',
            'psi(2S)'        : 'psi2S',
            'Lambda_b0'      : 'Lb',
            'Lambda_c-'      : 'Lc',
            'Lambda0'        : 'Lz',
            'Lambda~0'       : 'Lz',
            'anti-Lambda_c-' : 'Lc',
            }
# ---------------------------
def _load_decays() -> None:
    dec_path = files('ap_utilities_data').joinpath('evt_dec.yaml')
    dec_path = str(dec_path)
    with open(dec_path, encoding='utf-8') as ifile:
        Data.d_decay = yaml.safe_load(ifile)
# ---------------------------
def _parse_args() -> None:
    parser = argparse.ArgumentParser(description='Used to perform several operations on TCKs')
    parser.add_argument('-i', '--input' , type=str, help='Path to textfile with event types')
    args = parser.parse_args()

    input_path = args.input
    with open(input_path, encoding='utf-8') as ifile:
        Data.l_event_type = ifile.read().splitlines()
# ---------------------------
def _reformat_decay(decay : str) -> str:
    # Symbol renaming needed, e.g. -> ==>, cc -> CC
    for org, new in Data.d_repl_sym.items():
        decay = decay.replace(org, new)

    # Need to make special substrings into underscored ones
    # e.g. J/psi(1S) -> J/psi_1S_
    for org, new in Data.d_repl_par.items():
        decay = decay.replace(org, new)

    # Add spaces to parentheses and brackets
    for org, new in Data.d_repl_spa.items():
        decay = decay.replace(org, new)

    return decay
# ---------------------------
def _reformat_back_decay(decay : str) -> str:
    # Put back special characters original naming
    for org, new in Data.d_repl_par.items():
        decay = decay.replace(new, org)

    # Decay cannot have space here, other spaces are allowed
    decay = decay.replace('] CC', ']CC')

    decay = decay.replace('[ '  ,   '[')
    decay = decay.replace('[  ' ,   '[')
    decay = decay.replace('  ]' ,   ']')
    decay = decay.replace('  [' ,   '[')
    decay = decay.replace(' ['  ,   '[')

    decay = decay.replace('(  ' ,   '(')
    decay = decay.replace('  )' ,   ')')

    return decay
# ---------------------------
def _replace_back(part : str) -> str:
    for org, new in Data.d_repl_par.items():
        if new in part:
            part = part.replace(new, org)

    return part
# ---------------------------
def _particles_from_decay(decay : str) -> list[str]:
    l_repl = list(Data.d_repl_sym.values())
    l_repl+= list(Data.d_repl_spa.values())
    l_repl = [ repl.replace(' ', '') for repl in l_repl ]

    l_part = decay.split(' ')
    l_part = [ part for part in l_part if part not in l_repl ]
    l_part = [ part for part in l_part if part != ''         ]
    l_part = [ _replace_back(part) for part in l_part ]

    return l_part
# ---------------------------
def _skip_decay(event_type : str, decay : str) -> bool:
    if event_type in Data.l_skip_type:
        log.debug(f'Skipping decay: {decay}')
        return True

    if '{,gamma}' in decay:
        log.warning(f'Skipping {event_type} decay: {decay}')
        return True

    if 'nos' in decay:
        log.warning(f'Skipping {event_type} decay: {decay}')
        return True

    return False
# ---------------------------
def _remove_index(particle : str) -> tuple[str,int]:
    mtch = re.match(r'(.*)_(\d+)$', particle)
    if not mtch:
        return particle, 1

    particle = mtch.group(1)
    npar     = mtch.group(2)
    npar     = int(npar)

    return particle, npar
# ---------------------------
def _get_hatted_decay( particle : str, i_par : int, decay : str) -> str:
    decay = decay.replace(' '   , '  ')
    decay = decay.replace('   ' , '  ')
    decay = decay.replace('    ', '  ')

    if i_par == 0:
        return decay

    particle, ipar = _remove_index(particle)

    decay = _replace_nth_particle(decay, particle, ipar)

    return decay
# ---------------------------
def _replace_nth_particle(decay : str, particle:str, ipar:int) -> str:
    src    = f' {particle}'
    tgt    = f'^{particle}'

    l_part = decay.split(src)
    npart  = len(l_part)
    if npart == 1:
        raise ValueError(f'Cannot find {particle} in {decay}')

    if npart == 2:
        decay = decay.replace(src, tgt)

    return src.join(l_part[:ipar]) + tgt + src.join(l_part[ipar:])
# ---------------------------
def _rename_repeated(l_par : list[str]) -> list[str]:
    d_par_freq = {}
    for par in l_par:
        if par not in d_par_freq:
            d_par_freq[par] = 1
            continue

        d_par_freq[par]+= 1

    l_par_renamed = []
    for par, freq in d_par_freq.items():
        if freq == 1:
            l_par_renamed.append(par)
        else:
            l_par_renamed += [ f'{par}_{i_par}' for i_par in range(1, freq + 1) ]

    return l_par_renamed
# ---------------------------
def _nickname_from_particle(name : str, event_type : str) -> str:
    name, ipar = _remove_index(name)
    name       = name.replace('anti-', '')

    if name not in Data.d_nicknames:
        log.warning(f'Nickname for {name} not found in {event_type}')
        return name

    nick = Data.d_nicknames[name]
    if ipar > 1:
        nick = f'{nick}_{ipar}'

    nick = nick.replace('anti-', '')

    return nick
# ---------------------------
def _replace_beauty(decay : str, event_type : str) -> str:
    if event_type == '11102453':
        bname = 'B0'
    else:
        log.warning(f'Cannot identify B meson type for {event_type}')
        bname = 'Beauty'

    decay = decay.replace('Beauty', bname)

    return decay
# ---------------------------
def _fix_names(decay : str, event_type : str) -> str:
    '''
    Decay fileld in decay files is not properly written, need to fix here, before using decay
    '''
    decay = decay.replace('K_1+', 'K_1(1270)+')
    decay = decay.replace('K*+' ,   'K*(892)+')
    decay = decay.replace('K*0' ,   'K*(892)0')
    decay = decay.replace('My_' ,           '')

    if 'Beauty' in decay:
        decay = _replace_beauty(decay, event_type)

    return decay
# ---------------------------
def _get_decay(event_type : str) -> Union[None,dict[str,str]]:
    decay = Data.d_decay[event_type]
    decay = _fix_names(decay, event_type)

    if _skip_decay(event_type, decay):
        return None

    decay = _reformat_decay(decay)
    l_par = _particles_from_decay(decay)
    l_par = _rename_repeated(l_par)
    decay = _reformat_back_decay(decay)

    d_dec = {}
    for i_par, par in enumerate(l_par):
        nickname        = _nickname_from_particle(par, event_type)
        d_dec[nickname] = _get_hatted_decay(par, i_par, decay)

    return d_dec
# ---------------------------
def _get_decays() -> dict[str, dict[str,str]]:
    d_decay = {}
    for event_type in Data.l_event_type:
        d_tmp = _get_decay(event_type)
        if d_tmp is None:
            continue

        decname = aput.read_decay_name(event_type=event_type, style= 'safe_1')
        d_decay[decname] = d_tmp

    return d_decay
# ---------------------------
def main():
    '''
    Script starts here
    '''
    _parse_args()
    _load_decays()
    d_decay = _get_decays()
    with open('decays.yaml', 'w', encoding='utf-8') as ofile:
        yaml.safe_dump(d_decay, ofile, width=80)
# ---------------------------
if __name__ == '__main__':
    main()
