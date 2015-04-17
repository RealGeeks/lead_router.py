
# Client to `lead_router`

Install it

    $ pip install git+ssh://git@github.com/RealGeeks/lead_router.py.git

First get a `user` and `token` from the `lead_router` project, it will
identify your project and which permissions you have.

```python
import leadrouter

client = leadrouter.Client('receivers.leadrouter.realgeeks.com',
                           user='me', token='secret')
```

with a `Client` object created use one the methods bellow:

#### `create_lead(site_uuid, lead)`

Send a new lead.

 - `site_uuid` is a string with the RG2 Site UUID
 - `lead` id a dictionary with lead fields

See [`https://github.com/RealGeeks/lead_router/wiki/Lead-Router-REST-API#post-sitessite-uuidleads`](https://github.com/RealGeeks/lead_router/wiki/Lead-Router-REST-API#post-sitessite-uuidleads)

#### `update_lead(site_uuid, lead_uuid, lead)`

Update an existing lead.

 - `site_uuid` is a string with the RG2 Site UUID
 - `lead_uuid` is a string with the Lead Manager Lead UUID
 - `lead` id a dictionary with lead fields to be overriden

See [`https://github.com/RealGeeks/lead_router/wiki/Lead-Router-REST-API#put-sitessite-uuidleadslead-uuid`](https://github.com/RealGeeks/lead_router/wiki/Lead-Router-REST-API#put-sitessite-uuidleadslead-uuid)

#### `add_activities(site_uuid, lead_uuid, activities)`

Update an existing lead.

 - `site_uuid` is a string with the RG2 Site UUID
 - `lead_uuid` is a string with the Lead Manager Lead UUID
 - `activities` is a list of dictionaries, each dictionary is an activitity

See [`https://github.com/RealGeeks/lead_router/wiki/Lead-Router-REST-API#post-sitessite-uuidleadslead-uuidactivities`](https://github.com/RealGeeks/lead_router/wiki/Lead-Router-REST-API#post-sitessite-uuidleadslead-uuidactivities)

## Exceptions

All methods return `None` on success.  On failure will raise `HTTPError` exception
with a generic error message.

If this exception was raises due to a invalid response from the server, like a 404, 400
or 500 the exception object will have two useful attributes;

 - `status_code`: integer with the response status code
 - `response_text`: original response body as string


# Development

To help with development, first clone and create a virtualenv.  Inside the project folder
run:

    $ pip install -e .

In order to run all tests [`beanstalkd`](http://kr.github.io/beanstalkd/) need to be
running:

    $ brew install beanstalkd
    $ beanstalkd -V
    pid 80350
    bind 4 0.0.0.0:11300

then run tests:

    $ python setup.py test

If you're familiar with py.test custom arguments can be provided:

    $ python setup.py test --pytest-args='-v --tb=short' 
