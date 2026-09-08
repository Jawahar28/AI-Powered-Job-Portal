from jobs.services.sources.adzuna import AdzunaSource

JOB_SOURCES = {
    "Adzuna" : AdzunaSource,
}

def get_source(name):
    source_class = JOB_SOURCES.get(name)

    if not source_class:
        raise ValueError (
            f"Unknown job source : {name}"
        )

    return source_class()