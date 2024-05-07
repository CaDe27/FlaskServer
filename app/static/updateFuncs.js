async function endDateAfterStartDate() {
    // Set the minimum value (min attribute) of the endDate to the selected start date
    const startDateValue = document.getElementById('startDate').value;
    let endDateElem = document.getElementById('endDate');

    if(endDateElem.value < startDateValue){
        endDateElem.value = startDateValue;
    }
    // we only check for equality because it was smaller, the value is still
    // now equal because of the previous if
    if(endDateElem.value == startDateValue){
        await endHourAfterStartHour();
        await endMinuteAfterStartMinute();
    }
}

async function startDateBeforeEndDate() {
    // Set the minimum value (min attribute) of the endDate to the selected start date
    let startDateElem = document.getElementById('startDate');
    const endDateValue = document.getElementById('endDate').value;
    if(startDateElem.value >= endDateValue){
        startDateElem.value = endDateValue;
        await startHourBeforeEndHour();
        await startMinuteBeforeEndMinute();
    }
}

async function startHourBeforeEndHour() {
    const startDateValue = document.getElementById('startDate').value;
    const endDateValue = document.getElementById('endDate').value;
    if(startDateValue != endDateValue)
        return;

    let startHourElem = document.getElementById('startHourSelect');
    const endHourValue = document.getElementById('endHourSelect').value;
    if(startHourElem.value >= endHourValue){
        startHourElem.value = endHourValue;
        await startMinuteBeforeEndMinute();
    }
}

async function endHourAfterStartHour() {
    const startDateValue = document.getElementById('startDate').value;
    const endDateValue = document.getElementById('endDate').value;
    if(startDateValue != endDateValue)
        return;

    let endHourElem = document.getElementById('endHourSelect');
    const startHourValue = document.getElementById('startHourSelect').value;
    if(endHourElem.value <= startHourValue){
         endHourElem.value = startHourValue;
         await endMinuteAfterStartMinute();
    }
}

async function startMinuteBeforeEndMinute() {
    const startDateValue = document.getElementById('startDate').value;
    const endDateValue = document.getElementById('endDate').value;
    if(startDateValue != endDateValue)
        return;

    const endHourValue = document.getElementById('endHourSelect').value;
    const startHourValue = document.getElementById('startHourSelect').value;
    if(endHourValue != startHourValue)
        return;

    let startMinuteElem = document.getElementById('startMinuteSelect');
    const endMinuteValue = document.getElementById('endMinuteSelect').value;
    if(startMinuteElem.value > endMinuteValue){
         startMinuteElem.value = endMinuteValue;
    }
}

async function endMinuteAfterStartMinute() {
    const startDateValue = document.getElementById('startDate').value;
    const endDateValue= document.getElementById('endDate').value;
    if(startDateValue != endDateValue)
        return;

    const endHourValue = document.getElementById('endHourSelect').value;
    const startHourValue = document.getElementById('startHourSelect').value;
    if(endHourValue != startHourValue)
        return;

    let endMinuteElem = document.getElementById('endMinuteSelect');
    const startMinuteValue = document.getElementById('startMinuteSelect').value;
    if(endMinuteElem.value < startMinuteValue){
         endMinuteElem.value = startMinuteValue;
    }
}

async function changeTimeEventListener(){
    const padWithZero = (value) => String(value).padStart(2, '0');
    const startDate = document.getElementById('startDate').value;
    const startHour = padWithZero(document.getElementById('startHourSelect').value);
    const startMinute = padWithZero(document.getElementById('startMinuteSelect').value);

    const endDate = document.getElementById('endDate').value;
    const endHour = padWithZero(document.getElementById('endHourSelect').value);
    const endMinute = padWithZero(document.getElementById('endMinuteSelect').value);

    const startTime = startDate + 'T' + startHour + ':' + startMinute + ':00';
    const endTime = endDate + 'T' + endHour + ':' + endMinute + ':59';

    return fetch('/get_graph_new_datetime', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // send data as JSON
        body: JSON.stringify({startTime, endTime}) 
    })
    .then(response => response.json())
    .then(data => {
        cy.elements().remove();
        cy.add(data.elements);  // update main visualization with new elements
        runBreadthFirstLayout();
    });
}

