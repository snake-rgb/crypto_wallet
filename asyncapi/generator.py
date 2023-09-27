from asyncapi_schema_pydantic import AsyncAPI, ChannelItem, Operation, Info, Message, Components, Tag
from pydantic import BaseModel

# Construct AsyncAPI by pydantic objects
async_api = AsyncAPI(
    asyncapi='2.3.0',
    info=Info(
        title="Socket.IO documentation",
        version="1.0.0",
        description="Auto-Modern socket.io documentation",

    ),
    channels={
        "connect": ChannelItem(
            description="This channel is used for connecting and authenticating users. Send Authorization header with "
                        "Bearer token to be authenticated. debug tokens also works.",
            publish=Operation(
                summary="Connect to server",
            ),

        ),
    },
)

# Asyncapi
# ------------------------------------------
# asyncdocs:
#   python asyncapi/generator.py
#   ag asyncapi_docs.yaml @asyncapi/html-template -o asyncapi_docs
#   python asyncapi/html_fixer.py
#   $(MANAGE) collectstatic --noinput

if __name__ == "__main__":
    json_data = async_api.json(by_alias=True, exclude_none=True, indent=2)

    # recursively delete "oneOf", "anyOf", "allOf", "enum" keys if they are []
    for_delete = ['"oneOf": [],\n', '"anyOf": [],\n', '"allOf": [],\n', '"enum": [],\n']
    for key in for_delete:
        json_data = json_data.replace(key, "")

    # dump to file sample.yaml
    with open("asyncapi_docs.yaml", "w") as f:
        f.write(json_data)
