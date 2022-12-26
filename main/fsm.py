from transitions.extensions import GraphMachine

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

machine = TocMachine(
    states=["start", "add_art", "remove_art", "clear_art", "show_act", "my_art",
            "no_support", "create_art", "select_art"],
    transitions=[
        {
            "trigger": "advance",
            "source": "start",
            "dest": "add_art",
            "conditions": "add_art",
        },
        {
            "trigger": "advance",
            "source": "start",
            "dest": "clear_art",
            "conditions": "clear_art",
        },
        {
            "trigger": "advance",
            "source": "start",
            "dest": "remove_art",
            "conditions": "remove_art",
        },
        {
            "trigger": "advance",
            "source": "start",
            "dest": "show_act",
            "conditions": "show_act",
        },
        {
            "trigger": "advance",
            "source": "start",
            "dest": "my_art",
            "conditions": "my_art",
        },
        {
            "trigger": "advance",
            "source": "start",
            "dest": "no_support",
            "conditions": "no_support",
        },
        {
            "trigger": "advance",
            "source": "start",
            "dest": "create_art",
            "conditions": "create_art",
        },
        {
            "trigger": "advance",
            "source": "create_art",
            "dest": "start",
            "conditions": "else",
        },
        {
            "trigger": "advance",
            "source": "create_art",
            "dest": "select_art",
            "conditions": "select_art",
        },
        {
            "trigger": "advance",
            "source": "select_art",
            "dest": "start",
            "conditions": "draw",
        },
        {"trigger": "go_back", "source": ["add_art", "remove_art", "clear_art", "show_act", "my_art", "no_support"], "dest": "start"},
    ],
    initial="start",
    auto_transitions=False,
    show_conditions=True,
)
machine.get_graph().draw("fsm.png", prog="dot", format="png")
