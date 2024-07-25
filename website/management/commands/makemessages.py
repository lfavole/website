from django.core.management.commands.makemessages import Command as OldCommand

class Command(OldCommand):
    """
    This class does the same thing as the original `makemessages` command
    but the default value of `--add-location` is changed to `never`.
    """
    def add_arguments(self, parser):
        super().add_arguments(parser)
        for action in parser._actions:
            if "--add-location" in action.option_strings:
                action.default = "never"
