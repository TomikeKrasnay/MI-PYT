import click
import configparser
import os
import sys

from .basePrinter import Printer, QuietPrinter, VerbosePrinter
from .runModes import RunProcessor, DryRunProcessor, DEFAULT_ERROR_RETURN

DEFAULT_CONFIG_FILE = './config.cfg'
NO_GH_TOKEN_RETURN = 3
GH_ERROR_RETURN = {
    401: 4,
    404: 5
}
NO_LABELS_SPEC_RETURN = 6
NO_REPOS_SPEC_RETURN = 7
NO_WEBHOOK_SECRET_RETURN = 8


###############################################################################
# Simple helpers
###############################################################################

def create_config(config_filename=None, token=None):
    """Method for load a config file from the local storage.

    If config no exists, creates a new configuration.

    Args:
        config_filename (str): Path config file.
        token (str): A GitHub token.

    Returns:
        ConfigParser: Configuration from config file.

    """
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg_filename = config_filename or DEFAULT_CONFIG_FILE

    if os.access(cfg_filename, os.R_OK):
        with open(cfg_filename) as f:
            cfg.read_file(f)
    if token is not None:
        cfg.read_dict({'github': {'token': token}})
    return cfg


def extract_labels(gh, template_opt, cfg):
    """Method for extracting labels from the config file or the template repository.

    Args:
        gh (GitHub): A GitHub object.
        template_opt (str): A template repository.
        cfg: (ConfigParser): Current configuration.

    Returns:
        dictionary where key and value is str: A mapping of color to each label in the given repository.

    """
    if template_opt is not None:
        return gh.list_labels(template_opt)
    if cfg.has_section('others') and 'template-repo' in cfg['others']:
        return gh.list_labels(cfg['others']['template-repo'])
    if cfg.has_section('labels'):
        return {name: str(color) for name, color in cfg['labels'].items()}
    click.echo('No labels specification has been found', err=True)
    sys.exit(NO_LABELS_SPEC_RETURN)


def get_labels_from_json(labels):
    """Method for parsed labels from the json data."""
    parsed_labels = {}
    for one_label in labels:
        parsed_labels[one_label['name']] = one_label['color']

    return parsed_labels


def get_repos_from_json(repos):
    """Method for parsed repos from the json data."""
    parsed_repos = []
    for one_repo in repos:
        parsed_repos.append(one_repo['full_name'])
    return parsed_repos


def extract_repos(cfg):
    """Method for extracting repositories from the configuration.

    Args:
        cfg: (ConfigParser): Current configuration.

    Returns:
        list ([str]): A list of repositories.

    """
    if cfg.has_section('repos'):
        repos = cfg['repos'].keys()
        return [r for r in repos if cfg['repos'].getboolean(r, False)]
    click.echo('No repositories specification has been found', err=True)
    sys.exit(NO_REPOS_SPEC_RETURN)


def pick_printer(verbose, quiet):
    """Pick the correct printer, based on verbosity.
    Returns:
            BasePrinter: VerbosePrinter or QuietPrinter or Printer.

    """
    if verbose and not quiet:
        return VerbosePrinter
    if quiet and not verbose:
        return QuietPrinter
    return Printer


def pick_runner(dry_run):
    """Pick the correct runner.

    If dry_run is picked, the program won't do any changes.

    """
    return DryRunProcessor if dry_run else RunProcessor


def gh_error_return(github_error):
    """Return a GitHub request status code.

    Args:
        github_error (GitHubError): an exception object representing the error

    """
    return GH_ERROR_RETURN.get(github_error.status_code, DEFAULT_ERROR_RETURN)


def retrieve_github_client(ctx):
    """Retrieve the GitHub object.

        If GitHub not exists, function exits the program.

        Args:
            ctx: click context.

        Returns:
            GitHub: The GitHub object.

    """
    if 'GitHub' not in ctx.obj:
        click.echo('No GitHub token has been provided', err=True)
        sys.exit(NO_GH_TOKEN_RETURN)
    return ctx.obj['GitHub']
