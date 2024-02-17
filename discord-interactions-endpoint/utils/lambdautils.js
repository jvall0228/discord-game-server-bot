import { LambdaClient, ListFunctionsCommand, ListTagsCommand, InvokeCommand } from "@aws-sdk/client-lambda";

export async function getLambdaFunctions(){
    const client = new LambdaClient({});
    const command = new ListFunctionsCommand({});
    const response = await client.send(command);
    
    return response.Functions;
}

export async function getLambdaFunctionTags(arn){
    const client = new LambdaClient({});
    const command = new ListTagsCommand({Resource: arn});
    const response = await client.send(command);

    return response.Tags ?? {};
}

export async function getLambdaFunctionByCommandName(commandName){
    const funcList = await getLambdaFunctions();

    for(let i = 0; i < funcList.length; i++){
        console.log(funcList[i]);
        const tags = await getLambdaFunctionTags(funcList[i].FunctionArn);
        if(tags['discord-command-name'] === commandName){
            return funcList[i];
        }
    }
    
    return {};
}

export async function invokeLambdaFunction(funcName, event){
    const client = new LambdaClient({});
    const input = {
        FunctionName: funcName,
        InvocationType: "Event",
        LogType: "Tail",
        Payload: JSON.stringify(event),
    };

    const command = new InvokeCommand(input);
    return client.send(command);
}