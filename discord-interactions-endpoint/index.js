import {verifyEvent, getHTTPResponse, getCommandEvent} from './utils/webutils.js'
import {handleCommand} from './utils/botutils.js'


export async function handler(event, context, callback){
    console.log("Received Event:");
    console.log(JSON.stringify(event));
    const verifyPromise = verifyEvent(event);
    const body = JSON.parse(event.body ?? '{}');

    if (event) {
        switch (body.type) {
          case 1:
            if (await verifyPromise) {
              return getHTTPResponse(null, JSON.stringify({ "type": 1}), 200);
            }
            break;
          case 2:
            if (await verifyPromise) {
              const commandName = body.data ? body.data.name : '';
              await handleCommand(commandName, getCommandEvent(body));
              return getHTTPResponse(null, JSON.stringify({ "type": 5}), 200);
            }
        }
    }
    
    return getHTTPResponse(null, JSON.stringify('invalid request signature'), 401);
}