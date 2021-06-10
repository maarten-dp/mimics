import operator

import pytest

from mimics import Deferred, TrueSight, Recorder, Mimic


def test_it_can_defer_a_funtion_call(trap):
    def some_function(param1, param2):
        return f"{param1} {param2}"

    some_function = trap.suspend(some_function)

    result = some_function("bomp", "bamp")

    assert result != "bomp bamp"
    trap.release(some_function)
    assert result == "bomp bamp"


def test_it_can_defer_an_instanced_function_call(trap):
    class Test:
        def some_function(self, param1, param2):
            return f"{self.__class__.__name__} {param1} {param2}"

    Test = trap.suspend(Test)

    test = Test()
    result = test.some_function("bomp", "bamp")

    assert result != "Test bomp bamp"
    trap.release(Test)
    assert result == "Test bomp bamp"


def test_it_can_defer_a_decorator(trap):
    def some_decorator(fn):
        def decorator(*args, **kwargs):
            injected = "I'm injected!"
            return fn(injected, *args, **kwargs)

        return decorator

    some_decorator = trap.suspend(some_decorator)

    @some_decorator
    def some_function(injected, param1):
        return f"{injected} => {param1}"

    result = some_function("yuck")

    assert result != "I'm injected! => yuck"
    trap.release(some_decorator)
    assert result == "I'm injected! => yuck"


def test_it_can_defer_second_level_decorator(trap):
    class Test:
        def some_decorator(self, fn):
            def decorator(*args, **kwargs):
                injected = f"I'm injected from {self.__class__.__name__}!"
                return fn(injected, *args, **kwargs)

            return decorator

    Test = trap.suspend(Test)
    test = Test()

    @test.some_decorator
    def some_function(injected, param1):
        return f"{injected} => {param1}"

    result = some_function("yuck")

    assert result != "I'm injected from Test! => yuck"
    trap.release(Test)
    assert result == "I'm injected from Test! => yuck"


def test_it_can_format_a_suspended_result():
    deferred = Deferred(Recorder(), "SomeString")
    handle = TrueSight(deferred)
    handle.suspended = False

    assert f"{deferred}!" == "SomeString!"


def test_it_can_pose_as_an_instance(trap):
    class Test:
        pass

    DeferredTest = trap.suspend(Test)

    test = DeferredTest()
    # Should this be an instance of DeferredTest?
    assert isinstance(test, Deferred)
    trap.release(DeferredTest)
    assert isinstance(test, Test)


def test_it_can_suspend_an_initialization_with_parameters(trap):
    class Test:
        def __init__(self, param1):
            self.param1 = param1

    Test = trap.suspend(Test)
    test = Test("some param")

    assert test.param1 != "some param"
    trap.release(Test)
    assert test.param1 == "some param"


@pytest.mark.parametrize(
    "op,result",
    [
        (operator.add, 7),
        (operator.sub, -1),
        (operator.mul, 12),
        (operator.pow, 81),
        (operator.floordiv, 0),
        (operator.mod, 3),
        (operator.and_, 0),
        (operator.or_, 7),
        (operator.xor, 7),
        (operator.lshift, 48),
        (operator.rshift, 0),
        (operator.eq, False),
        (operator.ne, True),
        (operator.ge, False),
        (operator.gt, False),
        (operator.le, True),
        (operator.lt, True),
    ],
)
def test_it_can_defer_operators(trap, op, result):
    var = 3
    var = trap.suspend(var)
    result = op(var, 4)

    assert result != result
    trap.release(var)
    assert result == result


@pytest.mark.skip("Have a look at this later")
def test_it_can_defer_operation_assignments(trap):
    my_number = 4
    my_number = trap.suspend(my_number)
    my_number += 5
    trap.release(my_number)
    assert my_number == 9


def test_a_mimic_can_solve_chicken_and_egg():
    class A:
        def __init__(self, b):
            self.b = b

    class B:
        def __init__(self, a):
            self.a = a

    mimic = Mimic()
    husk = mimic.husk()
    b = B(husk)
    a = A(b)
    mimic.absorb(husk).as_being(a)

    assert b.a == a
    assert a.b == b
