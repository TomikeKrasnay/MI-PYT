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
    if template_opt is not None:
        return gh.list_labels(template_opt)
    if cfg.has_section('others') and 'template-repo' in cfg['others']:
        return gh.list_labels(cfg['others']['template-repo'])
    if cfg.has_section('labels'):
        return {name: str(color) for name, color in cfg['labels'].items()}
    click.echo('No labels specification has been found', err=True)
    sys.exit(NO_LABELS_SPEC_RETURN)


def extract_repos(cfg):
    if cfg.has_section('repos'):
        repos = cfg['repos'].keys()
        return [r for r in repos if cfg['repos'].getboolean(r, False)]
    click.echo('No repositories specification has been found', err=True)
    sys.exit(NO_REPOS_SPEC_RETURN)


def pick_printer(verbose, quiet):
    if verbose and not quiet:
        return VerbosePrinter
    if quiet and not verbose:
        return QuietPrinter
    return Printer


def pick_runner(dry_run):
    return DryRunProcessor if dry_run else RunProcessor


def gh_error_return(github_error):
    return GH_ERROR_RETURN.get(github_error.status_code, DEFAULT_ERROR_RETURN)


def retrieve_github_client(ctx):
    if 'GitHub' not in ctx.obj:
        click.echo('No GitHub token has been provided', err=True)
        sys.exit(NO_GH_TOKEN_RETURN)
    return ctx.obj['GitHub']
