# MockAPI Destination

This is the repository for the MockAPI destination connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/destinations/mockapi).

## Local development

### Prerequisites
**To iterate on this connector, make sure to complete this prerequisites section.**

#### Minimum Python version required `= 3.9`

#### Build & Activate Virtual Environment and install dependencies
From this connector directory, create a virtual environment:
```
python -m venv .venv
```

This will generate a virtualenv for this module in `.venv/`. Make sure this venv is active in your
development environment of choice. To activate it from the terminal, run:
```
source .venv/bin/activate
pip install -r requirements.txt
```

#### Create credentials
Create a `secrets/config.json` file with your MockAPI configuration:
```json
{
  "api_url": "https://your-project-id.mockapi.io/api/v1"
}
```

### Locally running the connector
```
python main.py spec
python main.py check --config secrets/config.json
python main.py write --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Locally running the connector docker image

#### Build
First, make sure you build the latest Docker image:
```
docker build . -t airbyte/destination-mockapi:dev
```

#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/destination-mockapi:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-mockapi:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/destination-mockapi:dev write --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

## Testing
Make sure to familiarize yourself with [pytest test discovery](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery) to know how your test files and methods should be named.

First install test dependencies into your virtual environment:
```
pip install .[tests]
```

### Unit Tests
To run unit tests locally, from the connector directory run:
```
python -m pytest unit_tests
```

## Testing

You can run full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):

```bash
airbyte-ci connectors --name=destination-motherduck build
```

```bash
airbyte-ci connectors --name=destination-motherduck test
```

### Integration Tests
There are two types of integration tests: Acceptance Tests and custom integration tests.

#### Custom Integration tests
Place custom tests inside `integration_tests/` folder, then, from the connector directory, run
```
python -m pytest integration_tests
```

#### Acceptance Tests
Customize `acceptance-test-config.yml` file to configure tests. See [Connector Acceptance Tests](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference) for more information.

If this is a community connector, please make sure to use the latest version of the [Airbyte CDK](https://docs.airbyte.com/connector-development/cdk-python) and set the `acceptance_tests.connection.tests` to `basic_read` only.

To run acceptance tests locally, from the connector directory, run
```
python -m pytest integration_tests -p integration_tests.acceptance
```

### Using gradle to run tests
All commands should be run from airbyte project root.
To run unit tests:
```
./gradlew :airbyte-integrations:connectors:destination-mockapi:unitTest
```
To run acceptance tests:
```
./gradlew :airbyte-integrations:connectors:destination-mockapi:integrationTest
```

## Dependency Management
All of this connector's dependencies should go in `setup.py`, NOT `requirements.txt`. The requirements file is only used to connect internal Airbyte dependencies in the monorepo for local development.

We split dependencies between two groups, dependencies that are:
- required for your connector to work need to go to `MAIN_REQUIREMENTS` list.
- required for the testing need to go to `TEST_REQUIREMENTS` list

### Publishing a new version of the connector
You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?
1. Make sure your changes are passing unit and integration tests.
1. Bump the connector version in `metadata.yaml`: increment the `dockerImageTag` value. Please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors).
1. Make sure the `metadata.yaml` content is up to date.
1. Make the connector documentation and its changelog is up to date (`docs/integrations/destinations/mockapi.md`).
1. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
1. Pat yourself on the back for being an awesome contributor.
1. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.