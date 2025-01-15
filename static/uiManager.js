class UIManager {
    constructor() {
        this.currentStep = 0;
        this.progressSteps = ['Extract', 'Analyze', 'Integrate', 'Track'];
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        document.getElementById('jobForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.startJobParsing();
        });

        document.getElementById('menuToggle').addEventListener('click', () => {
            const menu = document.getElementById('floatingMenu');
            menu.classList.toggle('hidden');
        });
    }

    updateProgress(step) {
        this.currentStep = step;
        this.updateProgressUI();
    }

    updateProgressUI() {
        const steps = document.querySelectorAll('.progress-step');
        steps.forEach((step, index) => {
            step.classList.remove('active');
            if (index < this.currentStep) {
                step.classList.add('active');
            }
        });
    }

    async startJobParsing() {
        this.updateProgress(1); // Start with Extract Job Data
        try {
            const formData = new FormData(document.getElementById('jobForm'));
            // Simulate parsing delay
            await new Promise(resolve => setTimeout(resolve, 1000));
            this.updateProgress(2); // Move to AI Analysis
            // Simulate AI analysis delay
            await new Promise(resolve => setTimeout(resolve, 1000));
            this.updateProgress(3); // Move to Notion Integration
            // Simulate Notion integration delay
            await new Promise(resolve => setTimeout(resolve, 1000));
            this.updateProgress(4); // Move to Application Tracking
        } catch (error) {
            console.error('Parsing failed:', error);
            // Show error UI
        }
    }
}

const uiManager = new UIManager(); 