'''
Script used to extract decay fields by reading MCDecayTree.py, it uses as input Renato -> DecFiles naming dictionary
'''
import re
from typing import Union

import yaml
from dmu.logging.log_store import LogStore

log=LogStore.add_logger('test_mctree')
# ----------------------------
class Data:
    mode_regex   : str = r'\s+modename\s*=\s*(".*")\s*'
    fields_regex : str = r'\s*FIELDS\s*=\s*{\s*'
    decay_regex  : str = r'\s*"(.*)"\s*:\s*"(.*).*",?'

    d_mode_nick  : dict[str,str]
# ----------------------------
def _get_lines() -> list[str]:
    with open('MCDecayTree.py', encoding='utf-8') as ifile:
        text = ifile.read()

    return text.splitlines()
# ----------------------------
def _get_mode(line : str) -> Union[None,str]:
    mtch = re.match(Data.mode_regex, line)
    if not mtch:
        return None

    mode = mtch.group(1)
    mode = mode.replace('"', '')

    # Needed for lines like:
    # 'Bd_KPi if mode == ':
    if ' ' in mode:
        l_mode = mode.split(' ')
        mode   = l_mode[0]

    return mode
# ----------------------------
def _is_fieldsline(line : str) -> bool:
    mtch = re.match(Data.fields_regex, line)
    if not mtch:
        return False

    return True
# ----------------------------
def _extract_head_decay(line : str) -> Union[None,tuple[str,str]]:
    mtch = re.match(Data.decay_regex, line)

    if not mtch:
        return None

    head  = mtch.group(1)
    decay = mtch.group(2)

    decay = decay.replace(' ', 'space')
    decay = decay.replace('space', ' ')

    return head, decay
# ----------------------------
def _nick_name_from_mode(mode : str) -> str:
    if mode not in Data.d_mode_nick:
        log.warning(f'Cannot find decay {mode}')
        return mode

    return Data.d_mode_nick[mode]
# ----------------------------
def _get_groups(l_line : list[str]) -> dict[str,dict[str,str]]:
    save = False

    d_group : dict[str,dict[str,str]] = {}
    this_mode = 'no_mode'
    for line in l_line:
        mode_name = _get_mode(line)
        if mode_name is not None:
            this_mode = mode_name
            d_group[this_mode] = {}

        save = save or _is_fieldsline(line)
        if save and 'FIELDS' not in line:
            val = _extract_head_decay(line)
            if val is None:
                continue

            head, decay = val
            head = head.ljust(15)
            d_group[this_mode][head] = decay

        if save and '}' in line:
            save = False

    d_group_trimm = { _nick_name_from_mode(mode) : d_decay for mode, d_decay in d_group.items() if len(d_decay) > 0 }

    return d_group_trimm
# ----------------------------
def _format_line(line : str) -> str:
    nquote = line.count('\'')
    if nquote != 4:
        return line

    line = line.replace('\'', '', 2)

    return line
# ----------------------------
def _post_process(path : str) -> None:
    with open(path, encoding='utf-8') as ifile:
        l_line = ifile.read().splitlines()

    l_line_form = [ _format_line(line) for line in l_line ]

    form_path = path.replace('.yaml', '_form.yaml')
    with open(form_path, 'w', encoding='utf-8') as ofile:
        text = '\n'.join(l_line_form)
        ofile.write(text)
# ----------------------------
def _load_nicknames() -> None:
    with open('nickname.yaml', encoding='utf-8') as ifile:
        Data.d_mode_nick = yaml.safe_load(ifile)
# ----------------------------
def main():
    '''
    Script starts here
    '''
    _load_nicknames()

    l_line = _get_lines()
    d_group= _get_groups(l_line)

    with open('decays.yaml', 'w', encoding='utf-8') as ofile:
        yaml.safe_dump(d_group, ofile, width=200)

    _post_process('decays.yaml')
# ----------------------------
if __name__ == '__main__':
    main()