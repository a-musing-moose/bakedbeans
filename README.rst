Baked Beans
===========

Baked Beans is a terribly named HTTP stub server for REST services that deal in JSON payloads written in Python but easily runnable as a Docker container.

It takes a super simple approach of using a folder of contents that provide the canned responses it produces.

e.g ``GET http://localhost:3000/path/to/some/resource`` would map to the file: ``<base_folder>/path/to/some/resource.get.json``.

Note in the example above that the file name looked for includes the HTTP method used.

In it's basic mode, Baked Beans will simply load the matching file and pipe it back to the client.

It also supports a limited amount of smarts. JSON file constructed to a specific schema can be used by Baked Beans to return specific responses. For example, it can match responses based on GET parameters.


Installation
------------

Create a python virtual environment with your favourite tools. Then use pip to install ``bakedbeans``:

.. code-block:: bash

    (venv) $ pip install bakedbeans


Running
-------

Baked Beans provides a simple command line executable to run the server:

.. code-block:: bash

    (venv) $ baked /path/to/contents/folder
     * Running on http://127.0.0.1:3000/ (Press CTRL+C to quit)


You can specify the host name with ``--host`` and the port it binds to with ``--port``.

Baked Beans is also built with Docker in mind. To run Baked Beans in docker you will need to mount your local contents directory as a volume.  For example:

.. code-block:: bash
    docker run -it --rm -p 3000:3000 -v /full/path/to/contents:/contents moose/bakedbeans

This will run Baked Beans in a container that will remove itself once exit, mounting the ``/full/path/to/contents`` inside the container at ``/contents`` which is where Baked Beans is configured to load the contents from.

Writing contents
-----------------

Baked Beans maps URLs to file paths, adding ``.<method>.json`` to the end of the path. There are a couple of exceptions, for example if the URL ends with ``/`` it will instead add ``index.<method>.json``.

Examples:

    +-------------------------------------+--------------------------------+
    | Request URL                         | Mapped Path                    |
    +=====================================+================================+
    | GET http://localhost:3000/somewhere |  ``<base>/somewhere.get.json`` |
    +-------------------------------------+--------------------------------+
    | POST http://localhost:3000/another  |  ``<base>/another.post.json``  |
    +-------------------------------------+--------------------------------+
    | GET http://localhost:3000/          |  ``<base>/index.get.json``     |
    +-------------------------------------+--------------------------------+

By default the contents of the file once loaded to feed back to the request verbatim.

However, if you want to get clever with the response you can write the JSON file in the ``bean`` format. ``Beans`` are just something I made up for this project and take the form of a JSON object. For example:


.. code-block:: javascript

    {
        "_bean": true,
        "responses": [
            {
                "params": {
                    "product": "1111"
                },
                "contents": {
                    "id": 1111,
                    "name": "Product A"
                }
            },
            {
                "params": {
                    "product": "2222"
                },
                "status": 203,
                "contents": {
                    "id": 2222,
                    "name": "Product B"
                }
            }


        ]

    }


With the ``bean`` above, it is matching the response based on the GET parameters that accompany the request.  e.g. ``http://localhost:3000/path?product=1111`` would match the first response and return the value of ``contents``. A GET param of ``product=2222`` would match the second. If no match is found, then the first one is selected regardless.

Note also that the second response specifies a ``status``, this allow you to specify a specific status code to use for the response. If not specified then a default value based on the HTTP method is used.

The default status codes are:

+---------+------+
| Method  | Code |
+=========+======+
| GET     |  200 |
+---------+------+
| POST    |  201 |
+---------+------+
| DELETE  |  204 |
+---------+------+
| PUT     |  200 |
+---------+------+
| PATCH   |  200 |
+---------+------+
| <OTHER> |  200 |
+---------+------+

Currently only GET parameter matching is supported but header and body matching would be a nice addition as would regex of values and use of matched criteria within the content...


Hits & Misses
-------------

The above describes have things work if everything is perfect. The url matches a content file, the content file is valid JSON, and if needed a valid ``bean``.  But what happens when things don't match up:

Content not found
    ``404`` status with a body of ``{"error": "content not found the/missing/path"}``

Invalid content file
    ``500`` status with a body of ``{"error": "content invalid"}``

Bean fails validation
    ``500`` status with a body of ``{"error": "This is one mouldy bean"}``


More detailed descriptions of the error encountered can be found in the logs.



