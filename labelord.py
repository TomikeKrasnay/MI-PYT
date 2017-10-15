# This is skeleton for labelord module
# MI-PYT, task 1 (requests+click)
# File: labelord.py
# TODO: create requirements.txt and install
import click
import requests
import configparser
import json

# PRIVATE FUNCTIONS


def request(url, session):
    r = session.get(url)
    if r.status_code == 404:
        click.echo("GitHub: ERROR 404 - Not Found")
        exit(5)

    if r.status_code == 401:
        click.echo('GitHub: ERROR 401 - Bad credentials')
        exit(4)

    if r.status_code != 200:
        exit(10)

    result = r.json()
    if r.links:
        while 'next' in r.links:
            next_url = r.links['next']['url']
            r = session.get(next_url)
            result = result + r.json()

    return result


def labels_for_run(session, repo_name, is_quiet, is_verbose):
    r = session.get('https://api.github.com/repos/' + repo_name + '/labels?per_page=100&page=1')
    if r.status_code == 404:
        if (is_quiet and is_verbose) or (not is_quiet and not is_verbose):
            click.echo("ERROR: LBL; {}; 404 - Not Found".format(repo_name))
            return {}

        if not is_quiet:
            click.echo("[LBL][ERR] {}; 404 - Not Found".format(repo_name))
        return {}

    if r.status_code == 401:
        if not is_quiet:
            click.echo("[LBL][ERR] {}; 401 - Bad credentials".format(repo_name))
        return {}

    result = r.json()
    # if r.links:
    #     while 'next' in r.links:
    #         next_url = r.links['next']['url']
    #         r = session.get(next_url)
    #         result = result + r.json()
    return result


def print_repos(session):
    json_data = get_all_repos(session)

    for one_repo in json_data:
        click.echo("{}".format(one_repo["full_name"]))

    exit(0)


def print_labels(session, name_repo):
    json_data = get_all_labels(session, name_repo)
    for one_repo in json_data:
        click.echo("#{} {}".format(one_repo['color'], one_repo['name']))

    exit(0)


def get_all_labels(session, name_repo):
    json_data = request('https://api.github.com/repos/' + name_repo + '/labels?per_page=100&page=1', session)
    return json_data


def get_all_repos(session):
    json_data = request('https://api.github.com/user/repos?per_page=100&page=1', session)
    return json_data


def diff(first, second):
        second = set(second)
        return [item for item in first if item not in second]


def analyze_labels_actual_with_new(session, repo_name, old_git, new_labels, configuration, mode):
    parsed_git_labels = parse_labels(old_git)

    lowercase_git_labels = [x.lower() for x in parsed_git_labels]
    all_git_labels_name = [x for x in parsed_git_labels]
    lowercase_config_labels = [x.lower() for x in new_labels]

    number_errors = 0
    number_success = 0

    if mode == "replace":
        labels_for_delete = diff(lowercase_git_labels, lowercase_config_labels)
        for label in labels_for_delete:
            index = lowercase_git_labels.index(label)
            label_name = all_git_labels_name[index]
            if not delete_label(session, repo_name, label_name, parsed_git_labels[label_name], configuration):
                number_errors = number_errors + 1
            else:
                number_success = number_success + 1

    for key in new_labels:
        label_config_name_lower = key.lower()
        label_config_color = new_labels[key]
        if label_config_name_lower in lowercase_git_labels:
            if key in parsed_git_labels:
                # update label because color has been changed
                if label_config_color != parsed_git_labels[key]:
                   if not update_color_label(session, repo_name, key, label_config_color, configuration):
                       number_errors = number_errors + 1
                   else:
                       number_success = number_success + 1

            else:
                # update label because name has been changed
                if not update_color_label(session, repo_name, key, label_config_color, configuration):
                    number_errors = number_errors + 1
                else:
                    number_success = number_success + 1
        else:
            # create_color_label(session, repo_name, key, label_config_color, configuration)
            if not create_color_label(session, repo_name, key, label_config_color, configuration):
                number_errors = number_errors + 1
            # else:
            #     number_success = number_success + 1

    return [number_errors, number_success]


def parse_labels(labels):
    parsed_labels = {}
    for one_label in labels:
        parsed_labels[one_label['name']] = one_label['color']

    return parsed_labels


def parse_repos(repos):
    parsed_repos = {}
    for one_repo in repos:
        parsed_repos[one_repo['full_name']] = True

    return parsed_repos


def update_color_label(session, repo_name, label_name, new_color, configuration):
    is_dry = configuration['dry_run']
    is_quiet = configuration['quiet']
    is_verbose = configuration['verbose']
    if not is_dry:
        header_data = {"name": label_name, "color": new_color}
        url = 'https://api.github.com/repos/'+repo_name+'/labels/'+label_name
        response = session.patch(url, json.dumps(header_data))
        return handle_response(response, configuration, "UPD", 200, repo_name, label_name, new_color)
    else:
        if not is_quiet and is_verbose:
            click.echo("[UPD][DRY] {}; {}; {}".format(repo_name, label_name, new_color))
        return True


def create_color_label(session, repo_name, label_name, new_color, configuration):
    is_dry = configuration['dry_run']
    is_quiet = configuration['quiet']
    is_verbose = configuration['verbose']
    if not is_dry:
        header_data = {"name": label_name, "color": new_color}
        url = 'https://api.github.com/repos/'+repo_name+'/labels'
        response = session.post(url, json.dumps(header_data))
        return handle_response(response, configuration, "ADD", 201, repo_name, label_name, new_color)
    else:
        if not is_quiet and is_verbose:
            click.echo("[ADD][DRY] {}; {}; {}".format(repo_name, label_name, new_color))
        return True


