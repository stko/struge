from typing import Optional

import argparse
import json
from jinja2 import Environment
import oyaml


class Node(dict):
    """dict extension class to store one element of the tree,
    recursive load and print
    """
    object_count = 0
    component_count= 0
    layout_count = 0
    reference_count = 0

    def __init__(
        self,
        parent,
        struge_name: str,
        own_node,
        model: dict,
        components: dict,
        layouts: dict,
    ):
        self.struge_name = struge_name
        self.parent = parent
        if "name" not in own_node:
            Node.object_count += 1
            self.name = f"object_{Node.object_count}"
        else:
            self.name= own_node["name"]
            del own_node["name"]
        self.content = ""
        self.inner_content = ""
        self.layout= ""
        self.inner= None
        if isinstance(own_node, str):
            self.content = own_node
        else:
            for key, value in own_node.items():
                if key == "inner":
                    self.inner = self.eval_inner(value, model, components, layouts, True)
                elif key == "layout":
                    if value not in layouts:
                        print(
                            f"FATAL: Layout '{value}' not found in layout definitions - Aborting.."
                        )
                        raise ValueError(
                            f"Layout '{value}' not found in layout definitions - Aborting.."
                        )
                    self.layout = layouts[value]
                else:
                    if key.startswith("~"):
                        key = key[1:]  # remove the write protection
                    self[key] = value
            # now we inerit the parent content
            if self.parent:
                for key, value in parent.items():
                    if "~"+key in own_node: # write protected key
                        continue
                    self[key] = value
        #self.get_content()

    def get_content(self):
        if self.inner:
            if isinstance(self.inner, list):
                for sub_node in self.inner:
                    if isinstance(sub_node, Node):
                        self.inner_content += sub_node.get_content()
                    else:
                        self.inner_content += str(sub_node)
            else:
                    if isinstance(self.inner, Node):
                        self.inner_content += self.inner.get_content()
                    else:
                        self.inner_content += str(self.inner)
        if self.layout:
            env = Environment()
            t = env.from_string(self.layout)
            self.content = t.render(item=self, inner=self.inner_content)
            return self.content
        else:
            self.content = self.inner_content
            return self.content
    
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
        self, node_name, model: dict, components: dict, layout: dict, is_component: bool
    ):
        if isinstance(node_name, dict):
            # if the node is a dict, we create a new node with the name
            Node.reference_count += 1
            first_node_name = list(node_name.keys())[0]
            node_name=node_name[first_node_name]
            first_node_name= f"{first_node_name}_{Node.reference_count}"
            return Node(
                self,
                struge_name=first_node_name,
                own_node=node_name,
                model=model,
                components=components,
                layouts=layout,
            )
        elif node_name in model:
            return Node(
                self,
                struge_name=node_name,
                own_node=model.get(node_name),
                model=model,
                components=components,
                layouts=layout,
            )
        elif node_name in components:
            Node.component_count += 1
            return Node(
                self,
                struge_name=f"component_{Node.component_count}",
                own_node=components.get(node_name),
                model=model,
                components=components,
                layouts=layout,
            )
        elif node_name in layout:
            Node.layout_count += 1
            # if the node is a layout, we create a new node with the name
            return Node(
                self,
                struge_name=f"layout_{Node.layout_count}",
                own_node=layout.get(node_name),
                model=model,
                components=components,
                layouts=layout,
            )
        else:
            return node_name

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
        self, project_file_path: str, components_file_path: str, implementation_file_path: str
    ):
        try:
            with open(project_file_path, encoding="utf8") as fin:
                self.main = oyaml.load(fin, Loader=oyaml.Loader)
        except:
            self.main = {}
        try:
            with open(components_file_path, encoding="utf8") as fin:
                self.components = oyaml.load(fin, Loader=oyaml.Loader)
        except:
            self.components = {}
        try:
            with open(implementation_file_path, encoding="utf8") as fin:
                self.layout = oyaml.load(fin, Loader=oyaml.Loader)
        except:
            self.layout = {}
        self.structure: Optional[Node] = None  # stores the final tree

    def _parse(self):
        if "main" not in self.main:
            print(
                "FATAL: Main data does not contain the 'main' root element - Aborting.."
            )
        self.structure = Node(
            None,
            "main",
            self.main.get("main"),
            self.main,
            self.components,
            self.layout,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-p", "--project", help="the main yaml project layout", default="project.yaml"
    )
    parser.add_argument(
        "-c",
        "--components",
        help="the yaml component library",
        default="components.yaml",
    )
    parser.add_argument(
        "-i", "--implementation", help="the  yaml implementation instructions", default="implementation.yaml"
    )
    parser.add_argument(
        "-o", "--output", help="the generated output", default="dist/index.html"
    )

    args = parser.parse_args()
    layout = Layout(args.project, args.components, args.implementation)
    layout._parse()
    print(json.dumps(layout.structure,sort_keys=True, indent=4))
    content = layout.structure.get_content()
    with open(args.output, "w", encoding="utf8") as fout:
        fout.write(content)
    print(content)
