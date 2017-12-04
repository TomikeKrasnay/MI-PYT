import click

###############################################################################
# Printing and logging
###############################################################################


class BasePrinter:
    """Class for various printing types.

    Attributes:
        repos (set): All repositories.
        errors (int): Count of errors.

     """

    SUCCESS_SUMMARY = '{} repo(s) updated successfully'
    ERROR_SUMMARY = '{} error(s) in total, please check log above'

    EVENT_CREATE = 'ADD'
    EVENT_DELETE = 'DEL'
    EVENT_UPDATE = 'UPD'
    EVENT_LABELS = 'LBL'

    RESULT_SUCCESS = 'SUC'
    RESULT_ERROR = 'ERR'
    RESULT_DRY = 'DRY'

    def __init__(self):
        """Default constructor, define all class variables"""
        self.repos = set()
        self.errors = 0

    def add_repo(self, slug):
        """Adds a repository to the class variable repos.

        Args:
            slug (str): A GitHub repository slug.

        """
        self.repos.add(slug)

    def event(self, event, result, repo, *args):
        """This method is called when event is printed.

        In this parent method only counting errors.
        Args:
            event (str): Which event has been use on the repo.
            result (str): Result
            repo: repository

        """
        if result == self.RESULT_ERROR:
            self.errors += 1

    def summary(self):
        """This method prints summary for each event.

        This method has been overridden in children classes.

        """
        pass

    def _create_summary(self):

        """This method creates summary.

        Check if there were no errors, If is error count more than 0,
        add their count to the result string. Resulting message contains
        how many repositories were processed.

        Returns:
            str - the resulting string.
        """

        if self.errors > 0:
            return self.ERROR_SUMMARY.format(self.errors)
        return self.SUCCESS_SUMMARY.format(len(self.repos))


class Printer(BasePrinter):
    """This class is the general printer."""

    def event(self, event, result, repo, *args):
        super().event(event, result, repo, *args)
        if result == self.RESULT_ERROR:
            line_parts = ['ERROR: ' + event, repo, *args]
            click.echo('; '.join(line_parts))

    def summary(self):
        click.echo('SUMMARY: ' + self._create_summary())


class QuietPrinter(BasePrinter):
    """This printer is used when the application is in quiet/silent mode."""
    pass


class VerbosePrinter(BasePrinter):
    """This printer is used when the application is in verbose mode."""

    LINE_START = '[{}][{}] {}'

    def event(self, event, result, repo, *args):
        super().event(event, result, repo, *args)
        line_parts = [self.LINE_START.format(event, result, repo), *args]
        click.echo('; '.join(line_parts))

    def summary(self):
        click.echo('[SUMMARY] ' + self._create_summary())
