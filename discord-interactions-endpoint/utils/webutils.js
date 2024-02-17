import nacl from 'tweetnacl';

import {BOT_PUBLIC_KEY} from './constants.js';

export async function verifyEvent(event){
    try {
        console.log('Verifying incoming event...');
        const isVerified = nacl.sign.detached.verify(
            Buffer.from(event['headers']['x-signature-timestamp'] + event.body),
            Buffer.from(event['headers']['x-signature-ed25519'], 'hex'),
            Buffer.from(BOT_PUBLIC_KEY ?? '', 'hex'),
        );
        console.log('Returning verification results...');
        console.log(isVerified);
        return isVerified;
      } catch (exception) {
        console.log(exception);
        return false;
      }
}

export function getHTTPResponse(headers, body, statusCode){
    const response = {};
    if(headers){
        response.headers = headers;
    }

    if(body){
        response.body = body;
    }

    response.statusCode = statusCode ?? '500';

    return response;
}

export function getCommandEvent(body){
    const event = {};
    event.body = body;
    event.key = BOT_PUBLIC_KEY;

    return event;
}