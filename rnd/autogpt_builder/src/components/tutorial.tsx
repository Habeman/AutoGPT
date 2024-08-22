import Shepherd from 'shepherd.js';
import 'shepherd.js/dist/css/shepherd.css';

export const startTutorial = (setPinBlocks: (value: boolean) => void) => {
    const tour = new Shepherd.Tour({
        useModalOverlay: true,
        defaultStepOptions: {
            cancelIcon: { enabled: true },
            scrollTo: { behavior: 'smooth', block: 'center' },
        },
    });

    // CSS classes for disabling and highlighting blocks
    const disableClass = 'disable-blocks';
    const highlightClass = 'highlight-block';
    let isConnecting = false;

    // Helper function to disable all blocks except the target block
    const disableOtherBlocks = (targetBlockSelector: string) => {
        document.querySelectorAll('[data-id^="add-block-button"]').forEach((block) => {
            block.classList.toggle(disableClass, !block.matches(targetBlockSelector));
            block.classList.toggle(highlightClass, block.matches(targetBlockSelector));
        });
    };

    // Helper function to enable all blocks
    const enableAllBlocks = () => {
        document.querySelectorAll('[data-id^="add-block-button"]').forEach((block) => {
            block.classList.remove(disableClass, highlightClass);
        });
    };

    // Inject CSS for disabling and highlighting blocks
    const injectStyles = () => {
        const style = document.createElement('style');
        style.textContent = `
            .${disableClass} {
                pointer-events: none;
                opacity: 0.5;
            }
            .${highlightClass} {
                background-color: #ffeb3b;
                border: 2px solid #fbc02d;
                transition: background-color 0.3s, border-color 0.3s;
            }
        `;
        document.head.appendChild(style);
    };

    // Helper function to check if an element is present in the DOM
    const waitForElement = (selector: string): Promise<void> => {
        return new Promise((resolve) => {
            const checkElement = () => {
                if (document.querySelector(selector)) {
                    resolve();
                } else {
                    setTimeout(checkElement, 10);
                }
            };
            checkElement();
        });
    };

    // Function to detect the correct connection and advance the tour
    const detectConnection = () => {
        const checkForConnection = () => {
            const correctConnection = document.querySelector('[data-testid="rf__edge-1_result_2_a"]');
            if (correctConnection) {
                tour.show('press-run-again');
            } else {
                setTimeout(checkForConnection, 100);
            }
        };

        checkForConnection();
    };

    // Define state management functions to handle connection state
    function startConnecting() {
        isConnecting = true;
    }

    function stopConnecting() {
        isConnecting = false;
    }

    // Reset connection state when revisiting the step
    function resetConnectionState() {
        stopConnecting();
    }

    // Event handlers for mouse down and up to manage connection state
    function handleMouseDown() {
        startConnecting();
        setTimeout(() => {
            if (isConnecting) {
                tour.next();
            }
        }, 100);
    }
    // Event handler for mouse up to check if the connection was successful
    function handleMouseUp(event: { target: any; }) {
        const target = event.target;
        const validConnectionPoint = document.querySelector('[data-id="2-a-target"]');
    
        if (validConnectionPoint && !validConnectionPoint.contains(target)) {
            setTimeout(() => {
                if (!document.querySelector('[data-testid="rf__edge-1_result_2_a"]')) {
                    stopConnecting();
                    tour.show('connect-blocks-output');
                }
            }, 200);
        } else {
            stopConnecting();
        }
    }

    injectStyles();

    tour.addStep({
        id: 'starting-step',
        title: 'Welcome to the Tutorial',
        text: 'This is the AutoGPT builder!',
        buttons: [
            {
                text: 'Next',
                action: tour.next,
            },
        ],
    });

    tour.addStep({
        id: 'open-block-step',
        title: 'Open Blocks Menu',
        text: 'Please click the block button to open the blocks menu.',
        attachTo: { element: '[data-id="blocks-control-popover-trigger"]', on: 'bottom' },
        advanceOn: { selector: '[data-id="blocks-control-popover-trigger"]', event: 'click' },
        buttons: [],
    });

    tour.addStep({
        id: 'scroll-block-menu',
        title: 'Scroll Down or Search',
        text: 'Scroll down or search in the blocks menu for the "Math Block" and press the "+" to add the block.',
        attachTo: { element: '[data-id="blocks-control-popover-content"]', on: 'bottom' },
        buttons: [],
        beforeShowPromise: () => waitForElement('[data-id="blocks-control-popover-content"]').then(() => {
            disableOtherBlocks('[data-id="add-block-button-b1ab9b19-67a6-406d-abf5-2dba76d00c79"]');
        }),
        advanceOn: {
            selector: '[data-id="add-block-button-b1ab9b19-67a6-406d-abf5-2dba76d00c79"]',
            event: 'click',
        },
        when: {
            show: () => setPinBlocks(true),
            hide: enableAllBlocks,
        },
    });

    tour.addStep({
        id: 'focus-new-block',
        title: 'New Block',
        text: 'This is a Math Block. Let’s go over how it works.',
        attachTo: { element: `[data-id="custom-node-1"]`, on: 'top' },
        beforeShowPromise: () => waitForElement('[data-id="custom-node-1"]'),
        buttons: [
            {
                text: 'Next',
                action: tour.next,
            },
        ],
        when: {
            show: () => setPinBlocks(false),
        },
    });

    tour.addStep({
        id: 'input-to-block',
        title: 'Input to the Block',
        text: 'This is the input pin for the block. You can input the output of other blocks here; this block takes numbers as input.',
        attachTo: { element: '[data-nodeid="1"]', on: 'left' },
        buttons: [
            {
                text: 'Back',
                action: tour.back,
            },
            {
                text: 'Next',
                action: tour.next,
            },
        ],
    });

    tour.addStep({
        id: 'output-from-block',
        title: 'Output from the Block',
        text: 'This is the output pin for the block. You can connect this to another block to pass the output along.',
        attachTo: { element: '[data-handlepos="right"]', on: 'right' },
        buttons: [
            {
                text: 'Back',
                action: tour.back,
            },
            {
                text: 'Next',
                action: tour.next,
            },
        ],
    });

    tour.addStep({
        id: 'select-operation',
        title: 'Select Operation',
        text: 'Select a mathematical operation to perform. Let’s choose "Add" for now.',
        attachTo: { element: '.mt-1.mb-2', on: 'right' },
        buttons: [
            {
                text: 'Back',
                action: tour.back,
            },
            {
                text: 'Next',
                action: tour.next,
            },
        ],
        when: {
            show: () => tour.modal.hide(),
            hide: () => tour.modal.show(),
        },
    });

    tour.addStep({
        id: 'enter-number-1',
        title: 'Enter a Number',
        text: 'Enter a number here to try the Math Block!',
        attachTo: { element: '#a', on: 'right' },
        buttons: [
            {
                text: 'Back',
                action: tour.back,
            },
            {
                text: 'Next',
                action: tour.next,
            },
        ],
    });

    tour.addStep({
        id: 'enter-number-2',
        title: 'Enter Another Number',
        text: 'Enter another number here!',
        attachTo: { element: '#b', on: 'right' },
        buttons: [
            {
                text: 'Back',
                action: tour.back,
            },
            {
                text: 'Next',
                action: tour.next,
            },
        ],
    });

    tour.addStep({
        id: 'press-run',
        title: 'Press Run',
        text: 'Start your first flow by pressing the Run button!',
        attachTo: { element: '[data-id="control-button-2"]', on: 'right' },
        advanceOn: { selector: '[data-id="control-button-2"]', event: 'click' },
        buttons: [
            {
                text: 'Back',
                action: tour.back,
            },
        ],
    });

    tour.addStep({
        id: 'check-output',
        title: 'Check the Output',
        text: 'Check here to see the output of the block after running the flow.',
        attachTo: { element: '.node-output', on: 'bottom' },
        beforeShowPromise: () => waitForElement('.node-output'),
        buttons: [
            {
                text: 'Back',
                action: tour.back,
            },
            {
                text: 'Next',
                action: tour.next,
            },
        ],
    });

    tour.addStep({
        id: 'copy-paste-block',
        title: 'Copy and Paste the Block',
        text: 'Let’s duplicate this block. Click and hold the block with your mouse, then press Ctrl+C to copy and Ctrl+V to paste.',
        attachTo: { element: `[data-id="custom-node-1"]`, on: 'top' },
        buttons: [
            {
                text: 'Back',
                action: tour.back,
            },
        ],
        when: {
            show: () => document.addEventListener('keydown', handleCtrlV),
            hide: () => document.removeEventListener('keydown', handleCtrlV),
        },
    });

    const handleCtrlV = (event: KeyboardEvent) => {
        if (event.ctrlKey && event.key === 'v') {
            tour.next();
        }
    };

    tour.addStep({
        id: 'focus-second-block',
        title: 'Focus on the New Block',
        text: 'This is your copied Math Block. Now, let’s move it to the side of the first block.',
        attachTo: { element: `[data-id="custom-node-2"]`, on: 'top' },
        beforeShowPromise: () => waitForElement('[data-id="custom-node-2"]'),
        buttons: [
            {
                text: 'Next',
                action: tour.next,
            },
        ],
    });

    tour.addStep({
        id: 'connect-blocks-output',
        title: 'Connect the Blocks: Output',
        text: 'Now, let’s connect the output of the first Math Block to the input of the second Math Block. Drag from the output pin of the first block to the input pin (A) of the second block.',
        attachTo: { element: '[data-id="1-result-source"]', on: 'bottom' },
        buttons: [
            {
                text: 'Back',
                action: tour.back,
            },
        ],
        beforeShowPromise: () => {
            return waitForElement('[data-id="1-result-source"]');
        },
        when: {
            show: () => {
                resetConnectionState();  // Reset state when revisiting this step
                tour.modal.show();
                const outputPin = document.querySelector('[data-id="1-result-source"]');
                if (outputPin) {
                    outputPin.addEventListener('mousedown', handleMouseDown);
                }
            },
            hide: () => {
                const outputPin = document.querySelector('[data-id="1-result-source"]');
                if (outputPin) {
                    outputPin.removeEventListener('mousedown', handleMouseDown);
                }
            },
        },
    });
    
    tour.addStep({
        id: 'connect-blocks-input',
        title: 'Connect the Blocks: Input',
        text: 'Now, connect the output to the input pin of the second block (A).',
        attachTo: { element: '[data-id="2-a-target"]', on: 'top' },
        buttons: [],
        beforeShowPromise: () => {
            return waitForElement('[data-id="2-a-target"]').then(() => {
                detectConnection();
            });
        },
        when: {
            show: () => {
                tour.modal.show();
                document.addEventListener('mouseup', handleMouseUp, true);
            },
            hide: () => {
                tour.modal.hide();
                document.removeEventListener('mouseup', handleMouseUp, true);
            },
        },
    });

    tour.addStep({
        id: 'press-run-again',
        title: 'Press Run Again',
        text: 'Now, press the Run button again to execute the flow with the new Math Block added!',
        attachTo: { element: '[data-id="control-button-2"]', on: 'right' },
        advanceOn: { selector: '[data-id="control-button-2"]', event: 'click' },
        buttons: [],
    });

    tour.addStep({
        id: 'congratulations',
        title: 'Congratulations!',
        text: 'You have successfully created your first flow. Watch for the outputs in the blocks!',
        beforeShowPromise: () => waitForElement('.node-output'),
        when: {
            show: () => tour.modal.hide(),
        },
        buttons: [
            {
                text: 'Finish',
                action: tour.complete,
            },
        ],
    });

    // Unpin blocks when the tour is completed or canceled
    tour.on('complete', () => {
        setPinBlocks(false);
        localStorage.setItem('shepherd-tour', 'completed'); // Optionally mark the tutorial as completed
      });
    
      tour.on('cancel', () => {
        setPinBlocks(false);
        localStorage.setItem('shepherd-tour', 'canceled'); // Optionally mark the tutorial as canceled
      });
    tour.start();
};
