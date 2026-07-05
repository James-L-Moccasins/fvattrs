from hypothesis import strategies


primitives = strategies.one_of(
    strategies.booleans(),
    strategies.integers(),
    strategies.floats(),
    strategies.text(),
    strategies.dates(),
)
