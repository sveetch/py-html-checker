
def click_debug_helper(results, caplog=None, expected=None):
    """
    A simple helper function for a common printout of a click command failures.

    Arguments:
        results (object): Result object as returned from ``CliRunner.runner.invoke()``.

    Keyword Arguments:
        caplog (function): Pytest's Caplog fixture function if available to debug
            logging messages.
        expected (object): Any object type that would be expected from main test
            assertion.
    """
    print("=> results.output <=")
    print(results.output)
    print()

    print("=> results.exception <=")
    print(results.exception)
    print()

    if expected:
        print("=> expected <=")
        print(expected)
        print()

    if caplog:
        print("=> caplog.record_tuples <=")
        print(caplog.record_tuples)
        print()

    print("=> results.exception <=")
    print(type(results.exception))
    print(results.exception)
    print()
    if results.exception is not None:
        raise results.exception
