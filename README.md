# techpriest
Search info in telegram and send to telegram

## Prehistory
It is too many channels for search

> Enginseer with proper augmentations   
> (c) Author

Enjoy.

## How to use
Need to fill three files `search_scheme.txt` and `search_places.txt`.



In case you got:

```
{
"ok": false,
"error_code": 400,
"description": "Bad Request: chat not found"
}
```
Initiate: 
`https://api.telegram.org/bot_BOT_TOKEN_/sendMessage?chat_id=_CHAT_ID_&text=START`

For troubleshoot some issues:
`https://api.telegram.org/bot_BOT_TOKEN_/getUpdates`