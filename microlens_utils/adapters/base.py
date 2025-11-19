"""Input/output package interface and base parameterization adapters.

All conversion adapters should inherit from BaseAdapter and implement the
required methods to convert to/from the BaseModel truth representation. This
way there are only a small number of adapter implementations needed to support
many different input/output formats.

"""