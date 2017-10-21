# This is skeleton for labelord module
# MI-PYT, task 1 (requests+click)
# File: labelord.py
# TODO: create requirements.txt and install
import click
import flask
import os
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


def labels_for_run(session, repo_name, configuration):
    is_quiet = configuration['quiet']
    is_verbose = configuration['verbose']
    r = session.get('https://api.github.com/repos/' + repo_name + '/labels?per_page=100&page=1')
    if r.status_code == 404:
        if (is_quiet and is_verbose) or (not is_quiet and not is_verbose):
            click.echo("ERROR: LBL; {}; 404 - Not Found".format(repo_name))
            return 0

        if not is_quiet:
            click.echo("[LBL][ERR] {}; 404 - Not Found".format(repo_name))
        return 0

    if r.status_code == 401:
        if not is_quiet:
            click.echo("[LBL][ERR] {}; 401 - Bad credentials".format(repo_name))
        return 0

    result = r.json()
    return result


def print_repos(session):
    json_data = get_all_repos(session)
    for one_repo in json_data:
        click.echo("{}".format(one_repo["full_name"]))
    exit(0)


def get_name_repos(session):
    json_data = get_all_repos(session)
    result_array = []
    for one_repo in json_data:
        result_array.append(one_repo["full_name"])
    return result_array


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


def analyze_labels_with_new(session, repo_name, old_git, new_labels, configuration, mode):
    parsed_git_labels = parse_labels(old_git)
    lowercase_git_labels = [x.lower() for x in parsed_git_labels]
    all_git_labels_name = [x for x in parsed_git_labels]
    lowercase_config_labels = [x.lower() for x in new_labels]

    number_errors = 0
    if mode == "replace":
        # remove all different labels
        labels_for_delete = diff(lowercase_git_labels, lowercase_config_labels)
        for label in labels_for_delete:
            index = lowercase_git_labels.index(label)
            label_name = all_git_labels_name[index]
            # if return value is false, increase errors
            if not delete_label(session, repo_name, label_name, parsed_git_labels[label_name], configuration):
                number_errors = number_errors + 1

    for key in new_labels:
        new_label_name = key
        label_config_name_lower = key.lower()
        label_config_color = new_labels[new_label_name]
        # for each new label analyze if exist
        if label_config_name_lower in lowercase_git_labels:
            # compare git label with new label (update or create)
            errors = compare_git_with_new_label(all_git_labels_name, parsed_git_labels, lowercase_git_labels,
                                               label_config_name_lower, label_config_color, new_label_name,
                                               repo_name, session, configuration)
            # increase errors if was
            number_errors = number_errors + errors
        else:
            # create new label because not exist
            # if return value is false, increase errors
            if not create_label(session, repo_name, new_label_name, label_config_color, configuration):
                number_errors = number_errors + 1

    return number_errors


def compare_git_with_new_label(all_git_labels_name, parsed_git_labels, lowercase_git_labels, label_config_name_lower,
                               label_config_color, new_label_name, repo_name, session, configuration):
    number_errors = 0
    index = lowercase_git_labels.index(label_config_name_lower)
    label_git_name = all_git_labels_name[index]
    if new_label_name in parsed_git_labels:
        # update label because color has been changed
        if label_config_color != parsed_git_labels[new_label_name]:
            # if return value is false, increase errors
            if not update_label(session, repo_name, new_label_name, label_git_name, label_config_color, configuration):
                number_errors = 1
    else:
        # update label because name has been changed
        # if return value is false, increase errors
        if not update_label(session, repo_name, new_label_name, label_git_name,
                            label_config_color, configuration):
            number_errors = 1

    return number_errors


def parse_labels(labels):
    parsed_labels = {}
    for one_label in labels:
        parsed_labels[one_label['name']] = one_label['color']

    return parsed_labels


def parse_repos(repos):
    parsed_repos = []
    for one_repo in repos:
        parsed_repos.append(one_repo['full_name'])
    return parsed_repos


def update_label(session, repo_name, label_name, old_label_name, new_color, configuration):
    return request_run(configuration, session, repo_name, "UPD", old_label_name, label_name, new_color)


def create_label(session, repo_name, label_name, new_color, configuration):
    return request_run(configuration, session, repo_name, "ADD", "", label_name, new_color)


def delete_label(session, repo_name, label_name, color, configuration):
    return request_run(configuration, session, repo_name, "DEL", label_name, "", color)


