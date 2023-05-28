import platform

print(
    "{} {}".format(
        platform.python_implementation(),
        platform.python_version(),
    )
)
