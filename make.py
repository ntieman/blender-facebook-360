import re
import os

__dir__ = os.path.dirname(os.path.realpath(__file__))


def path(relative):
    return os.path.join(__dir__, relative)


modules = [
    'xmp',
    'ui',
    '__init__'
]

combined = ''
imports = modules[:]

for module in modules:
    short_path = module + '.py'
    full_path = path('src/' + short_path)

    with open(full_path, 'r') as f:
        combined += "#{}\n".format(short_path)
        line = f.readline()

        while line:
            include_line = True
            match = re.match(r'(from ([A-Za-z0-9.]+) )?import ([A-Za-z0-9.]+)', line)

            if match:
                import_from = match.group(2)
                import_main = match.group(3)

                if import_main in imports or import_from in modules:
                    include_line = False

                imports.append(import_main)
            if include_line:
                combined += line

            line = f.readline()

        combined += "\n"

with open(path('dist/facebook_360.py'), 'w') as f:
    f.write(combined)
