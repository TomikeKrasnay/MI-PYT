Examples
=========

If you wonder how certain methods work, here you can see some examples, tested thanks to doctest just for you.

Parsing the labels from GitHub JSON
------------------------------------

All data from GitHub API are in JSONs format. This app parsed JSON like this:

.. testsetup::


    from labelord.helper import get_labels_from_json
    json = [{"id": 208045946, "url": "https://api.github.com/repos/octocat/Hello-World/labels/bug", "name": "bug", "color": "f29513", "default": "true"}, {"id": 208045947, "url": "https://api.github.com/repos/octocat/Hello-World/labels/enhancement", "name": "enhancement", "color": "84b6eb", "default": "true"}, {"id": 208045948, "url": "https://api.github.com/repos/octocat/Hello-World/labels/question", "name": "question", "color": "cc317c", "default": "true"}]

.. testcode::

    labels = get_labels_from_json(json)
    print(labels)


.. testoutput::

    {'bug': 'f29513', 'enhancement': '84b6eb', 'question': 'cc317c'}