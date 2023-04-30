# Eventbrite

This page contains the setup guide and reference information for the [Eventbrite](https://www.eventbrite.com/platform/api#/introduction/about-our-api) source

## Prerequisites

Access Token (which acts as bearer token) is mandate for this connector to work, We could get ot via cURL call, see (Bearer ref - https://www.eventbrite.com/platform/api#/introduction/authentication) 

## Setup guide

### Step 1: Set up Eventbrite connection

- Get your bearer token on keys section (ref - https://www.eventbrite.com/platform/api#/introduction/authentication)
- Setup params (All params are required)
- Available params
    - start_date: Date filter for eligible streams

## Step 2: Set up the Eventbrite connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the eventbrite connector and select **Eventbrite** from the Source type dropdown.
4. Enter your `account_token, api_token and start_date`.
5. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `account_token, api_token and start_date`.
5. Click **Set up source**.

## Supported sync modes

The Eventbrite source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- categories

## API method example

GET https://www.eventbriteapi.com/v3/categories/

## Performance considerations

Eventbrite [API reference](https://www.eventbriteapi.com/v3/) has v3 at present. The connector as default uses v3.

## Changelog

| Version | Date       | Pull Request                                           | Subject        |
| :------ | :--------- | :----------------------------------------------------- | :------------- |
| 0.1.0   | 2023-04-20 | [Init](https://github.com/airbytehq/airbyte/pull/)| Initial commit |