function augmentOneMinute(dateElem, hourElem, minuteElem) {
    // Get the current date, hour, and minute from the elements
    const [year, month, day] = dateElem.value.split('-').map(Number);
    const currentHour = parseInt(hourElem.value, 10);
    const currentMinute = parseInt(minuteElem.value, 10);
    const currentDate = new Date(year, month - 1, day, currentHour, currentMinute);
    // Add one minute
    currentDate.setMinutes(currentDate.getMinutes() + 1);
    // Update the elements with the new values
    const newHour = currentDate.getHours();
    const newMinute = currentDate.getMinutes();
    
    // when you use toISOString(), it changes to utc time. We are on UTC-6,
    // so to show the local date we substract the hours UTC is going to add
    const offsetDate = new Date(currentDate.getTime() - (6 * 60 * 60 * 1000))
    dateElem.value = offsetDate.toISOString().split('T')[0];
    hourElem.value = newHour.toString().padStart(2, '0');
    minuteElem.value = newMinute.toString().padStart(2, '0');
}

async function updateTimeIfNewMinute() {
    const currentMinute = new Date().getMinutes();
    let lastRequestMinute = parseInt(document.getElementById('endMinuteSelect').value, 10);
    if (currentMinute !== lastRequestMinute) {
        augmentOneMinute(document.getElementById('startDate'),
                         document.getElementById('startHourSelect'),
                         document.getElementById('startMinuteSelect')
                        );
        augmentOneMinute(document.getElementById('endDate'),
                        document.getElementById('endHourSelect'),
                        document.getElementById('endMinuteSelect')
                       );
        await changeTimeEventListener();
    }
}

async function changeLowerThresholdListener(){
    const newThreshold = document.getElementById('lowerThreshold').value;
    return fetch('/get_graph_new_lower_edge_threshold', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // send data as JSON
        body: JSON.stringify({newThreshold}) 
    })
    .then(response => response.json())
    .then(data => {
        cy.elements().remove();
        cy.add(data.elements);  // update main visualization with new elements
        runBreadthFirstLayout();
    });
}

async function changeUpperThresholdListener(){
    const newThreshold = document.getElementById('upperThreshold').value;
    return fetch('/get_graph_new_upper_edge_threshold', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // send data as JSON
        body: JSON.stringify({newThreshold}) 
    })
    .then(response => response.json())
    .then(data => {
        cy.elements().remove();
        cy.add(data.elements);  // update main visualization with new elements
        runBreadthFirstLayout();
    });
}

async function changeNoThresholdListener(){
    const noLimit = document.getElementById('noLimitCheckbox').checked;
    return fetch('/get_graph_change_no_threshold_flag', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // send data as JSON
        body: JSON.stringify({noLimit}) 
    })
    .then(response => response.json())
    .then(data => {
        cy.elements().remove();
        cy.add(data.elements);  // update main visualization with new elements
        runBreadthFirstLayout();
    });
}

async function changeInDepthEventListener(){
    const new_depth_limit = document.getElementById('inDepthLimit').value;
    return fetch('/get_graph_new_in_depth_limit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // send data as JSON
        body: JSON.stringify({new_depth_limit}) 
    })
    .then(response => response.json())
    .then(data => {
        cy.elements().remove();
        cy.add(data.elements);  // update main visualization with new elements
        runBreadthFirstLayout();
    });
}

async function changeOutDepthEventListener(){
    const new_depth_limit = document.getElementById('outDepthLimit').value;
    return fetch('/get_graph_new_out_depth_limit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // send data as JSON
        body: JSON.stringify({new_depth_limit}) 
    })
    .then(response => response.json())
    .then(data => {
        cy.elements().remove();
        cy.add(data.elements);  // update main visualization with new elements
        runBreadthFirstLayout();
    });
}

