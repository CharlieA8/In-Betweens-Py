document.addEventListener('DOMContentLoaded', function() {
    const steps = document.querySelectorAll('.step');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    let currentStep = 0;
    
    function updateStepVisibility() {
        steps.forEach((step, index) => {
            if (index === currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
        
        prevBtn.disabled = currentStep === 0;
        nextBtn.textContent = currentStep === steps.length - 1 ? "Got it!" : "Next";
    }
    
    prevBtn.addEventListener('click', function() {
        if (currentStep > 0) {
            currentStep--;
            updateStepVisibility();
        }
    });
    
    nextBtn.addEventListener('click', function() {
        if (currentStep < steps.length - 1) {
            currentStep++;
            updateStepVisibility();
        } else {
            window.location.href = '/';
        }
    });
    
    // Initial setup
    updateStepVisibility();
});