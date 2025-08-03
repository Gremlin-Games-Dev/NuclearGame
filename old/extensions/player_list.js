class PlayerExtension {
    constructor() {
        this.basePlayerUrl = "http://localhost:5000";
    }

    getInfo() {
        return {
            id: "playerExtension",
            name: "Player List",
            blocks: [
                {
                    opcode: "setServerUrl",
                    blockType: "command",
                    text: "PlayerList: Set server URL to [URL]",
                    arguments: {
                        URL: {
                            type: "string",
                            defaultValue: "http://localhost:5000"
                        }
                    }
                },
                {
                    opcode: "listFiles",
                    blockType: "reporter",
                    text: "List files in folder [FOLDER]",
                    arguments: {
                        FOLDER: {
                            type: "string",
                            defaultValue: "room1"
                        }
                    }
                }
            ]
        };
    }

    setServerUrl(args) {
        this.basePlayerUrl = args.URL;
    }

    async listFiles(args) {
        const { FOLDER } = args;
        const url = `${this.basePlayerUrl}/list-files?folder=${encodeURIComponent(FOLDER)}`;
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            if (data.error) {
                return `Error: ${data.error}`;
            }
            return data.files.join(", ");
        } catch (error) {
            return `Error: ${error.message}`;
        }
    }
}

Scratch.extensions.register(new PlayerExtension());