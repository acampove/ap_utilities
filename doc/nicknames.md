## Decay nicknames

### Accessing table with DecFiles sample nicknames

These nicknames can be accessed from python scripts with:

```python
import ap_utilities.decays.utilities as aput

# To get exactly what was saved
literal = aput.read_decay_name(event_type=event_type, style='literal')

# To get representation with special symbols like "," or "-" replaced
safe_1  = aput.read_decay_name(event_type=event_type, style= 'safe_1')

# To get event type back from nickname, only safe_1 implemented for now
event_type = aput.read_event_type(nickname=nickname, style= 'safe_1')
```

### Update table with nicknames and event types

This is most likely not needed, unless a new sample has been created and a new nickname needs to be added. The following lines:

```bash
export DECPATH=/home/acampove/Packages/DecFiles

update_decinfo
```

will:

1. Set the path to the [DecFiles](https://gitlab.cern.ch/lhcb-datapkg/Gen/DecFiles)
root directory such that `update_decinfo` can use it.
1. Read the event types and nicknames and save them to a YAML file
1. Read the event types and decay strings and save them to a YAML file

