
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

See [`https://github.com/RealGeeks/lead_router/wiki/Incoming-API#post-sitessite_uuidleads`](https://github.com/RealGeeks/lead_router/wiki/Incoming-API#post-sitessite_uuidleads)

#### `update_lead(site_uuid, lead_uuid, lead)`

Update an existing lead.

 - `site_uuid` is a string with the RG2 Site UUID
 - `lead_uuid` is a string with the Lead Manager Lead UUID
 - `lead` id a dictionary with lead fields to be overriden

See [`https://github.com/RealGeeks/lead_router/wiki/Incoming-API#patch-sitessite_uuidleadslead_uuid`](https://github.com/RealGeeks/lead_router/wiki/Incoming-API#patch-sitessite_uuidleadslead_uuid)

#### `add_activities(site_uuid, lead_uuid, activities)`

Add activities to an existing lead.

 - `site_uuid` is a string with the RG2 Site UUID
 - `lead_uuid` is a string with the Lead Manager Lead UUID
 - `activities` is a list of dictionaries, each dictionary is an activitity

See [`https://github.com/RealGeeks/lead_router/wiki/Incoming-API#postsitessite_uuidleadslead_uuidactivities`](https://github.com/RealGeeks/lead_router/wiki/Incoming-API#postsitessite_uuidleadslead_uuidactivities)

#### `create_potential_seller_lead(site_uuid, lead)`

Send a new potential seller lead.  Somebody who attempted to view a property valuation but didn't sign-up to give contact details. So all we have is the property they looked at.

 - `site_uuid` is a string with the RG2 Site UUID
 - `lead` id a dictionary with lead fields

See [`https://github.com/RealGeeks/lead_router/wiki/Incoming-API#post-sitessite_uuidpotential-seller-leads`](https://github.com/RealGeeks/lead_router/wiki/Incoming-API#post-sitessite_uuidpotential-seller-leads)

## Exceptions

All methods return `None` on success.  On failure will raise `HTTPError` exception
with a generic error message.

If this exception was raises due to a invalid response from the server, like a 404, 400
or 500 the exception object will have two useful attributes;

 - `status_code`: integer with the response status code
 - `response_text`: original response body as string


## Async send

We have a client implementation that instead of sending requests directly just put them in a queue to be sent asynchronously, it's the `Publisher` and `subscriber`.

Use `Publisher` the same way you would use `Client`:

```python
import leadrouter

client = leadrouter.Publisher('receivers.leadrouter.realgeeks.com',
                              user='me', token='secret')
```

extra arguments could be given to customize the `beanstalkd` address and tube to use: `beanstalkd_host`, `beanstalkd_port`, `beanstalkd_tube`.

To consume the queue and actually make requests use:

    $ leadrouter subscriber

make sure it's using the same `beanstalkd` and same tube. The defaults should just work.

There is also a `DebugPublisher` available for development.  If you have a project using `Publisher` but don't want to use `beanstalkd` locally, it will record all method calls in a file for debugging.

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

It will calculate the coverage, if you want to view the coverage report
in html, use:

    $ coverage html  # you'll probably need to 'pip install coverage' first
    $ open htmlcov/index.html

# Production

Each rg2 server has a `leadrouter subscriber` running, and there is a beanstalkd
for each server.  See [config in rg2](https://github.com/RealGeeks/rg2/blob/master/server_config/supervisord.conf)

We have [graphs of leadrouter tube on beanstalkd](http://grafana.rg-infrastructure.com/dashboard/db/beanstalk-rg2-lead-router)

[Sentry errors](https://app.getsentry.com/realgeeks/lead-router-subscriber/). 
If the error has job as JSON you can send resend this job manually:

    $ leadrouter send --help

Since rg2 is currently installing this project from master (see rg2 requirements.txt) to
deploy you can just push to master then run (from server_config):

    $ fab production web.upgrade_leadrouter
    $ fab production web.restart_leadrouter_subscriber
