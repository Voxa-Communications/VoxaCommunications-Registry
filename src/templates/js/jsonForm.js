export class JsonForm { 
    constructor(elementID) {
        this.elementID = elementID;
        this.form = document.getElementById(elementID);
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
    };
    
    async handleSubmit(event) {
        event.preventDefault();
        
        const buttonText = document.getElementById('buttonText');
        const spinner = document.getElementById('spinner');
        
        // Show spinner, hide button text
        buttonText.style.display = 'none';
        spinner.style.display = 'block';
        
        const formData = new FormData(this.form);
        const data = {};
        
        formData.forEach((value, key) => {
            data[key] = value;
        });
        
        try {
            console.log('Form data:', data);
            console.log('Form action:', this.form.action);
            console.log('Form method:', this.form.method);
            const response = await fetch(this.form.action, {
                method: this.form.method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                alert('Form submitted successfully!');
                this.form.reset();
            } else {
                const error = await response.json();
                alert(`Form submission failed: ${error.message || 'Unknown error'}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            // Hide spinner, show button text
            buttonText.style.display = 'inline';
            spinner.style.display = 'none';
        }
    }
}

// Bassed off of:
/*
document.getElementById('loginForm').addEventListener('submit', async function(event) {
            event.preventDefault();
            
            const buttonText = document.getElementById('buttonText');
            const spinner = document.getElementById('spinner');
            
            // Show spinner, hide button text
            buttonText.style.display = 'none';
            spinner.style.display = 'block';
            
            const formData = new FormData(this);
            const data = {
                email: formData.get('email'),
                password: formData.get('password')
            };
            
            try {
                const response = await fetch('/api/v1/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    alert('Login successful!');
                    this.reset();
                } else {
                    const error = await response.json();
                    alert(`Login failed: ${error.message || 'Unknown error'}`);
                }
            } catch (error) {
                alert(`Error: ${error.message}`);
            } finally {
                // Hide spinner, show button text
                buttonText.style.display = 'inline';
                spinner.style.display = 'none';
            }
        });
*/