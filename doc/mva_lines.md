# Specific to MVA lines in the RD group

## Add lines to `Config.py`

To do that run:

```bash
transform_text -i Config.py -c conf_rename.toml
```

which will create an `output.py` file with the replacements specified in `hlt_rename.toml`.

## Add lines to `main.py`

To do that run:

```bash
transform_text -i main.py  -c main_rename.toml
```
