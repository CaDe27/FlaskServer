// Function to generate options for a dropdown based on a range and optionally zero-pads numbers
function generateOptions(selectElement, start, end, zeroPad = false) {
    for (let i = start; i <= end; i++) {
        const option = document.createElement('option');
        const optionText = zeroPad ? String(i).padStart(2, '0') : i;
        option.value = optionText;
        option.textContent = optionText;
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