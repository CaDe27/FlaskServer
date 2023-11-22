// Function to generate options for a dropdown based on a range and optionally zero-pads numbers
function generateOptions(selectElement, start, end, zeroPad = false) {
    for (let i = start; i <= end; i++) {
        const option = document.createElement('option');
        option.value = i;
        // Use padStart to add a leading zero for numbers less than 10
        option.textContent = zeroPad ? String(i).padStart(2, '0') : i; 
        selectElement.appendChild(option);
    }
}

function fillServiceSelectorOptions(selectElement, serviceNames) {
    const currentSelectedValue = selectElement.value;
    serviceNames.forEach(item => {
        if (item !== currentSelectedValue) {
            const option = document.createElement('option');
            option.value = item;
            option.textContent = item;
            selectElement.appendChild(option);
        }
    });
}