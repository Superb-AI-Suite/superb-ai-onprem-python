

class UndefinedType():
    """A singleton type used to represent an undefined value."""
    def __repr__(self):
        return "Undefined"

    def __bool__(self):
        return False  # Ensures it evaluates as False in boolean contexts

Undefined = UndefinedType()
