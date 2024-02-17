import {getLambdaFunctionByCommandName, invokeLambdaFunction} from './lambdautils.js'

export async function handleCommand(commandName, event){
    const func = await getLambdaFunctionByCommandName(commandName);
    await invokeLambdaFunction(func.FunctionName, event);
}