def delete_label(session, repo_name, label_name, color, configuration):
    is_dry = configuration['dry_run']
    is_quiet = configuration['quiet']
    is_verbose = configuration['verbose']
    if not is_dry:
        url = 'https://api.github.com/repos/'+repo_name+'/labels/' + label_name
        response = session.delete(url)
        return handle_response(response, configuration, "DEL", 204, repo_name, label_name, color)
    else:
        if not is_quiet and is_verbose:
            click.echo("[DEL][DRY] {}; {}; {}".format(repo_name, label_name, color))
        return True


def handle_response(response, configuration, method, valid_code, repo_name, label_name, color):
    is_verbose = configuration['verbose']
    is_quiet = configuration['quiet']
    if response.status_code == valid_code:
        if not is_quiet and is_verbose:
            click.echo("[{}][SUC] {}; {}; {}".format(method, repo_name, label_name, color))
        return True
    else:
        if not is_quiet and is_verbose:
            click.echo("[{}][ERR] {}; {}; {}; {} - {}".format(method, repo_name, label_name, color,
                                                         response.status_code, response.json()['message']))
        if (is_quiet and is_verbose) or (not is_quiet and not is_verbose):
            click.echo("ERROR: {}; {}; {}; {}; {} - {}".format(method, repo_name, label_name, color,
                                                              response.status_code, response.json()['message']))

        return False





# PUBLIC FUNCTIONS


@click.group('labelord')
@click.pass_context
@click.option('-c', "--config", default="./config.cfg",
              help="Name of the config file")
@click.option('-t', "--token", envvar='GITHUB_TOKEN',
              help="Your github token")
def cli(ctx, config, token):
    if not token:
        configparser.optionxform = str
        config_file = configparser.ConfigParser()
        if not config_file.read(config):
            click.echo("No GitHub token has been provided")
            exit(3)

        token = config_file['github']['token']

    session = ctx.obj.get('session', requests.Session())
    session.headers = {'User-Agent': 'Python'}

    def token_auth(req):
        req.headers['Authorization'] = 'token ' + token
        return req

    session.auth = token_auth
    ctx.obj['session'] = session
    ctx.obj['config_file'] = config


@cli.command()
@click.pass_context
def list_repos(ctx):
    session = ctx.obj['session']
    print_repos(session)


@cli.command()
@click.argument('name_repo', nargs=1)
@click.pass_context
def list_labels(ctx, name_repo):
    session = ctx.obj['session']
    print_labels(session, name_repo)


@cli.command()
@click.argument('mode', nargs=1, type=click.Choice(['update', 'replace']))
@click.option('-r', "--template-repo", default="",
              help="Name of template repo")
@click.option("-a", "--all-repos", is_flag=True, help="If you want all repos")
@click.option("-d", "--dry-run", is_flag=True, help="If you want dry run")
@click.option("-v", "--verbose", is_flag=True, help="Show additional output.")
@click.option("-q", "--quiet", is_flag=True, help="Dont show additional output.")
@click.pass_context
def run(ctx, mode, **configuration):
    session = ctx.obj['session']
    config = ctx.obj['config_file']
    is_quiet = configuration['quiet']
    is_verbose = configuration['verbose']

    config_file = configparser.ConfigParser()
    config_file.optionxform = str
    if not config_file.read(config):
        exit(3)

    if 'repos' not in config_file:
        # if not is_quiet:
        click.echo("No repositories specification has been found")
        exit(7)

    if not config_file['repos']:
        click.echo("SUMMARY: 0 repo(s) updated successfully")
        exit(0)

    if 'labels' not in config_file:
        # if not is_quiet:
        click.echo("No labels specification has been found")
        exit(6)

    repos = []
    config_repos = config_file['repos']
    for key in config_repos:
        if config_file['repos'].getboolean(key):
            repos.append(key)

    if configuration['all_repos']:
        repos = get_all_repos(session)
        repos = parse_repos(repos)

    all_errors = 0
    all_success = 0

    new_labels = config_file['labels']
    if configuration['template_repo']:
        repo_template = configuration['template_repo']
        all_labels_template = get_all_labels(session, repo_template)
        new_labels = parse_labels(all_labels_template)

    # print(len(new_labels))
    if mode == "replace" and not config_file['labels']:
        for repo in repos:
            repo_name = repo
            all_repo_labels = labels_for_run(session, repo_name, is_quiet, is_verbose)
            parsed_labels = parse_labels(all_repo_labels)
            for key in parsed_labels:
                delete_label(session, repo_name, key, "", configuration)

    else:
        for repo in repos:
            repo_name = repo
            all_repo_labels = labels_for_run(session, repo_name, is_quiet, is_verbose)
            if all_repo_labels:
                result = analyze_labels_actual_with_new(session, repo_name, all_repo_labels,
                                                        new_labels, configuration, mode)
                all_success = all_success + result[1]
                all_errors = all_errors + result[0]
            else:
                all_errors = all_errors + 1

    if not is_quiet and is_verbose:
        if all_errors > 0:
            click.echo("[SUMMARY] {} error(s) in total, please check log above".format(all_errors))
        else:
            click.echo("[SUMMARY] {} repo(s) updated successfully".format(len(repos)))

    if (is_quiet and is_verbose) or (not is_quiet and not is_verbose):
        if all_errors > 0:
            click.echo("SUMMARY: {} error(s) in total, please check log above".format(all_errors))
        else:
            click.echo("SUMMARY: {} repo(s) updated successfully".format(len(repos)))

    if all_errors > 0:
        exit(10)
    else:
        exit(0)


if __name__ == '__main__':
    cli(obj={})