def request_run(configuration, session, repo_name, method, old_name, new_label_name, new_color):
    is_dry = configuration['dry_run']
    is_quiet = configuration['quiet']
    is_verbose = configuration['verbose']

    if not is_dry:
        if method == "ADD":
            header_data = {"name": new_label_name, "color": new_color}
            url = 'https://api.github.com/repos/' + repo_name + '/labels'
            response = session.post(url, json.dumps(header_data))
            return handle_response(response, configuration, "ADD", 201, repo_name, new_label_name, new_color)
        if method == "DEL":
            url = 'https://api.github.com/repos/' + repo_name + '/labels/' + old_name
            response = session.delete(url)
            return handle_response(response, configuration, "DEL", 204, repo_name, old_name, new_color)
        if method == "UPD":
            header_data = {"name": new_label_name, "color": new_color}
            url = 'https://api.github.com/repos/' + repo_name + '/labels/' + old_name
            response = session.patch(url, json.dumps(header_data))
            return handle_response(response, configuration, "UPD", 200, repo_name, new_label_name, new_color)
    else:
        if not is_quiet and is_verbose:
            if method == "DEL":
                click.echo("[{}][DRY] {}; {}; {}".format(method, repo_name, old_name, new_color))
            else:
                click.echo("[{}][DRY] {}; {}; {}".format(method, repo_name, new_label_name, new_color))
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


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('labelord, version 0.1')
    ctx.exit()


def prepare_session(ctx):
    token = ctx.obj['token']
    config = ctx.obj['config']
    if not token:
        config_name = config
        configparser.optionxform = str
        config_file = configparser.ConfigParser()
        if not config_file.read(config_name):
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
    return ctx


def setup_config(config, is_web):
    config_file = configparser.ConfigParser()
    config_file.optionxform = str

    if not config_file.read(config):
        exit(3)

    if 'repos' not in config_file:
        # if not is_quiet:
        click.echo("No repositories specification has been found")
        exit(7)

    if not is_web:
        if not config_file['repos']:
            click.echo("SUMMARY: 0 repo(s) updated successfully")
            exit(0)

        if 'labels' not in config_file:
            # if not is_quiet:
            click.echo("No labels specification has been found")
            exit(6)

    return config_file


def run_response(configuration, len_repos, all_errors):
    is_quiet = configuration['quiet']
    is_verbose = configuration['verbose']
    if not is_quiet and is_verbose:
        if all_errors > 0:
            click.echo("[SUMMARY] {} error(s) in total, please check log above".format(all_errors))
        else:
            click.echo("[SUMMARY] {} repo(s) updated successfully".format(len_repos))

    if (is_quiet and is_verbose) or (not is_quiet and not is_verbose):
        if all_errors > 0:
            click.echo("SUMMARY: {} error(s) in total, please check log above".format(all_errors))
        else:
            click.echo("SUMMARY: {} repo(s) updated successfully".format(len_repos))

    if all_errors > 0:
        exit(10)
    else:
        exit(0)


def get_repos(config_file, configuration, session):
    repos = []
    config_repos = config_file['repos']
    for key in config_repos:
        if config_file['repos'].getboolean(key):
            repos.append(key)

    if configuration:
        repos = get_all_repos(session)
        repos = parse_repos(repos)

    return repos


def new_labels_from_template(name, session):
    all_labels_template = get_all_labels(session, name)
    return parse_labels(all_labels_template)


def remove_labels_from_all_repos(session, configuration, repos):
    for repo in repos:
        repo_name = repo
        all_repo_labels = labels_for_run(session, repo_name, configuration)
        parsed_labels = parse_labels(all_repo_labels)
        for key in parsed_labels:
            delete_label(session, repo_name, key, "", configuration)

# PUBLIC FUNCTIONS


@click.group('labelord')
@click.pass_context
@click.option('-c', "--config", default="./config.cfg", envvar='LABELORD_CONFIG',
              help="Path of the auth config file.")
@click.option('-t', "--token", envvar='GITHUB_TOKEN',
              help="GitHub API token.")
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help="Show the version and exit.")
def cli(ctx, config, token):
    ctx.obj['token'] = token
    ctx.obj['config'] = config


@cli.command()
@click.pass_context
def list_repos(ctx):
    """Listing accessible repositories."""
    prepare_session(ctx)
    session = ctx.obj['session']
    print_repos(session)


