#!/usr/bin/env python
import re
import sys

# Validate project_slug
MODULE_REGEX = r'^[_a-zA-Z][_a-zA-Z0-9]+$'
module_name = '{{ cookiecutter.project_slug }}'

if not re.match(MODULE_REGEX, module_name):
    print(f'ERROR: {module_name} is not a valid Python module name!')
    print('Please use only letters, numbers, and underscores, and start with a letter or underscore.')
    sys.exit(1)

# Validate email
EMAIL_REGEX = r'^[^@]+@[^@]+\.[^@]+$'
email = '{{ cookiecutter.author_email }}'

if not re.match(EMAIL_REGEX, email):
    print(f'ERROR: {email} is not a valid email address!')
    sys.exit(1)

print(f"✅ Pre-generation validation passed for {module_name}")