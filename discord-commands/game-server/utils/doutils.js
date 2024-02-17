import axios from 'axios'
import {getDOHeaders} from './webutils.js'
import {DO_BASE_URL, DO_DROPLETS_URI} from './constants.js'

export async function getListOfDroplets(){
    const url = DO_BASE_URL+DO_DROPLETS_URI;
    const headers = getDOHeaders();
    const response = await axios.get(url, {headers: headers})
    
    return response;
}