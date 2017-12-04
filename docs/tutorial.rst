Configuration
=================

To initialize the configuration of labelord properly, you first need to initialize your personal access GitHub token and webhook secret (only required when using the web application).

Webhook
--------

Webhooks allow you to build or set up GitHub Apps which subscribe to certain events on GitHub.com. When one of those events is triggered, we'll send a HTTP POST payload to the webhook's configured URL. Webhooks can be used to update an external issue tracker, trigger CI builds, update a backup mirror, or even deploy to your production server. You're only limited by your imagination.

	- head over to the **Settings** page of your repository and click on **Webhooks & services**,
	- click on **Add webhook**,
	- fill the **Payload URL** (the server endpoint that will receive the webhook payload),
	- select **Content type** (we will be working with Application/json),
	- specify your **Webhook secret** (you will need to use this one in the configuration file),
	- choose **Let me select individual events** and **Label** option,
	- when you're finished, click on **Add webhook**.

GitHub token
-------------

**GitHub personal access token** is a unique string, which user can generate in order to authenticate himself during the communication with GitHub API. For **labelord** to work properly, the GitHub token is required. You can generate your own following these steps:

	- navigate to your **GitHub** profile and choose **Settings**,
	- in the left sidebar, click **Developer settings**,
	- in the left sidebar, click **Personal access tokens**,
	- click **Generate new token** (give your token a descriptive name),
	- select the scopes, or permissions, you'd like to grant this token (if you want **labelord** to be able to manage also your private repositories, you need to choose **“Full control of private repositories** permission),
	- when you're finished, click on **Generate token**.


Configuration file
-------------------

The configuration file with sufix ".cfg", which is used to specify the repositories and labels, has to be located in the labelord directory. In this application is path to cofiguration file "./config.cfg" 

You have two option like define the configuration file:

    - using the ``-c/--config`` option when running from CLI
    - specifying the ``LABELORD_CONFIG`` environment variable when running as a web application

Configuration files has to contain these fields:

	- ``[github]``
		- ``token``: your GitHub personal access token.
		- ``webhook_secret``: your webhook secret key to validate all the incoming GitHub webhooks (only required if using the web application).
		
		.. warning:: **Don't forget to keep your token and webhook secret safe and never publish them!**

	- ``[repos]``
		- here, you can specify all of the repositories you want to manage, in the form of GITHUB_USERNAME/REPOSITORY_NAME = on/off.
		- the on/off option specifies if you want to perfom changes in the specified repository or not (can be altered by 1/0).

	- ``[labels]``
		- here, you can specify all of the labels you want to create / edit, in the form of LABEL_NAME = LABEL_COLOR. The label color is specified in the hexadecimal RGB format. One label per line!

	- ``[others]``
		- here, you can specify the "template" repository, which labels will be used as a source of labels instead of the labels specified in [labels] section.
		- form: TEMPLATE_REPO = GITHUB_USERNAME/REPOSITORY_NAME

Example configuration file
---------------------------

::

   [github]
   token = YOUR_TOKEN
   webhook_secret = YOUR_WEBHOOK

   [labels]
   hotFix = FA1111
   Enhancement = FA1111

   [repos]
   tomikeKrasnay/example_project = on
   tomikeKrasnay/example_project_2 = off