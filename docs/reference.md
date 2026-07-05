# API reference

fvattrs works by decorating a function with `@define_io` and defining how to convert and validate the function's argument(s) and output. It also offer `define` to convert/validate inline.


## Core

::: src.fvattrs._core.define
    options:
      heading_level: 3
      show_root_heading: true
      show_root_full_path: false

::: src.fvattrs._core.define_io
    options:
      heading_level: 3
      show_root_heading: true
      show_root_full_path: false

::: src.fvattrs._core.PositionalArgument
    options:
      heading_level: 3
      show_root_heading: true
      show_root_full_path: false

::: src.fvattrs._core.KeywordArgument
    options:
      heading_level: 3
      show_root_heading: true
      show_root_full_path: false

::: src.fvattrs._core.Output
    options:
      heading_level: 3
      show_root_heading: true
      show_root_full_path: false


## Converters

::: src.fvattrs.converters.to_path
    options:
      heading_level: 3
      show_root_heading: true
      show_root_full_path: false

::: src.fvattrs.converters.to_date
    options:
      heading_level: 3
      show_root_heading: true
      show_root_full_path: false


## Validators

::: src.fvattrs.validators.is_file
    options:
      heading_level: 3
      show_root_heading: true
      show_root_full_path: false

::: src.fvattrs.validators.is_folder
    options:
      heading_level: 3
      show_root_heading: true
      show_root_full_path: false