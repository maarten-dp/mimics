from mimics import Mimic


def test_it_can_defer_class_definition():
    mimic = Mimic()
    Husk = mimic.husk()

    class TestDeferred(Husk):
        def do_the_thing(self):
            return self.thing

    zhu_li = TestDeferred("doing the thing")
    dont_look_yet = zhu_li.do_the_thing()

    class Test:
        def __init__(self, thing):
            self.thing = thing

    mimic.absorb(Husk).as_being(Test)

    assert dont_look_yet == "doing the thing"
