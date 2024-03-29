How to publish schemas
----------------------

1. Ensure `jq` is installed:

    ```bash
    brew install jq
    ```

1. Run the command:

    ```bash
    push.sh <REDPANDA_URL> <API_KEY>
    ```

    where:

    ```text
    <REDPANDA_URL>: URL to connect to RedPanda where the schemas will be uploaded
    <API_KEY>: secret key with write permission for redpanda
    ```

How to remove last schemas created
----------------------------------

Run the command:

```bash
remove_all.sh <REDPANDA_URL> <API_KEY>
```

where:

```text
<REDPANDA_URL>: URL to connect to RedPanda where the schemas will be uploaded
<API_KEY>: secret key with write permission for redpanda
```
