import json
from datetime import datetime
from typing import Optional
from uuid import UUID

from asyncapi_schema_pydantic import (  # noqa
    AsyncAPI,
    Info,
    ChannelItem,
    Operation,
    Message,
    ChannelBindings,
    AmqpChannelBinding,
    AmqpQueue,
    Components,
    Tag, WebSocketsChannelBinding
)
from pydantic import BaseModel, EmailStr


class AsyncSchema:

    @classmethod
    def async_schema(cls, **kwargs):
        """
        Return async schema.
        """
        schema = cls.schema()
        schema.pop("definitions", None)
        schema_str = json.dumps(schema)
        schema_str = schema_str.replace("#/definitions/", "#/components/schemas/")
        return json.loads(schema_str)


class Disconnect(BaseModel, AsyncSchema):
    detail: str


class ChatMessage(BaseModel, AsyncSchema):
    text: str
    image: Optional[str] = None
    user_id: UUID


class User(BaseModel, AsyncSchema):
    id: UUID
    username: str
    email: EmailStr
    profile_image: Optional[str] = None


class AccessToken(BaseModel, AsyncSchema):
    access_token: str


# Construct AsyncAPI by pydantic objects
async_api = AsyncAPI(
    asyncapi='2.3.0',
    info=Info(
        title="Socket.IO documentation",
        version="1.0.0",
        description="Crypto Wallet socket.io documentation",

    ),
    servers={
        "rabbitmq": {
            "url": "amqp://localhost:5672",
            "protocol": "amqp",
            "protocolVersion": "0.9.1",
            "description": "RabbitMQ development server",
        },
        "socketio": {
            "url": "http://0.0.0.0:8001/socket.io",
            "protocol": "wss",
            "protocolVersion": "5",
            "description": "Socketio development server",
        },
    },
    channels={
        "disconnect": ChannelItem(
            description="This channel is used for disconnecting users and delete them from list of"
                        " online users and leave chat_room, emit event about user who leave from room",
            bindings=ChannelBindings(
                ws=WebSocketsChannelBinding(),
            ),
            publish=Operation(
                summary="User disconnect from chat.",
                message={
                    "$ref": "#/components/messages/DisconnectData",
                },
            ),
        ),
        "join_chat": ChannelItem(
            description="This channel is used for send list of online users to client and save user data in session",
            bindings=ChannelBindings(
                ws=WebSocketsChannelBinding(),
            ),
            publish=Operation(
                summary="Send list of online users and connect user to chat room",
                message={
                    "$ref": "#/components/messages/UserInfo",
                },
            ),
            subscribe=Operation(
                summary="Receive user access token",
                message={
                    "$ref": "#/components/messages/UserToken",
                },
            ),
        ),
        "send_message": ChannelItem(
            description="This channel is used for send message data to all online users",
            bindings=ChannelBindings(
                ws=WebSocketsChannelBinding(),
            ),
            publish=Operation(
                summary="User send message to room chat",
                message={
                    "$ref": "#/components/messages/DisconnectData",
                },
            ),
            subscribe=Operation(
                summary="User send message to server then server resend this message to all in room",
                message={
                    "$ref": "#/components/messages/DisconnectData",
                },
            ),
        ),

    },
    components=Components(
        messages={
            "DisconnectData": Message(
                name="DisconnectData",
                title="Disconnect user",
                summary="Action for disconnect user from server",
                description="Disconnect user from server and print success disconnect,"
                            " delete user from list of online users",
                contentType="application/json",
                tags=[
                    Tag(name="Disconnect User")
                ],
                payload={
                    "$ref": "#/components/schemas/Disconnect",
                },
            ),
            "SendMessage": Message(
                name="SendMessage",
                title="Send Message",
                summary="Action to get new messages.",
                description="Get new messages in chat",
                contentType="application/json",
                tags=[
                    Tag(name="Send Message"),
                ],
                payload={
                    "$ref": "#/components/schemas/ChatMessage",
                },
            ),
            "UserInfo": Message(
                name="UserInfo",
                title="User Info",
                summary="Action to got a list of online users info.",
                description="Get info about all online users",
                contentType="application/json",
                tags=[
                    Tag(name="User"),
                    Tag(name="Additional Info"),
                ],
                payload={
                    "$ref": "#/components/schemas/User",
                },
            ),
            "UserToken": Message(
                name="UserToken",
                title="User Token",
                summary="Auth user",
                description="Verify token and auth user in chat",
                contentType="application/json",
                tags=[
                    Tag(name="UserToken"),
                ],
                payload={
                    "$ref": "#/components/schemas/AccessToken",
                },
            ),
        },
        schemas={
            "User": User.async_schema(),
            "ChatMessage": ChatMessage.async_schema(),
            "Disconnect": Disconnect.async_schema(),
            "AccessToken": AccessToken.async_schema(),
        },
    )
)

if __name__ == "__main__":
    json_data = async_api.json(by_alias=True, exclude_none=True, indent=2)

    # recursively delete "oneOf", "anyOf", "allOf", "enum" keys if they are []
    for_delete = ['"oneOf": [],\n', '"anyOf": [],\n', '"allOf": [],\n', '"enum": [],\n']
    for key in for_delete:
        json_data = json_data.replace(key, "")

    # dump to file sample.yaml
    with open("asyncapi_docs.yaml", "w") as f:
        f.write(json_data)
