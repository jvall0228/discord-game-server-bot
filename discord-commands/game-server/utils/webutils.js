import {DO_ACCESS_TOKEN} from './constants.js'

export function getDOHeaders(){
    const headers = {};
    headers['Authorization'] = 'Bearer '+DO_ACCESS_TOKEN;
    headers['Content-Type'] = 'application/json';
    return headers;
}