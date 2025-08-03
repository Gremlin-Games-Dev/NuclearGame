class ServerExtension {
    constructor() {
        this.baseUrl = "http://localhost:5000";
        this.socket = new WebSocket(this.baseUrl.replace("http", "ws"));
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (this.pendingRequests[data.event]) {
                this.pendingRequests[data.event](data.payload);
                delete this.pendingRequests[data.event];
            }
        };
        this.pendingRequests = {};
    }

    getInfo() {
        return {
            id: "serverExtension",
            name: "Server Module",
            blocks: [
                {
                    opcode: "sendHeartbeat",
                    blockType: "command",
                    text: "Send heartbeat for player [PLAYER_ID] in room [ROOM_ID]",
                    arguments: {
                        PLAYER_ID: { type: "string", defaultValue: "player1" },
                        ROOM_ID: { type: "string", defaultValue: "room1" }
                    }
                },
                {
                    opcode: "createPlayer",
                    blockType: "command",
                    text: "Create player file for player [PLAYER_ID] in room [ROOM_ID]",
                    arguments: {
                        PLAYER_ID: { type: "string", defaultValue: "player1" },
                        ROOM_ID: { type: "string", defaultValue: "room1" }
                    }
                },
                {
                    opcode: "getPlayerData",
                    blockType: "reporter",
                    text: "Get player data for player [PLAYER_ID] in room [ROOM_ID]",
                    arguments: {
                        PLAYER_ID: { type: "string", defaultValue: "player1" },
                        ROOM_ID: { type: "string", defaultValue: "room1" }
                    }
                },
                {
                    opcode: "setPlayerData",
                    blockType: "command",
                    text: "Set player data for player [PLAYER_ID] in room [ROOM_ID] to [DATA]",
                    arguments: {
                        PLAYER_ID: { type: "string", defaultValue: "player1" },
                        ROOM_ID: { type: "string", defaultValue: "room1" },
                        DATA: { type: "string", defaultValue: "{}" }
                    }
                },
                {
                    opcode: "getConfig",
                    blockType: "reporter",
                    text: "Get server configuration",
                },
                {
                    opcode: "getIcon",
                    blockType: "reporter",
                    text: "Get server icon",
                },
                {
                    opcode: "downloadMap",
                    blockType: "reporter",
                    text: "Download map as data URI",
                },
                {
                    opcode: "createRoom",
                    blockType: "command",
                    text: "Create room [ROOM_ID]",
                    arguments: {
                        ROOM_ID: { type: "string", defaultValue: "room1" }
                    }
                }
            ]
        };
    }

    sendMessage(event, payload) {
        return new Promise((resolve) => {
            this.pendingRequests[event] = resolve;
            this.socket.send(JSON.stringify({ event, payload }));
        });
    }

    sendHeartbeat({ PLAYER_ID, ROOM_ID }) {
        this.sendMessage("heartbeat", { player_id: PLAYER_ID, room_id: ROOM_ID });
    }

    createPlayer({ PLAYER_ID, ROOM_ID }) {
        this.sendMessage("create_player", { player_id: PLAYER_ID, room_id: ROOM_ID });
    }

    getPlayerData({ PLAYER_ID, ROOM_ID }) {
        return this.sendMessage("get_player", { player_id: PLAYER_ID, room_id: ROOM_ID })
            .then(data => JSON.stringify(data));
    }

    setPlayerData({ PLAYER_ID, ROOM_ID, DATA }) {
        this.sendMessage("set_player_data", {
            player_id: PLAYER_ID,
            room_id: ROOM_ID,
            data: JSON.parse(DATA)
        });
    }

    async getConfig() {
        const response = await fetch(`${this.baseUrl}/config.json`);
        return response.json().then(data => JSON.stringify(data));
    }

    async getIcon() {
        const response = await fetch(`${this.baseUrl}/icon.svg`);
        if (!response.ok) throw new Error("Failed to fetch icon");
        const blob = await response.blob();
        return new Promise(resolve => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.readAsDataURL(blob);
        });
    }

    async downloadMap() {
        const response = await fetch(`${this.baseUrl}/map.zip`);
        if (!response.ok) throw new Error("Failed to fetch map");
        const blob = await response.blob();
        return new Promise(resolve => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.readAsDataURL(blob);
        });
    }

    createRoom({ ROOM_ID }) {
        fetch(`${this.baseUrl}/room/create`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ room_id: ROOM_ID })
        });
    }
}

Scratch.extensions.register(new ServerExtension());