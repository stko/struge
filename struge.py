import argparse
from copy import copy
import oyaml


class Node(dict):
    """dict extension class to store one element of the tree,
    recursive load and print
    """

    def __init__(
        self,
        name: str,
        own_node,
        model: dict,
        components: dict,
        layout: dict,
        is_component: bool,
    ):
        self.name = name
        for key, value in own_node.items():
            if key == "inner":
                self["inner"] = self.eval_inner(value, model, components, layout, True)
            else:
                self[key] = value

    def eval_inner(
        self, own_node, model: dict, components: dict, layout: dict, is_component: bool
    ):
        if isinstance(own_node, str):
            return self.eval_single_node(own_node, model, components, layout, True)
        else:
            result = []
            for sub_node in own_node:
                result.append(
                    self.eval_single_node(sub_node, model, components, layout, True)
                )
            return result

    def eval_single_node(
        self, own_node, model: dict, components: dict, layout: dict, is_component: bool
    ):

        if own_node in model:
            return Node(
                name=own_node,
                own_node=model.get(own_node),
                model=model,
                components=components,
                layout=layout,
                is_component=False,
            )
        elif own_node in components:
            return Node(
                components.get(own_node),
                model=model,
                components=components,
                layout=layout,
                is_component=True,
            )
        elif own_node in layout:
            return Node(
                layout.get(own_node),
                model=model,
                components=components,
                layout=layout,
                is_component=True,
            )
        else:
            return own_node

    def create_copy(
        self, own_node, model: dict, components: dict, layout: dict, is_component: bool
    ):
        pass


class Layout:
    """
    loads the three inputs for the main layout,
    the self defined component layer and the final
    implementation
    """

    def __init__(
        self, main_file_path: str, components_file_path: str, layout_file_path_str
    ):
        try:
            with open(main_file_path, encoding="utf8") as fin:
                self.main = oyaml.load(fin, Loader=oyaml.Loader)
        except:
            self.main = {}
        try:
            with open(components_file_path, encoding="utf8") as fin:
                self.components = oyaml.load(fin, Loader=oyaml.Loader)
        except:
            self.components = {}
        try:
            with open(layout_file_path_str, encoding="utf8") as fin:
                self.layout = oyaml.load(fin, Loader=oyaml.Loader)
        except:
            self.layout = {}
        self.structure = None  # stores the final tree

    def _parse(self):
        if "main" not in self.main:
            print(
                "FATAL: Main data does not contain the 'main' root element - Aborting.."
            )
        self.structure = Node(
            "main",
            self.main.get("main"),
            self.main,
            self.components,
            self.layout,
            False,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-m", "--main", help="the main yaml build layout", default="main.yaml"
    )
    parser.add_argument(
        "-c",
        "--components",
        help="the yaml component library",
        default="components.yaml",
    )
    parser.add_argument(
        "-l", "--layout", help="the  yaml layout instructions", default="layout.yaml"
    )

    args = parser.parse_args()
    layout = Layout(args.main, args.components, args.layout)
    layout._parse()
    print(layout)
