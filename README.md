# Struge - a Structure Generation Tool

Struge helps to generate nested textual structures out of component definitons and an overall layout instruction.

What does this mean in practice?

Let's say you want to generate a layout mockup for a new web application. For that you could either use some of the online design tools like Figma. But these tools are mostly tailored for UI design for small mobile devices, but not for more desktop like UIs with menu bars, project explorers and tool boxes.

Another approach could be tools like the Qt designer, but that requires at least anything like some player software for everybody who want to take a look into the design.

When then finally looking into the web design tools, then you normally need to decide first with which toolbox (Vue, jQueryIU, Nuvt ect.) you want to go, before you can sketch your first design ideas, but if you want to do some sketches first and decide on the implementation later, then you have not much choice as to write the (html-) sources first by hand.

But when writing more complex html structures just with a text editor, you'll probertly find that it is quite time consuming and anouying  to play around with nested html elements and all its variants of class and style properties. Each time when something need to be modified, you have to carefully change the elements without destroying the nested structures or to find and modify all affected html elements.

It would be much easier if even such a simple mockup could be made out of a simple construction kit, and that is where `Struge` comes in place.

With `Struge`, you can
  * seperate between your layout idea and the final implementation. You could even have diffenent implemention models and apply your layout to them to see the different appearences.
  * define reoccuring elements as a component. So whenever you want to change any of its properties, you'll only need to change it ones, and Struge will replace all occurencies.

## How does Struge work?
All data for Struge are stored as YAML text files. Struge reads these files, concats the content and compiles the output, so its command line syntax is

```
python struge.py --help
usage: struge.py [-h] [-p PROJECT] [-c COMPONENTS] [-i IMPLEMENTATION] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -p PROJECT, --project PROJECT
                        the main yaml project layout (default: project.yaml)
  -c COMPONENTS, --components COMPONENTS
                        the yaml component library (default: components.yaml)
  -i IMPLEMENTATION, --implementation IMPLEMENTATION
                        the yaml implementation instructions (default: implementation.yaml)
  -o OUTPUT, --output OUTPUT
                        the generated output (default: dist/index.html)
```

### project.yaml
This file contains, programmably spoken, a dictionary with at least one entry. This entry must be named `main`, as that is the starting point to compile the output. This file can also contain other elements, which are unique to this project and don't need to be shared.

### components.yaml
This file is optional. Whenever some elements shall be used in multiple projects, they can be collected in this file, and then this file can be used in different projects. 

### implementation.yaml
This file finally contains everything which is needed to calculate the final implementation of a project.

This file can also contain element definitions, but its main purpose is to contain the layout instruction of how to build the final output out of the given project and components properties.


This build is done with the help of the [Jinja Template Engine](https://jinja.palletsprojects.com/en/stable/templates/) 

## Struge and the Jinja Template Engine
The [Jinja Template Engine](https://jinja.palletsprojects.com/en/stable/templates/) allows to take a textual template (everything is possible, as long it is any kind of text) and inject some data into it, which is provided by the Struge data objects.

Explained by a use case (which are the included sample files):

We have a `project.yaml` file:

```
main:
    title: "Struge Example Project"
    layout: page
    inner:
        - c_h2_header:
            text: "My first text"
        - c_h3_header:
            text: "My second text"
        - c_h3_header_with_protected_text:
            text: "My third text"
        - p_list    

p_list:
    layout: list
    list_items:
        - list element 1
        - list element 2
        - list element 3 
```

a `components.yaml` file:

```
c_h2_header:
    layout: header
    size: h2

c_h3_header:
    layout: header
    size: h3


c_h3_header_with_protected_text:
    layout: header
    size: h3
    ~text: "This text is protected and will not be overridden by the parent."

```

and a `implementation.yaml` file:

```
page: '<html>

  <head>

      <title>{{ item.title }}</title>

  </head>

  <body>

     {{ inner }}

  </body>

  </html>'


header: '<{{ item.size }}>{{ item.text }}</{{ item.size }}>'

list: '<ul>
    
    {% for li in item.list_items %}
    <li>{{ li }}
    
    {% endfor %}
    </ul>'

```

which will finally generate the following result `dist/index.html`

```
<html>
<head>
<title>Struge Example Project</title>
</head>
<body>
<h2>My first text</h2><h3>My second text</h3><h3>This text is protected and will not be overridden by the parent.</h3><ul>
 <li>list element 1
 <li>list element 2
 <li>list element 3
 </ul>
</body>
</html>
```


Let's start with the `project.yaml`. It contains at least a `main` element, which is always the starting point. It may also contain some more other elements.

As naming convention all elements (except `main`) which are in the project itself are named with a leading `p_`, all components with a leading `c_`.

All elements can have any properties as needed, but there are two reserved property names which are used to calculate the results. These both are `layout` and `inner`. Their meanings are explained below.


So as the starting point, the `main` element is evaluated. When an element contains some `inner`, then these element references will recursively followed to finally compose the whole element tree.

To pass through properties from parent elements down to their final implementation, a principle called `property inheritance` is used

## Property Inheritance
Each property of a parent is copied to it's childs. In the above example this is done with the `text` property to feed its value through into the final implementation output.

When needed, it can be avoided that a child property will be overwritten by its parent by name the child property with a leading `~` like done in the example with the text property of the `c_h3_header_with_protected_text` component.

## Final Layout Implementation

After the above mention parent - child tree have been build and all properties have be inheritated, the final implementation will be calculated. This is done recusively from bottom to top in the following way:

When a node contains a `inner` element, then these inner nodes are calculated first. They return some content which is taken as the inner content of a node. When then the node also contains a `layout` instruction, then the node properties and its previously calculated inner content is used to feed the [Jinja Template Engine](https://jinja.palletsprojects.com/en/stable/templates/) with it.

In pseudo code, this would be like this:

     the_node_content = jinja_template_evaluation(item, inner)

where `item` is the node itself, and `inner` is the previously calculated inner content of the node.

These two variables are then evaluated by the jinja engine inside the given template, like we do for the headers with the `header` template in 

     header: '<{{ item.size }}>{{ item.text }}</{{ item.size }}>'

where the node (=item) `size` and `text` properties are used the generate a html header element.

Thanks to the powerful jinja engine, we can access all elements of the node and e.g. iterate through all its `list_items` to generate a html list like this:

```
list: '<ul>
    
    {% for li in item.list_items %}
    <li>{{ li }}
    
    {% endfor %}
    </ul>'

```

Finally whereever we want to fill the output with the inner content of the node, we simply can use the `inner` variable in our template which represents the inner content

    {{ inner }}


