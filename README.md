
# Python client to Real Geeks Leads API

Install it

    $ pip install leadrouter

First get a `user` and `token` from the `lead_router` project, it will identify your project and which permissions you have.

If you're a Real Geeks client write a message to [support](https://www.realgeeks.com/support/) asking for credentials for the Incoming Leads API for your site.

```python
import leadrouter

client = leadrouter.Client('receivers.leadrouter.realgeeks.com',
                           user='me', token='secret')
```

with a `Client` object created use one the methods below. For details on which fields you can send for `lead` and `activities` check our [documentation](https://developers.realgeeks.com/incoming-leads-api/)

#### `create_lead(site_uuid, lead)`

Send a new [lead](https://developers.realgeeks.com/leads/).

 - `site_uuid` is a string with the RG2 Site UUID
 - `lead` id a dictionary with lead fields

#### `update_lead(site_uuid, lead_uuid, lead)`

Update an existing lead.

 - `site_uuid` is a string with the RG2 Site UUID
 - `lead_uuid` is a string with the Lead Manager Lead UUID
 - `lead` id a dictionary with lead fields to be overriden

#### `add_activities(site_uuid, lead_uuid, activities)`

Add [activities](https://developers.realgeeks.com/activities/) to an existing lead.

 - `site_uuid` is a string with the RG2 Site UUID
 - `lead_uuid` is a string with the Lead Manager Lead UUID
 - `activities` is a list of dictionaries, each dictionary is an activitity

#### `create_potential_seller_lead(site_uuid, lead)`

Send a new potential seller lead.  Somebody who attempted to view a property valuation but didn't sign-up to give contact details. So all we have is the property they looked at.

 - `site_uuid` is a string with the RG2 Site UUID
 - `lead` id a dictionary with lead fields

## Exceptions

All methods return `None` on success.  On failure will raise `HTTPError` exception
with a generic error message.

If this exception was raises due to a invalid response from the server, like a 404, 400
or 500 the exception object will have two useful attributes;

 - `status_code`: integer with the response status code
 - `response_text`: original response body as string

## Async send

We have a client implementation that instead of sending requests directly just put them in a queue to be sent asynchronously, it's the `Publisher` and `subscriber`.

First, you will need to install the `beanstalkc` and `pyyaml` client libraries from pip (optional dependencies)

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

### Resend jobs from async client

When you use the Async send feature above sometimes a job could fail, most times it will retry but 
errors like validation errors will not retry. First look for the JSON body of a job, it will be
logged and sent to Sentry. It looks like this:

```json
{
	"parsed_job_body": {
		"host": "receivers.leadrouter.realgeeks.com",
		"params": {
			"lead_uuid": "8bac1437ad7b5433b248ebe8bf708b24",
			"site_uuid": "089df7bf-db46-4453-b29a-6b02700c4426",
			"activities": [{
				"source": "My App",
				"type": "property_viewed",
				"property": {"full_baths": 2.5},
				"created": "2019-02-06T21:19:51.284522+00:00"
			}]
		},
		"method": "add_activities",
		"auth": ["User", "Password"]
	},
	"retry": false,
	"log_level": "ERROR",
	"job_id": 1005832440,
	"log_message": "send failed: Property field 'full_baths' is not a valid integer.",
	"response_status": 422,
	"response_body": "{\"error\": \"Property field 'full_baths' is not a valid integer.\"}\n",
	"traceback": ""
}
```

Note how it failed to send to the `lead_router` due to a validation error, these errors will not
retry. Now save this json in a file `job.json`, modify the body to fix it and resend with:

    $ leadrouter send job.json

### Deployment

If you want to use Async Send there is a docker image, `quay.io/realgeeks/leadrouter_subscriber`. Set the following environment variables:
  * `BEANSTALK_HOST`
  * `BEANSTALK_PORT`
  * `BEANSTALK_TUBE`
  * `LOGLEVEL`

# Development [virtualenv]

To help with development, first clone and create a virtualenv. Inside the project folder
run:

    $ pip install -e .

In order to run all tests [`beanstalkd`](http://kr.github.io/beanstalkd/) need to be
running:

    $ brew install beanstalkd
    $ beanstalkd -V
    pid 80350
    bind 4 0.0.0.0:11300

then run tests:

    $ pip install tox
    $ tox

If you're familiar with py.test custom arguments can be provided. This way you can run specific
tests in a specific environment:

    $ source .tox/py26/bin/activate
    $ python setup.py test --pytest-args='-v --tb=short' 

# Development [Docker]
To build your docker environment, run: 

    $ docker-compose build

Now, open a shell in the docker container:

    $ docker-compose run leadrouter_subscriber bash

then run tests:

    root@container-sha:/usr/src/app# tox

It will calculate the coverage, if you want to view the coverage report
in html, use:

    $ coverage html  # you need to 'pip install coverage' first
    $ open htmlcov/index.html

Upload version to pypi:

    $ python setup.py sdist
    $ twine upload dist/*
