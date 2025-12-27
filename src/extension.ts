import * as path from 'path';
import * as vscode from 'vscode';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind
} from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('hals');
    const pythonPath = config.get<string>('pythonPath', 'python');
    let serverPath = config.get<string>('serverPath', '');

    if (!serverPath) {
        serverPath = context.asAbsolutePath(path.join('hals_lsp_server.py'));
    }

    const serverOptions: ServerOptions = {
        command: pythonPath,
        args: [serverPath],
        transport: TransportKind.stdio
    };

    const clientOptions: LanguageClientOptions = {
        documentSelector: [{ scheme: 'file', language: 'hals' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.{hal,hals}')
        },
        outputChannelName: 'HAL/S Language Server'
    };

    client = new LanguageClient(
        'halsLanguageServer',
        'HAL/S Language Server',
        serverOptions,
        clientOptions
    );

    client.start();

    context.subscriptions.push(
        vscode.commands.registerCommand('hals.restartServer', async () => {
            await client.stop();
            client.start();
            vscode.window.showInformationMessage('HAL/S Language Server restarted');
        })
    );
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
