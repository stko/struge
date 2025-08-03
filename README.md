# Struge - a Structure Generation Tool

Struge helps to generate nested textual structures out of component definitons and an overall layout instruction.

What does this mean in practice?

Let's say you want to generate a layout mockup for a new web application. For that you could either use some of the online design tools like Figma. But these tools are mostly tailored for UI design for small mobile devices, but not for more desktop like UIs with menu bars, project explorers and tool boxes.

Another approach could be tools like the Qt designer, but that requires at least anything like some player software for everybody who want to take a look into the design.

When then finally look into the web design tools, then you normally need to decide first with which toolbox (Vue, jQueryIU, Nuvt ect.) you want to go, before you can sketch your first design ideas, but if you want to do some sketches first and decide on the implementation later, then you have not much choise as to write the (html-) sources first by hand.

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

This file can also contain element definitions, but its main purpose is to contain the layout instruction of how to make the final source codes out of the given project and components properties.


This build is done with the help of the `Jinja Template Engine` 

## Struge and the Jinja Template Engine
The [Jinja Template Engine](https://jinja.palletsprojects.com/en/stable/templates/) allows to take a textual template (everything is possible, as long it is any kind of text) and inject some data into it, which is provided by the Struge data objects.