@cli.command()
@click.argument('repository', nargs=1)
@click.pass_context
def list_labels(ctx, repository):
    """Listing labels of desired repository."""
    prepare_session(ctx)
    session = ctx.obj['session']
    print_labels(session, repository)


@cli.command()
@click.argument('mode', nargs=1, type=click.Choice(['update', 'replace']))
@click.option('-r', "--template-repo", default="",
              help="Repository which serves as labels template.")
@click.option("-a", "--all-repos", is_flag=True, help="Run for all repositories available.")
@click.option("-d", "--dry-run", is_flag=True, help="Proceed with just dry run.")
@click.option("-v", "--verbose", is_flag=True, help="Really exhaustive output.")
@click.option("-q", "--quiet", is_flag=True, help="No output at all.")
@click.pass_context
def run(ctx, mode, **configuration):
    """Run labels processing."""
    prepare_session(ctx)
    session = ctx.obj['session']
    config = ctx.obj['config_file']
    config_file = setup_config(config, False)
    repos = get_repos(config_file, ('all_repos' in configuration), session)
    all_errors = 0
    new_labels = config_file['labels']
    # check if exist template repo
    if configuration['template_repo'] or ("others" in config_file):
        if configuration['template_repo']:
            name = configuration['template_repo']
        else:
            name = config_file['others']['template-repo']
        new_labels = new_labels_from_template(name, session)

    if mode == "replace" and not config_file['labels']:
        # remove all labels if is mode replace and labels in config file is empty
        remove_labels_from_all_repos(session, configuration, repos)
    else:
        # analyze each repo in github
        for repo in repos:
            repo_name = repo
            all_repo_labels = labels_for_run(session, repo_name, configuration)
            # analyze each label in repository
            if all_repo_labels != 0:
                result = analyze_labels_with_new(session, repo_name, all_repo_labels,
                                                new_labels, configuration, mode)
                all_errors = all_errors + result
            else:
                all_errors = all_errors + 1

    run_response(configuration, len(repos), all_errors)


#####################################################################
# STARING NEW FLASK SKELETON (Task 2 - flask)

class LabelordWeb(flask.Flask):
    inject_session = None
    ctx = None
    configuration = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can do something here, but you don't have to...
        # Adding more args before *args is also possible
        # You need to pass import_name to super as first arg or
        # via keyword (e.g. import_name=__name__)
        # Be careful not to override something Flask-specific
        # @see http://flask.pocoo.org/docs/0.12/api/
        # @see https://github.com/pallets/flask

    def inject_session(self, session):
        self.inject_session = session
        # # TODO: inject session for communication with GitHub
        # # The tests will call this method to pass the testing session.
        # # Always use session from this call (it will be called before
        # # any HTTP request). If this method is not called, create new
        # # session.
        # ...

    def reload_config(self):
        # TODO: check envvar LABELORD_CONFIG and reload the config
        # Because there are problems with reimporting the app with
        # different configuration, this method will be called in
        # order to reload configuration file. Check if everything
        # is correctly set-up
        ...


# TODO: instantiate LabelordWeb app
# Be careful with configs, this is module-wide variable,
# you want to be able to run CLI app as it was in task 1.
app = LabelordWeb(__name__)


@app.route('/', methods=['POST'])
def post():
    return 'OK'


@app.route('/', methods=['GET'])
def get():
    session = app.inject_session
    config = app.ctx.obj['config_file']
    config_file = setup_config(config, True)
    repos = get_repos(config_file, False, session)
    html_result = "master-to-master" + "<table>"
    for name in repos:
        html_result = html_result + "<tr>" + "<th>" + name + "</th>" + "</tr>"

    html_result = html_result + "</table>"
    return html_result


# TODO: implement web app
# hint: you can use flask.current_app (inside app context)


@cli.command()
@click.option('-h', '--host', default='127.0.0.1',
              help='The interface to bind to.')
@click.option('-p', '--port', default='5000',
              help='The port to bind to.', type=int)
@click.option('-d', '--debug', is_flag=True,
              help='Turns on DEBUG mode.')
@click.pass_context
def run_server(ctx, **configuration):
    """Run master-to-master replication server."""
    debug = configuration['debug']
    port = configuration['port']
    hostname = configuration['host']
    prepare_session(ctx)
    session = ctx.obj['session']
    app.inject_session = session
    app.ctx = ctx
    app.run(debug=debug, host=hostname, port=int(port))


# ENDING  NEW FLASK SKELETON
#####################################################################

if __name__ == '__main__':
    cli(obj={})
