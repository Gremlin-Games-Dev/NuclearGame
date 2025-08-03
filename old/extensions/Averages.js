(function (Scratch) {
    'use strict';

    class AverageExtension {
        getInfo() {
            return {
                id: 'averageextension',
                name: 'Average Extension',
                blocks: [
                    {
                        opcode: 'getAverage',
                        blockType: Scratch.BlockType.REPORTER,
                        text: 'average of [LIST]',
                        arguments: {
                            LIST: {
                                type: Scratch.ArgumentType.STRING,
                                defaultValue: '1,2,3'
                            }
                        }
                    },
                    {
                        opcode: 'getAverageWithoutOutliers',
                        blockType: Scratch.BlockType.REPORTER,
                        text: 'average without outliers in [LIST]',
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

        // Function to calculate the average of a list
        getAverage(args) {
            const numbers = this.parseNumbers(args.LIST);
            if (numbers.length === 0) return '';
            const sum = numbers.reduce((a, b) => a + b, 0);
            return sum / numbers.length;
        }

        // Function to calculate the average without outliers
        getAverageWithoutOutliers(args) {
            const numbers = this.parseNumbers(args.LIST);
            if (numbers.length === 0) return '';

            // Sort numbers to calculate IQR
            const sorted = [...numbers].sort((a, b) => a - b);
            const q1 = this.getQuantile(sorted, 0.25); // First quartile
            const q3 = this.getQuantile(sorted, 0.75); // Third quartile
            const iqr = q3 - q1; // Interquartile range

            // Define outlier boundaries
            const lowerBound = q1 - 1.5 * iqr;
            const upperBound = q3 + 1.5 * iqr;

            // Filter out outliers
            const filtered = numbers.filter(num => num >= lowerBound && num <= upperBound);

            if (filtered.length === 0) return ''; // Avoid division by zero
            const sum = filtered.reduce((a, b) => a + b, 0);
            return sum / filtered.length;
        }

        // Helper function to parse a list of numbers from a string
        parseNumbers(listString) {
            return listString
                .split(',')
                .map(item => parseFloat(item.trim()))
                .filter(num => !isNaN(num));
        }

        // Helper function to calculate quantiles
        getQuantile(sortedNumbers, quantile) {
            const pos = (sortedNumbers.length - 1) * quantile;
            const base = Math.floor(pos);
            const rest = pos - base;
            if (sortedNumbers[base + 1] !== undefined) {
                return sortedNumbers[base] + rest * (sortedNumbers[base + 1] - sortedNumbers[base]);
            } else {
                return sortedNumbers[base];
            }
        }
    }

    Scratch.extensions.register(new AverageExtension());
})(Scratch);