async function changeServiceSelectorEventListener(){
    const newService = document.getElementById('serviceSelector').value;
    return fetch('/get_graph_new_selected_service', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // send data as JSON
        body: JSON.stringify({newService}) 
    })
    .then(response => response.json())
    .then(data => {
        cy.elements().remove();
        cy.add(data.elements);  // update main visualization with new elements
        runBreadthFirstLayout();
    });
}

async function completeGraphCheckboxEventListener(){
    const checkbox = document.getElementById('completeGraphCheckbox');
    const showCompleteGraph = checkbox.checked? "True" : "False";
    
    return fetch('/update_complete_graph_checkbox', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // send data as JSON
        body: JSON.stringify({showCompleteGraph}) 
    })
    .then(response => response.json())
    .then(data => {
        cy.elements().remove();
        cy.add(data.elements);  // update main visualization with new elements
        runBreadthFirstLayout();
    });
}

function getEliminatedServices(){
    const eliminatedServicesSelect = document.getElementById('eliminatedServices');
    const options = eliminatedServicesSelect.querySelectorAll('option');
    const selectedValues = Array.from(options)
                                .filter(option => option.selected)
                                .map(option => option.value);

    return selectedValues;
}

async function filteredServicesEventListener(){
    const eliminatedServices = getEliminatedServices();
    return fetch('/updated_eliminated_services', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({eliminatedServices}) 
    })
    .then(response => response.json())
    .then(data => {
        cy.elements().remove();
        cy.add(data.elements);  // update main visualization with new elements
        runBreadthFirstLayout();
    });
}

function getCheckboxLabelValue(checkboxId) {
    const checkbox = document.getElementById(checkboxId);
    let labelValue = null;
    if (checkbox) {
        // Get the next sibling element, which is the label in this case
        let label = checkbox.nextElementSibling;
        if (label) {
            labelValue = label.innerText || label.textContent;
        } else {
            console.error("Label not found for checkbox with ID: " + checkboxId);
        }
    } else {
        console.error("Checkbox not found with ID: " + checkboxId);
    }
    return labelValue;
}

async function aggregationSelectorEventListener(){
    const aggretationType = this.value;
    return fetch('/update_aggregation_type', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({aggretationType}) 
    })
    .then(response => response.json())
    .then(data => {
        cy.elements().remove();
        cy.add(data.elements);  // update main visualization with new elements
        runBreadthFirstLayout();
    });
}

function onStatusCodeCheckboxChange(checkboxId) {
    const checkbox = document.getElementById(checkboxId);
    const isChecked = checkbox.checked;
    const statusCode =  getCheckboxLabelValue(checkboxId);
    return fetch('/get_graph_update_status_code', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // send data as JSON
        body: JSON.stringify({statusCode, isChecked}) 
    })
    .then(response => response.json())
    .then(data => {
        cy.elements().remove();
        cy.add(data.elements);  // update main visualization with new elements
        runBreadthFirstLayout();
    });
    
}

function onMergeCheckboxChange() {
    const checkbox = document.getElementById('mergeStatusCodesCheckbox');
    const isChecked = checkbox.checked;
    return fetch('/get_graph_update_merge_status_codes_checkbox', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // send data as JSON
        body: JSON.stringify({isChecked}) 
    })
    .then(response => response.json())
    .then(data => {
        cy.elements().remove();
        cy.add(data.elements);  // update main visualization with new elements
        runBreadthFirstLayout();
    });
}

async function runAlgorithmEventListener() {
    const selectedAlgorithm = document.getElementById('algorithmSelector').value;
    document.getElementById("algorithmTitle").textContent = selectedAlgorithm + " results"
    const response = await fetch('/run_algorithm', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ algorithm: selectedAlgorithm }) 
    })
    .then(response => response.json())
    .then(
        data =>{
            algorithmResults = document.getElementById('algorithmResults');
            algorithmResults.textContent = data.results;
            console.log(data.results)
        }
    );
}

