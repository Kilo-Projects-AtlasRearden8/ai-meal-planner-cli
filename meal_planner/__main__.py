"""Allow ``python -m meal_planner`` to launch the CLI."""

import sys

from .cli import main

sys.exit(main())
