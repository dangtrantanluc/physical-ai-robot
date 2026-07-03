"""Physical AI Robot — Backend "Robot Brain".

Clean Architecture + DDD. Dependency rule: outer layers depend on inner layers,
never the reverse.

    api  ->  application  ->  domain
    infrastructure  ->  domain   (implements domain ports)
    core is cross-cutting (config, logging, DI container).
"""

__version__ = "0.1.0"
