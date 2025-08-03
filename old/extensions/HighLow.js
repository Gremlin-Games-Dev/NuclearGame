(function (Scratch) {
    'use strict';

    class MinMaxExtension {
        getInfo() {
            return {
                id: 'minmaxextension',
                name: 'MinMax Extension',
                blocks: [
                    {
                        opcode: 'getMax',
                        blockType: Scratch.BlockType.REPORTER,
                        text: 'highest number in [LIST]',
                        arguments: {
                            LIST: {
                                type: Scratch.ArgumentType.STRING,
                                defaultValue: '1,2,3'
                            }
                        }
                    },
                    {
                        opcode: 'getMin',
                        blockType: Scratch.BlockType.REPORTER,
                        text: 'lowest number in [LIST]',
                        arguments: {
                            LIST: {
                                type: Scratch.ArgumentType.STRING,
                                defaultValue: '1,2,3'
                            }
                        }
                    }
                ]
            };
        }

        // Function to get the highest number in a list
        getMax(args) {
            const numbers = this.parseNumbers(args.LIST);
            if (numbers.length === 0) return '';
            return Math.max(...numbers);
        }

        // Function to get the lowest number in a list
        getMin(args) {
            const numbers = this.parseNumbers(args.LIST);
            if (numbers.length === 0) return '';
            return Math.min(...numbers);
        }

        // Helper function to parse a list of numbers from a string
        parseNumbers(listString) {
            return listString
                .split(',')
                .map(item => parseFloat(item.trim()))
                .filter(num => !isNaN(num));
        }
    }

    Scratch.extensions.register(new MinMaxExtension());
})(Scratch);