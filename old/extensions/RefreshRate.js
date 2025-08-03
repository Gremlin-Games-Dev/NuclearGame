(function (Scratch) {
    'use strict';

    class RefreshRateExtension {
        getInfo() {
            return {
                id: 'refreshrateextension',
                name: 'Refresh Rate Extension',
                blocks: [
                    {
                        opcode: 'getRefreshRate',
                        blockType: Scratch.BlockType.REPORTER,
                        text: 'get refresh rate',
                    }
                ]
            };
        }

        constructor() {
            this.lastTime = 0;
            this.frameTime = 0;
            this.refreshRate = 0;
        }

        // Function to estimate the refresh rate
        getRefreshRate() {
            const currentTime = performance.now();
            this.frameTime = currentTime - this.lastTime;
            this.lastTime = currentTime;

            // Estimate the refresh rate (in Hz)
            this.refreshRate = 1000 / this.frameTime;
            
            return Math.round(this.refreshRate);
        }
    }

    Scratch.extensions.register(new RefreshRateExtension());
})(Scratch);