# Pingdom

This page contains the setup guide and reference information for the [Pingdom](https://docs.pingdom.com/api/) source

## Prerequisites

Api key (which acts as bearer token) is mandate for this connector to work, It could be generated from the dashboard settings (ref - https://my.pingdom.com/app/api-tokens). 

## Setup guide

### Step 1: Set up Pingdom connection

- Generate an API key (Example: 12345)
- Params (If specific info is needed)
- Available params
    - api_key: The api token

## Step 2: Set up the Pingdom connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Pingdom connector and select **Pingdom** from the Source type dropdown.
4. Enter your `api_key`.
5. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `api_key`.
5. Click **Set up source**.

## Supported sync modes

The Pingdom source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- credits
- maintenance
- maintenance.occurences
- reference_countries
- reference_datetimeformats
- reference_numberformats
- reference_phonecodes
- reference_regions
- reference_timezones
- probes

## API method example

GET https://api.pingdom.com/api/3.1/actions

## Performance considerations

Pindom [API reference](https://api.pingdom.com/api/3.1/) has v3 at present. The connector as default uses v3.1.

## Changelog

| Version | Date       | Pull Request                                           | Subject        |
| :------ | :--------- | :----------------------------------------------------- | :------------- |
| 0.1.0   | 2023-04-10 | [Init](https://github.com/airbytehq/airbyte/pull/)| Initial commit |