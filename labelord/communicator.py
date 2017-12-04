import requests
import hashlib
import hmac

###############################################################################
# GitHub API communicator
###############################################################################


class GitHubError(Exception):
    """This exception is thrown when is error with the GitHub connection.

    Attributes:
        status_code (int): The status code from the response.
        message (str): Error message from the response.

    """
    def __init__(self, response):
        self.status_code = response.status_code
        self.message = response.json().get('message', 'No message provided')

    def __str__(self):
        return 'GitHub: ERROR {}'.format(self.code_message)

    @property
    def code_message(self, sep=' - '):
        return sep.join([str(self.status_code), self.message])


class GitHub:
    """This class is for connection with GitHub.

    Attributes:
        token (str): The token to be used for authorization with GitHub.
        session (Session): A Requests session to be used to send and receive data from GitHub API.

    """
    GH_API_ENDPOINT = 'https://api.github.com'

    def __init__(self, token, session=None):
        """Default constructor, define all class variables

        """
        self.token = token
        self.set_session(session)

    def set_session(self, session):
        """Sets the session and authorizes it for communicate with GitHub API.

        Args:
            session (Session): A Requests session.

        """
        self.session = session or requests.Session()
        self.session.auth = self._session_auth()

    def _session_auth(self):
        """Updates session's headers to authenticate with GitHub API.

        Returns:
            auth_function: authorization function.
        """
        def github_auth(req):
            req.headers = {
                'Authorization': 'token ' + self.token,
                'User-Agent': 'Python/Labelord'
            }
            return req
        return github_auth

    def _get_raising(self, url, expected_code=200):
        """Returns a response or raises a GitHubError in case the status code isn't equal with code what expected.

        Args:
            url (str): The URL address where send request.
            expected_code (int): Status code which is expected from the request.

         Raises:
            GitHubError: If the status code isn't equal with expected_code.

        Returns:
            Response: A Requests response.

        """
        response = self.session.get(url)
        if response.status_code != expected_code:
            raise GitHubError(response)
        return response

    def _get_all_data(self, resource):
        """Gets all data spread across multiple pages

        This method may make multiple requests for multiple pages of data.

        Args:
            resource (str): The desired API resource.

        Yields:
            str: A JSON string representing data.

        """
        response = self._get_raising('{}{}?per_page=100&page=1'.format(
            self.GH_API_ENDPOINT, resource
        ))
        yield from response.json()
        while 'next' in response.links:
            response = self._get_raising(response.links['next']['url'])
            yield from response.json()

    def list_repositories(self):
        """Get list of names of accessible repositories (including owner)

        Returns:
                list of str: The full names of each repository.

        """
        data = self._get_all_data('/user/repos')
        return [repo['full_name'] for repo in data]

    def list_labels(self, repository):
        """Get dict of labels with colors for given repository slug

        Returns:
            dictionary where key and value is str: A mapping of color to each label in the given repository.

        """
        data = self._get_all_data('/repos/{}/labels'.format(repository))
        return {l['name']: str(l['color']) for l in data}

    def create_label(self, repository, name, color, **kwargs):
        """Create new label in given repository.

        Args:
            repository (str): Name of repository.
            name (str): Name of label.
            color (str): Color of new label.

        """
        data = {'name': name, 'color': color}
        response = self.session.post(
            '{}/repos/{}/labels'.format(self.GH_API_ENDPOINT, repository),
            json=data
        )
        if response.status_code != 201:
            raise GitHubError(response)

    def update_label(self, repository, name, color, old_name=None, **kwargs):
        """Update existing label in given repository.

        Args:
            repository (str): Name of repository.
            name (str): Name of new label.
            color (str): Color of new label.
            old_name (str): Name of old label.

        """
        data = {'name': name, 'color': color}
        response = self.session.patch(
            '{}/repos/{}/labels/{}'.format(
                self.GH_API_ENDPOINT, repository, old_name or name
            ),
            json=data
        )
        if response.status_code != 200:
            raise GitHubError(response)

    def delete_label(self, repository, name, **kwargs):
        """Delete existing label in given repository.

        Args:
            repository (str): Name of repository.
            name (str): Name of label to be deleted.

        """
        response = self.session.delete(
             '{}/repos/{}/labels/{}'.format(
                 self.GH_API_ENDPOINT, repository, name
             )
        )
        if response.status_code != 204:
            raise GitHubError(response)

    @staticmethod
    def webhook_verify_signature(data, signature, secret, encoding='utf-8'):
        """Verifies the signature from webhook if is correct.

        More details on https://developer.github.com/webhooks/securing/.

        Args:

            data (str): Data for verification.
            signature (str): Signature.
            secret (str): Application's GitHub API secret.
            encoding (str): Encoding of the secret.

        """
        h = hmac.new(secret.encode(encoding), data, hashlib.sha1)
        return hmac.compare_digest('sha1=' + h.hexdigest(), signature)
