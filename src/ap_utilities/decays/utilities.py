'''
Module containing utility functions
'''
from importlib.resources import files

import yaml

# ---------------------------------
class Data:
    '''
    Class storing attributes shared
    '''

    d_form_long : dict[str,str]
    d_form_short: dict[str,str]

    is_initialized = False
# ---------------------------------
def _initialize():
    if Data.is_initialized:
        return

    d_form_short                        = {}
    d_form_short[                  '.'] =      'p'
    d_form_short[                  '-'] =     'mn'
    d_form_short[                  '+'] =     'pl'
    d_form_short[                  '='] =   '_eq_'
    d_form_short[                  ','] =      '_'
    d_form_short['GeV'                ] =      'G'

    d_form_long                         = {}
    d_form_long [         'DecProdCut'] =    'DPC'
    d_form_long [ 'EvtGenDecayWithCut'] =  'EGDWC'
    d_form_long ['VisibleInAcceptance'] =    'VIA'
    d_form_long [        'HighVisMass'] =    'HVM'
    d_form_long [       'OppositeSign'] =     'OS'
    d_form_long [           'TightCut'] =     'TC'
    d_form_long ['DiMuon_OppositeSign'] = 'DiM_OS'

    Data.d_form_long = d_form_long
    Data.d_form_short= d_form_short

    Data.is_initialized = True
# ---------------------------------
def _apply_format(d_format : dict[str,str], name : str) -> str:
    for org, new in d_format.items():
        name = name.replace(org, new)

    return name
# ---------------------------------
def _load_data(file_name : str) -> dict:
    file_path = files('ap_utilities_data').joinpath(file_name)
    file_path = str(file_path)
    with open(file_path, encoding='utf-8') as ifile:
        d_data = yaml.safe_load(ifile)

    return d_data
# ---------------------------------
def format_nickname(nickname : str, style : str) -> str:
    '''
    Function taking decays nickname and returning formatted version

    nickaname: Name to be formatted
    style    : How to format name, supported: literal, safe_1
    '''
    _initialize()

    if style == 'literal':
        return nickname

    if style != 'safe_1':
        raise ValueError(f'Invalid style: {style}')

    nickname = _apply_format(Data.d_form_long , nickname)
    nickname = _apply_format(Data.d_form_short, nickname)

    return nickname
# ---------------------------------
def read_decay_name(event_type : str, style : str = 'safe_1') -> str:
    '''
    Takes event type, and style strings, returns nickname of decay as defined in DecFiles package

    Styles:

    literal         : No change is made to nickname
    safe_1 (default): With following replacements:
        . -> p
        = -> _eq_
        - -> mn
        + -> pl
        , -> _
    '''
    _initialize()

    d_evt_name = _load_data('evt_name.yaml')

    if event_type not in d_evt_name:
        raise ValueError(f'Event type {event_type} not found')

    value = d_evt_name[event_type]
    value = format_nickname(value, style)

    return value
# ---------------------------------
def read_event_type(nickname : str) -> str:
    '''
    Takes nickname after reformatting, i.e. replacement of commans, equals, etc.
    Returns corresponding event type 
    '''
    _initialize()

    d_name_evt = _load_data('name_evt.yaml')

    if nickname not in d_name_evt:
        raise ValueError(f'Event type {nickname} not found')

    value = d_name_evt[nickname]

    return value
# ---------------------------------
def new_from_old_nick(nickname : str, style : str = 'safe_1') -> str:
    '''
    Function that takes a decay nick name using Run1/2 naming
    and returns nicknames using Run3 naming
    '''
    _initialize()

    d_old_evt = _load_data('old_name_evt.yaml')
    if nickname not in d_old_evt:
        raise ValueError(f'Old nickname {nickname} not found in: old_name_evt.yaml')

    evt_type   = d_old_evt[nickname]

    d_evt_name = _load_data('evt_name.yaml')
    if evt_type not in d_evt_name:
        raise ValueError(f'Event type {evt_type} not found in: evt_name.yaml')

    new_nick   = d_evt_name[evt_type]
    new_nick   = format_nickname(new_nick, style)

    return new_nick
# ---------------------------------
def old_from_new_nick(nickname : str) -> str:
    '''
    Function that takes a decay nick name using Run3 naming with safe_1 style
    and returns nicknames using Run1/2 naming
    '''
    _initialize()

    d_name_evt = _load_data('name_evt.yaml')
    if nickname not in d_name_evt:
        raise ValueError(f'Nickname {nickname} not found in: name_evt.yaml')

    evt_type   = d_name_evt[nickname]

    d_evt_old  = _load_data('evt_old_name.yaml')
    if evt_type not in d_evt_old:
        raise ValueError(f'Event type {evt_type} not found in: evt_old_name.yaml')

    old_nick   = d_evt_old[evt_type]

    return old_nick
# ---------------------------------
def name_from_lower_case(lower_case : str) -> str:
    '''
    Using new naming, but all lower case, will return
    original naming. Needed to deal with way AP names samples.
    '''
    _initialize()

    d_data = _load_data('lower_original.yaml')

    if   lower_case.endswith('_spr'):
        lower_case = lower_case[:-4]
        name = d_data[lower_case]
    elif lower_case.endswith('_ss'):
        lower_case = lower_case[:-3]
        name = d_data[lower_case]
        name = f'{name}_SS'
    elif lower_case not in d_data:
        raise ValueError(f'Sample {lower_case} not found in: lower_original.yaml')
    else:
        name = d_data[lower_case]

    return name
# ---------------------------------
